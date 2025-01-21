<script setup lang="ts">
import type { Channel } from '~/types'
import { ref, reactive, onMounted } from 'vue'
import { useStore } from '~/store'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { 
  ImageIcon, 
  UserCircleIcon, 
  PlusIcon, 
  TrashIcon
} from 'lucide-vue-next'

import useErrorHandler from '~/composables/useErrorHandler'

const store = useStore()
const router = useRouter()

// Channel data state
const channelData = reactive({
  artistName: '',
  username: '',
  bio: '',
  email: '',
  links: [] as Array<{ title: string, url: string }>
})

// Image preview states
const bannerPreview = ref<string | null>(null)
const profilePreview = ref<string | null>(null)
const isSaving = ref(false)

// File input refs
const bannerInput = ref<HTMLInputElement | null>(null)
const profileInput = ref<HTMLInputElement | null>(null)

// Methods for banner image
const handleBannerDrop = (e: DragEvent) => {
  const file = e.dataTransfer?.files[0]
  if (file && file.type.startsWith('image/')) {
    handleBannerFile(file)
  }
}

const handleBannerSelect = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) handleBannerFile(file)
}

const handleBannerFile = (file: File) => {
  bannerPreview.value = URL.createObjectURL(file)
}

// Methods for profile image
const handleProfileDrop = (e: DragEvent) => {
  const file = e.dataTransfer?.files[0]
  if (file && file.type.startsWith('image/')) {
    handleProfileFile(file)
  }
}

const handleProfileSelect = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) handleProfileFile(file)
}

const handleProfileFile = (file: File) => {
  profilePreview.value = URL.createObjectURL(file)
}

// Methods for social links
const addLink = () => {
  channelData.links.push({
    title: '',
    url: ''
  })
}

const removeLink = (index: number) => {
  channelData.links.splice(index, 1)
}

// Save changes
const saveChanges = async () => {
  if (!store.state.auth.authenticated) {
    router.push('/login')
    return
  }

  isSaving.value = true
  try {
    // We'll need to implement the actual API call here
    const formData = new FormData()
    formData.append('name', channelData.artistName)
    formData.append('username', channelData.username)
    formData.append('description', channelData.bio)
    formData.append('email', channelData.email)
    formData.append('links', JSON.stringify(channelData.links))

    // Add profile and banner images if changed
    if (profileInput.value?.files?.[0]) {
      formData.append('avatar', profileInput.value.files[0])
    }
    if (bannerInput.value?.files?.[0]) {
      formData.append('cover', bannerInput.value.files[0])
    }

    await axios.patch(`channels/${store.state.auth.username}/`, formData)
    
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
    
    channelData.artistName = channel.artist?.name || ''
    channelData.username = channel.actor.preferred_username
    channelData.bio = channel.artist?.description?.text || ''
    // Add other fields as needed
    
    if (channel.artist?.cover?.urls?.original) {
      bannerPreview.value = store.getters['instance/absoluteUrl'](channel.artist.cover.urls.original)
    }
    
    if (channel.artist?.avatar?.urls?.original) {
      profilePreview.value = store.getters['instance/absoluteUrl'](channel.artist.avatar.urls.original)
    }
    
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
  <div class="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-6">
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
      <div class="relative mb-20">
        <!-- Banner Image -->
        <div class="relative">
          <div
            class="aspect-[21/9] rounded-lg overflow-hidden bg-gray-800"
            @dragover.prevent
            @drop.prevent="handleBannerDrop"
          >
            <img
              v-if="bannerPreview"
              :src="bannerPreview"
              alt="Channel banner"
              class="w-full h-full object-cover"
            />
            <div
              class="absolute inset-0 flex flex-col items-center justify-center gap-3"
              :class="{'bg-black bg-opacity-50': bannerPreview}"
            >
              <ImageIcon 
                v-if="!bannerPreview"
                class="w-12 h-12 text-gray-500" 
              />
              <p class="text-sm text-gray-400">Upload your channel banner Image</p>
              <p class="text-xs text-gray-500">For better results, upload PNG or JPG images of at least 1156x400 pixels.</p>
              <p class="text-xs text-gray-500">2MB file-size limit.</p>
              <input
                type="file"
                ref="bannerInput"
                class="hidden"
                accept="image/*"
                @change="handleBannerSelect"
              />
              <button
                @click="$refs.bannerInput.click()"
                class="px-4 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
              >
                {{ bannerPreview ? 'Change Banner' : 'Upload Banner' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Profile Image -->
        <div class="absolute left-8 -bottom-16">
          <div
            class="relative w-32 h-32 rounded-full overflow-hidden bg-gray-800 border-4 border-gray-900"
            @dragover.prevent
            @drop.prevent="handleProfileDrop"
          >
            <img
              v-if="profilePreview"
              :src="profilePreview"
              alt="Profile image"
              class="w-full h-full object-cover"
            />
            <div
              class="absolute inset-0 flex flex-col items-center justify-center gap-2"
              :class="{'bg-black bg-opacity-50': profilePreview}"
            >
              <UserCircleIcon 
                v-if="!profilePreview"
                class="w-8 h-8 text-gray-500" 
              />
              <p class="text-xs text-gray-400">Upload photo</p>
              <input
                type="file"
                ref="profileInput"
                class="hidden"
                accept="image/*"
                @change="handleProfileSelect"
              />
              <button
                @click="$refs.profileInput.click()"
                class="text-xs underline hover:text-white transition-colors"
              >
                Browse
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Artist Details Form -->
      <div class="space-y-6 max-w-2xl">
        <div>
          <label class="block text-xl mb-2">Your name</label>
          <input
            v-model="channelData.artistName"
            type="text"
            class="w-full bg-gray-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
            placeholder="Enter your name"
          />
        </div>

        <div>
          <label class="block text-xl mb-2">@username</label>
          <input
            v-model="channelData.username"
            type="text"
            class="w-full bg-gray-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
            placeholder="@yourname"
          />
        </div>

        <div>
          <label class="block text-xl mb-2">Description</label>
          <textarea
            v-model="channelData.bio"
            rows="4"
            class="w-full bg-gray-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
            placeholder="Tell us about yourself..."
          ></textarea>
        </div>

        <!-- Social Links -->
        <div class="space-y-4">
          <label class="block text-xl mb-2">Links</label>
          <div
            v-for="(link, index) in channelData.links"
            :key="index"
            class="grid grid-cols-[1fr,2fr] gap-4"
          >
            <input
              v-model="link.title"
              type="text"
              class="w-full bg-gray-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
              placeholder="Link title"
            />
            <div class="flex gap-2">
              <input
                v-model="link.url"
                type="url"
                class="flex-1 bg-gray-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
                placeholder="Link URL"
              />
              <button
                @click="removeLink(index)"
                class="p-2 text-red-400 hover:text-red-300 transition-colors"
                :aria-label="'Remove ' + (link.title || 'link')"
              >
                <TrashIcon class="w-5 h-5" />
              </button>
            </div>
          </div>

          <button
            @click="addLink"
            class="text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-2"
          >
            <PlusIcon class="w-4 h-4" />
            Add link
          </button>
        </div>

        <div>
          <label class="block text-xl mb-2">Email address</label>
          <input
            v-model="channelData.email"
            type="email"
            class="w-full bg-gray-800 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
            placeholder="Enter your email"
          />
        </div>
      </div>
    </div>
  </div>
</template>