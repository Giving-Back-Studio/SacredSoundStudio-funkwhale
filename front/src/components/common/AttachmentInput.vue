<script setup lang="ts">
import type { BackendError } from '~/types'

import axios from 'axios'
import { useVModel } from '@vueuse/core'
import { reactive, ref, watch } from 'vue'
import { useStore } from '~/store'
import useFormData from '~/composables/useFormData'

interface Events {
  (e: 'update:modelValue', value: string | null): void
  (e: 'delete'): void
}

interface Props {
  modelValue: string | null
  imageClass?: string
  required?: boolean
  name?: string | undefined
  initialValue?: string | undefined
}

const emit = defineEmits<Events>()
const props = withDefaults(defineProps<Props>(), {
  imageClass: '',
  required: false,
  name: undefined,
  initialValue: undefined
})

const value = useVModel(props, 'modelValue', emit)

const attachment = ref()
const isLoading = ref(false)
const errors = reactive([] as string[])
const attachmentId = Math.random().toString(36).substring(7)

const input = ref()
const file = ref()
const submit = async () => {
  isLoading.value = true
  errors.length = 0
  file.value = input.value.files[0]

  const formData = useFormData({ file: file.value })

  try {
    const { data } = await axios.post('attachments/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    attachment.value = data
    value.value = data.uuid
  } catch (error) {
    if (error as BackendError) {
      const { backendErrors } = error as BackendError
      errors.push(...backendErrors)
    }
  } finally {
    isLoading.value = false
  }
}

const remove = async (uuid: string, sendEvent = true) => {
  isLoading.value = true
  errors.length = 0

  try {
    await axios.delete(`attachments/${uuid}/`)

    if (sendEvent) {
      attachment.value = null
      emit('delete')
    }
  } catch (error) {
    if (error as BackendError) {
      if (error.response.status !== 404) {
        // Already deleted, perhaps by manual removal
        const { backendErrors } = error as BackendError
        errors.push(...backendErrors)
      }
    }
  } finally {
    isLoading.value = false
  }
}

const initialValue = ref(props.initialValue ?? props.modelValue)
watch(value, (to, from) => {
  // NOTE: Remove old attachment if it's not the original one
  if (from !== initialValue.value && typeof from === 'string') {
    remove(from, false)
  }

  // NOTE: We want to bring back the original attachment, let's delete the current one
  if (attachment.value && to === initialValue.value) {
    remove(attachment.value.uuid)
  }
})

const store = useStore()
const getAttachmentUrl = (uuid: string) => {
  return store.getters['instance/absoluteUrl'](`api/v1/attachments/${uuid}/proxy?next=medium_square_crop`)
}
</script>

<template>
  <div class="ui form">
    <div
      v-if="errors.length > 0"
      role="alert"
      class="ui negative message"
    >
      <h4 class="header">
        {{ $t('components.common.AttachmentInput.header.failure') }}
      </h4>
      <ul class="list">
        <li
          v-for="(error, key) in errors"
          :key="key"
        >
          {{ error }}
        </li>
      </ul>
    </div>
    <div class="ui field">
      <span id="avatarLabel">
        <slot />
      </span>
      <div class="ui stackable grid row">
        <div class="three wide column">
          <img
            v-if="value && value === initialValue"
            alt=""
            :class="['ui', imageClass, 'image']"
            :src="getAttachmentUrl(value)"
          >
          <img
            v-else-if="attachment"
            alt=""
            :class="['ui', imageClass, 'image']"
            :src="getAttachmentUrl(attachment.uuid)"
          >
          <div
            v-else
            :class="['ui', imageClass, 'static', 'large placeholder image']"
          />
        </div>
        <div class="eleven wide column">
          <div class="file-input">
            <label :for="attachmentId">
              {{ $t('components.common.AttachmentInput.label.upload') }}
            </label>
            <input
              :id="attachmentId"
              ref="input"
              :name="name"
              :required="required || undefined"
              class="ui input"
              type="file"
              accept="image/png,image/jpeg"
              @change="submit"
            >
          </div>
          <div class="ui very small hidden divider" />
          <p>
            {{ $t('components.common.AttachmentInput.help.upload') }}
          </p>
          <button
            v-if="value"
            class="ui basic tiny button"
            @click.stop.prevent="remove(value as string)"
          >
            {{ $t('components.common.AttachmentInput.button.remove') }}
          </button>
          <div
            v-if="isLoading"
            class="ui active inverted dimmer"
          >
            <div class="ui indeterminate text loader">
              {{ $t('components.common.AttachmentInput.loader.uploading') }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
