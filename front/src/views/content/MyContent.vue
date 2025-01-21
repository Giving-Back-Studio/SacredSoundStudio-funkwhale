<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  PencilIcon, 
  SendIcon, 
  AlertCircleIcon,
  MusicIcon 
} from 'lucide-vue-next'

interface ContentItem {
  id: number
  name: string
  image: string
  status: 'draft' | 'in_qa' | 'published' | 'needs_review'
  uploadDate: string
  feedback?: string
}

// Status filter options
const statusFilters = [
  { label: 'All', value: 'all' },
  { label: 'Drafts', value: 'draft' },
  { label: 'In QA', value: 'in_qa' },
  { label: 'Published', value: 'published' },
  { label: 'Needs Review', value: 'needs_review' }
] as const

const currentFilter = ref('all')
const activeFeedback = ref<number | null>(null)

// Mock data - replace with actual API call
const content = ref<ContentItem[]>([
  {
    id: 1,
    name: 'Morning Meditation Chant',
    image: '/placeholder.svg?height=200&width=300',
    status: 'published',
    uploadDate: '2024-01-15T08:00:00Z'
  },
  {
    id: 2,
    name: 'Sacred Sound Journey',
    image: '/placeholder.svg?height=200&width=300',
    status: 'draft',
    uploadDate: '2024-01-16T10:30:00Z'
  },
  {
    id: 3,
    name: 'Healing Mantras Collection',
    image: '/placeholder.svg?height=200&width=300',
    status: 'needs_review',
    feedback: 'Please adjust the audio levels in the second track and resubmit.',
    uploadDate: '2024-01-14T15:45:00Z'
  },
  {
    id: 4,
    name: 'Divine Bhajans Live Recording',
    image: '/placeholder.svg?height=200&width=300',
    status: 'in_qa',
    uploadDate: '2024-01-17T09:15:00Z'
  }
])

// Computed
const filteredContent = computed(() => {
  if (currentFilter.value === 'all') return content.value
  return content.value.filter(item => item.status === currentFilter.value)
})

// Methods
const getStatusClass = (status: ContentItem['status']) => {
  const classes = {
    draft: 'bg-gray-600 text-white',
    in_qa: 'bg-blue-600 text-white',
    published: 'bg-green-600 text-white',
    needs_review: 'bg-yellow-600 text-white'
  }
  return classes[status] || 'bg-gray-600 text-white'
}

const formatStatus = (status: ContentItem['status']) => {
  const formats = {
    draft: 'Draft',
    in_qa: 'In QA',
    published: 'Published',
    needs_review: 'Needs Review'
  }
  return formats[status] || status
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const showFeedback = (item: ContentItem) => {
  activeFeedback.value = item.id
}

const hideFeedback = () => {
  activeFeedback.value = null
}

const editContent = (item: ContentItem) => {
  console.log('Edit content:', item.id)
  // Implement edit functionality
}

const submitForQA = (item: ContentItem) => {
  console.log('Submit for QA:', item.id)
  // Implement submit for QA functionality
}
</script>

<template>
  <main class="main pusher">
    <div class="max-w-7xl mx-auto px-6 py-4">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold">My Content</h1>
        <div class="flex gap-4">
          <button
            v-for="filter in statusFilters"
            :key="filter.value"
            @click="currentFilter = filter.value"
            class="px-4 py-2 rounded-full text-sm transition-colors"
            :class="currentFilter === filter.value 
              ? 'bg-white text-black' 
              : 'bg-gray-800 hover:bg-gray-700'"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>

      <!-- Content Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="item in filteredContent"
          :key="item.id"
          class="bg-gray-800 rounded-lg overflow-hidden group"
        >
          <!-- Content Preview -->
          <div class="relative aspect-video">
            <img
              :src="item.image"
              :alt="item.name"
              class="w-full h-full object-cover"
            />
            <div class="absolute inset-0 bg-black bg-opacity-40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
              <button
                @click="editContent(item)"
                class="p-2 bg-white text-black rounded-full hover:bg-gray-200 transition-colors"
                :aria-label="'Edit ' + item.name"
              >
                <PencilIcon class="w-5 h-5" />
              </button>
              <button
                v-if="item.status === 'draft'"
                @click="submitForQA(item)"
                class="p-2 bg-white text-black rounded-full hover:bg-gray-200 transition-colors"
                :aria-label="'Submit ' + item.name + ' for QA'"
              >
                <SendIcon class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- Content Info -->
          <div class="p-4">
            <div class="flex items-start justify-between gap-4">
              <h3 class="font-semibold text-lg line-clamp-1">{{ item.name }}</h3>
              <div class="flex items-center gap-2">
                <span
                  class="px-2 py-1 text-xs rounded-full"
                  :class="getStatusClass(item.status)"
                >
                  {{ formatStatus(item.status) }}
                </span>
                <div v-if="item.status === 'needs_review'" class="relative">
                  <button
                    @mouseenter="showFeedback(item)"
                    @mouseleave="hideFeedback"
                    class="text-yellow-500 hover:text-yellow-400"
                    :aria-label="'Show feedback for ' + item.name"
                  >
                    <AlertCircleIcon class="w-5 h-5" />
                  </button>
                  <!-- Feedback Tooltip -->
                  <div
                    v-if="activeFeedback === item.id"
                    class="absolute bottom-full right-0 mb-2 w-64 p-3 bg-gray-900 rounded-lg shadow-xl z-10"
                  >
                    <p class="text-sm">{{ item.feedback }}</p>
                    <div class="absolute bottom-0 right-4 transform translate-y-1/2 rotate-45 w-2 h-2 bg-gray-900"></div>
                  </div>
                </div>
              </div>
            </div>
            <p class="text-sm text-gray-400 mt-2">
              {{ formatDate(item.uploadDate) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-if="filteredContent.length === 0"
        class="text-center py-16 bg-gray-800 rounded-lg mt-6"
      >
        <MusicIcon class="w-16 h-16 mx-auto text-gray-600 mb-4" />
        <h3 class="text-xl font-semibold mb-2">No content found</h3>
        <p class="text-gray-400">
          {{ currentFilter === 'all' 
            ? "You haven't uploaded any content yet" 
            : `You don't have any ${formatStatus(currentFilter).toLowerCase()} content` }}
        </p>
      </div>
    </div>
  </main>
</template>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 