<script setup lang="ts">
import type { Channel } from '~/types'
import { ref, onMounted } from 'vue'
import { useStore } from '~/store'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

import AttachmentInput from '~/components/common/AttachmentInput.vue'
import TagsSelector from '~/components/library/TagsSelector.vue'
import useErrorHandler from '~/composables/useErrorHandler'

const store = useStore()
const router = useRouter()
const { t } = useI18n()

const artistName = ref('')
const bio = ref('')
const tags = ref([] as Array<string>)

// Image preview states
const cover = ref<string | null>(null)
const avatar = ref<string | null>(null)
const isLoaded = ref(false)
const isSaving = ref(false)

// Save changes
const saveChanges = async () => {

  isSaving.value = true

  try {
    await axios.put(`channels/${store.state.auth.username}/`, {
      content_category: 'music',
      name: artistName.value,
      description: {
        content_type: 'text/markdown',
        text: bio.value
      },
      cover: cover.value,
      avatar: avatar.value,
      tags: tags.value
    })
  } catch (error) {
    useErrorHandler(error as Error)
  } finally {
    isSaving.value = false
  }
}

// Load initial data
const loadChannelData = async () => {
  try {
    const response = await axios.get(`channels/${store.state.auth.username}/`)
    const channel = response.data as Channel
    
    artistName.value = channel.artist.name

    bio.value = channel.artist.description.text
    tags.value = channel.artist.tags
    
    if (channel.artist?.cover?.uuid) {
      cover.value = channel.artist.cover.uuid
    }
    
    if (store.state.auth.profile.avatar) {
      avatar.value = store.state.auth.profile.avatar.uuid
    }

    isLoaded.value = true
    
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

onMounted(() => {
  if (!store.state.auth.authenticated) {
    router.push('/login')
    return
  }
  loadChannelData()
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-900 to-black p-6">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">My Channel</h1>
        <button
          @click="saveChanges"
          class="px-6 py-2 bg-white text-black rounded-lg hover:bg-gray-200 transition-colors"
          :disabled="isSaving"
        >
          {{ isSaving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>

      <!-- Banner and Profile Section -->
      <div v-if="isLoaded" class="relative text-white mb-6">
        <label class="block text-xl mb-2">Cover</label>
        <attachment-input
          v-model="cover"
          name="cover"
          imageClass="podcast">
        </attachment-input>

        <!-- Profile Image -->
        <label class="block text-xl mb-2">Avatar</label>
        <attachment-input
          v-model="avatar"
          name="avatar"
          imageClass="podcast">
        </attachment-input>
      </div>

      <!-- Artist Details Form -->
      <div class="space-y-6 max-w-2xl">
        <div>
          <label class="block text-xl mb-2">Your name</label>
          <input
            v-model="artistName"
            type="text"
            class="w-full bg-gray-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
            placeholder="Enter your name"
          />
        </div>

        <div class="ui field">
          <label for="channel-tags">
            {{ $t('components.audio.ChannelForm.label.tags') }}
          </label>
          <tags-selector
            id="channel-tags"
            v-model="tags"
            :required="false"
          />
        </div>
        <div>
          <label class="block text-xl mb-2">Description</label>
          <textarea
            v-model="bio"
            rows="4"
            class="w-full bg-gray-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
            placeholder="Tell us about yourself..."
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>