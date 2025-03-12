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
const isLoaded = ref(false)
const isSaving = ref(false)

const channelUrl = `/channels/${store.state.auth.profile.actor_username}`

// Save changes
const saveChanges = async () => {

  isSaving.value = true

  try {
    await axios.put(channelUrl, {
      content_category: 'music',
      name: artistName.value,
      description: {
        content_type: 'text/markdown',
        text: bio.value
      },
      cover: cover.value,
      tags: tags.value
    })
  } catch (error) {
    useErrorHandler(error as Error)
  } finally {
    isSaving.value = false
    router.push(channelUrl)
  }
}

// Load initial data
const loadChannelData = async () => {
  try {
    const response = await axios.get(channelUrl)
    const channel = response.data as Channel
    
    artistName.value = channel.artist.name

    if (channel.artist.description) {
      bio.value = channel.artist.description.text
    }

    tags.value = channel.artist.tags
    
    if (channel.artist?.cover?.uuid) {
      cover.value = channel.artist.cover.uuid
    }

    isLoaded.value = true
    
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

onMounted(loadChannelData)
</script>

<template>
  <div class="main pusher">
    <div class="ui container">
      <div class="ui basic segment">
        <!-- Header -->
        <div class="ui clearing basic segment">
          <h1 class="ui left floated header">My Channel</h1>
          <button
            @click="saveChanges"
            :class="['ui', 'right', 'floated', 'primary', {loading: isSaving}, 'button']"
            :disabled="isSaving"
          >
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>

        <!-- Channel Form -->
        <div v-if="isLoaded" class="ui form">
          <!-- Cover Image -->
          <div class="ui field">
            <label>Cover</label>
            <attachment-input
              v-model="cover"
              name="cover"
              imageClass="channel-image large">
            </attachment-input>
          </div>

          <!-- Channel Name -->
          <div class="ui required field">
            <label>Channel Name</label>
            <input
              v-model="artistName"
              type="text"
              placeholder="Enter your name"
            />
          </div>

          <!-- Tags -->
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

          <!-- Description -->
          <div class="ui field">
            <label>Description (Supports Markdown)</label>
            <textarea
              v-model="bio"
              rows="4"
              placeholder="Tell us about yourself..."
            ></textarea>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
