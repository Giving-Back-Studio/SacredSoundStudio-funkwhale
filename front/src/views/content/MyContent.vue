<script setup>
import { computed, ref, onMounted } from 'vue'
import axios from 'axios'
import { ChevronLeft, ChevronRight, UploadCloud, Edit2, Trash2, Clock } from 'lucide-vue-next'

import store from '~/store'
import useLogger from '~/composables/useLogger'
import useErrorHandler from '~/composables/useErrorHandler'

const logger = useLogger();

const scrollContainers = ref({})
const scrollPositions = ref({})

const content = ref([])

// Load TaggedItems filtered by Artist
const fetchContent = async () => {
  const params = {
    artist: store.state.auth.profile.artist
  }

  const measureLoading = logger.time('Fetching My Content')
  try {
    const response = await axios.get('/tracks', {
      params,
      paramsSerializer: {
        indexes: null
      }
    })

    content.value = response.data.results
  } catch (error) {
    useErrorHandler(error)
    content.value = undefined
  } finally {
    measureLoading()
  }
}
fetchContent()

const categories = computed(() => {
  const cats = {}

  for (const item of content.value) {
    const slimItem = {
      id: item.id,
      title: item.title,
      artist: item.artist.name,
      duration: item.uploads?.duration,
      cover: item.cover || item.album.cover?.urls?.medium_square_crop || '/placeholder.svg?height=280&width=280'
    }

    for (const tagIdx in item.tags) {
      const tag = item.tags[tagIdx]
      if (cats[tag] && !cats[tag].includes(slimItem)) {
        cats[tag].push(slimItem)
      } else {
        cats[tag] = [slimItem]
        scrollPositions.value[tag] = 0
      }
    }
  }

  return Object.entries(cats).sort((a, b) => b[1].length - a[1].length)
})

const scroll = (categoryId, direction) => {
  const container = scrollContainers.value[categoryId]
  if (!container) return
  
  const scrollAmount = 600
  const scrollLeft = direction === 'left' 
    ? container.scrollLeft - scrollAmount
    : container.scrollLeft + scrollAmount
    
  container.scrollTo({
    left: scrollLeft,
    behavior: 'smooth'
  })
}

const updateScrollPosition = (categoryId, event) => {
  scrollPositions.value[categoryId] = event.target.scrollLeft
}

const viewMore = (categoryId) => {
  console.log(`View more for ${categoryId}`)
}

const initiateUpload = (categoryId) => {
  console.log(`Initiate upload for ${categoryId}`)
}

const editContent = (item) => {
  console.log('Edit content:', item)
}

const deleteContent = (item) => {
  console.log('Delete content:', item)
}
</script>

<template>
  <div class="min-h-screen bg-[#F1F4F8]">
    <main class="container mx-auto px-4 py-8">
      <h1 class="text-4xl font-bold text-[#434289] mb-8">My Content</h1>
      
      <div v-for="([category, items]) in categories" :key="category" class="mb-12">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-[#434289]">{{ category }}</h2>
          <div v-if="items.length > 4" class="flex items-center gap-4">
            <div class="flex gap-2">
              <button 
                @click="scroll(category, 'left')"
                class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 transition-colors"
                :disabled="scrollPositions[category] <= 0"
                :aria-label="`Scroll ${category} left`"
              >
                <ChevronLeft class="h-5 w-5 text-[#434289]" />
              </button>
              <button 
                @click="scroll(category, 'right')"
                class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 transition-colors"
                :aria-label="`Scroll ${category} right`"
              >
                <ChevronRight class="h-5 w-5 text-[#434289]" />
              </button>
            </div>
            <button 
              class="text-sm font-medium text-[#434289] hover:underline"
              @click="viewMore(category)"
            >
              More
            </button>
          </div>
        </div>

        <div 
          class="relative overflow-hidden"
          :ref="el => { if (el) scrollContainers[category] = el }"
        >
          <div 
            class="flex gap-4 overflow-x-auto scrollbar-hide scroll-smooth"
            @scroll="updateScrollPosition(category, $event)"
          >

            <!-- Content Items -->
            <div 
              v-for="item in items" 
              :key="item.id"
              class="flex-none w-[280px]"
            >
              <div class="bg-white rounded-lg shadow-sm overflow-hidden transition-transform hover:scale-[1.02]">
                <div class="aspect-square relative group">
                  <img 
                    :src="item.cover" 
                    :alt="item.title"
                    class="w-full h-full object-cover"
                  />
                  <div class="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
                    <button 
                      class="p-2 rounded-full bg-white text-[#434289] hover:bg-gray-100"
                      @click.stop="editContent(item)"
                    >
                      <Edit2 class="h-5 w-5" />
                    </button>
                    <button 
                      class="p-2 rounded-full bg-white text-red-500 hover:bg-gray-100"
                      @click.stop="deleteContent(item)"
                    >
                      <Trash2 class="h-5 w-5" />
                    </button>
                  </div>
                </div>
                <div class="p-4">
                  <h3 class="font-semibold text-[#434289] mb-1">{{ item.title }}</h3>
                  <p class="text-sm text-gray-600">{{ item.artist }}</p>
                  <div class="flex items-center gap-2 mt-2">
                    <Clock class="h-4 w-4 text-gray-400" />
                    <span class="text-sm text-gray-500">{{ item.duration }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>