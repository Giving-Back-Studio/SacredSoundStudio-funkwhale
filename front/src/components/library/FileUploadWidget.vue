<script setup lang="ts">
import type { VueUploadItem } from 'vue-upload-component'

import { useCookies } from '@vueuse/integrations/useCookies'
import { computed, ref, watch, getCurrentInstance } from 'vue'
import { useStore } from '~/store'
import axios from 'axios'

import FileUpload from 'vue-upload-component'

const { get } = useCookies()
const instance = getCurrentInstance()
const attrs = instance?.attrs ?? {}

const store = useStore()
const headers = computed(() => {
  const headers: Record<string, string> = typeof attrs.headers === 'object'
    ? { ...attrs.headers }
    : {}

  if (store.state.auth.oauth.accessToken) {
    headers.Authorization ??= store.getters['auth/header']
  }

  const csrf = get('csrftoken')
  if (csrf) headers['X-CSRFToken'] = csrf

  return headers
})

const patchFileData = (file: VueUploadItem, data: Record<string, unknown> = {}) => {
  let metadata = data.import_metadata as Record<string, unknown>

  // @ts-expect-error Taken from 3.1.2
  const filename: string = file.file.name || file.file.filename || file.name
  data.source = `upload://${filename}`

  if (metadata) {
    metadata = { ...metadata }
    if (data.channel && !metadata.title) {
      metadata.title = filename.replace(/\.[^/.]+$/, '')
    }

    data.import_metadata = JSON.stringify(metadata)
  }

  return data
}

const uploadAction = async (file: VueUploadItem, self: any): Promise<VueUploadItem> => {
  file.data = patchFileData(file, file.data)
  
  // Check if the file is large (over 100MB) and should use S3 direct upload
  // @ts-expect-error Taken from 3.1.2
  const fileSize = file.size || file.file?.size || 0
  const isLargeFile = fileSize > 100 * 1024 * 1024 // 100MB threshold
  
  if (isLargeFile) {
    try {
      // Get pre-signed URL from our API
      const response = await axios.post(
        store.getters['instance/absoluteUrl']('/api/v1/uploads/s3-presigned-url'),
        {
          filename: file.name,
          file_size: fileSize,
          content_type: file.type,
          library: file.data.library,
          channel: file.data.channel,
          import_status: file.data.import_status,
          import_metadata: file.data.import_metadata
        },
        { headers }
      )
      
      // Upload directly to S3 using the pre-signed URL
      const formData = new FormData()
      
      // Add all the fields from the presigned URL response
      Object.entries(response.data.fields).forEach(([key, value]) => {
        formData.append(key, value as string)
      })
      
      // Add the file as the last field
      formData.append('file', file.file)
      
      // Upload to S3
      await axios.post(response.data.presigned_url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (e) => {
          // Update progress
          file.progress = Math.round((e.loaded * 100) / (e.total || fileSize))
          self.update(file)
        }
      })
      
      // Update the file with the upload UUID from the response
      file.response = { uuid: response.data.upload_uuid }
      file.success = true
      file.error = false
      file.active = false
      
      return file
    } catch (error) {
      file.error = true
      file.success = false
      file.active = false
      console.error('S3 upload error:', error)
      return file
    }
  }
  
  // For smaller files, use the standard upload process
  if (self.features.html5) {
    if (self.shouldUseChunkUpload(file)) return self.uploadChunk(file)
    if (file.putAction) return self.uploadPut(file)
    if (file.postAction) return self.uploadHtml5(file)
  }

  if (file.postAction) return self.uploadHtml4(file)
  return Promise.reject(new Error('No action configured'))
}

// NOTE: We need to expose the data and methods that we use
const upload = ref()

const active = ref(false)
watch(active, () => (upload.value.active = active.value))

const update = (file: VueUploadItem, data: Partial<VueUploadItem>) => upload.value.update(file, data)
const remove = (file: VueUploadItem) => upload.value.remove(file)

defineExpose({
  active,
  update,
  remove
})
</script>

<script lang="ts">
// NOTE: We're disallowing overriding `custom-action` and `headers` props
export default { inheritAttrs: false }
</script>

<template>
  <file-upload
    ref="upload"
    v-bind="$attrs"
    :post-action="$store.getters['instance/absoluteUrl']('/api/v1/uploads/')"
    :multiple="true"
    :thread="1"
    :custom-action="uploadAction"
    :headers="headers"
    :extensions="$store.state.ui.supportedExtensions"
    :drop="true"
    name="audio_file"
  >
    <slot />
  </file-upload>
</template>
