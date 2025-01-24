<script setup>
import { ref, onMounted } from 'vue'
import { ChevronLeft, ChevronRight, UploadCloud, Edit2, Trash2, Clock } from 'lucide-vue-next'

const scrollContainers = ref({})
const scrollPositions = ref({})

const categories = ref([
  {
    id: 'studio',
    title: 'Studio Production',
    items: Array.from({ length: 5 }, (_, i) => ({
      id: `studio-${i}`,
      title: `Studio Track ${i + 1}`,
      artist: 'You',
      duration: '3:45',
      cover: `/placeholder.svg?height=280&width=280`
    }))
  },
  {
    id: 'meditation',
    title: 'Meditation',
    items: Array.from({ length: 3 }, (_, i) => ({
      id: `meditation-${i}`,
      title: `Meditation Session ${i + 1}`,
      artist: 'You',
      duration: '15:00',
      cover: `/placeholder.svg?height=280&width=280`
    }))
  },
  {
    id: 'djset',
    title: 'DJ Set',
    items: Array.from({ length: 4 }, (_, i) => ({
      id: `djset-${i}`,
      title: `DJ Set ${i + 1}`,
      artist: 'You',
      duration: '60:00',
      cover: `/placeholder.svg?height=280&width=280`
    }))
  },
  {
    id: 'live',
    title: 'Live Recording',
    items: Array.from({ length: 2 }, (_, i) => ({
      id: `live-${i}`,
      title: `Live Session ${i + 1}`,
      artist: 'You',
      duration: '45:00',
      cover: `/placeholder.svg?height=280&width=280`
    }))
  }
])

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

onMounted(() => {
  categories.value.forEach(category => {
    scrollPositions.value[category.id] = 0
  })
})
</script>

<template>
  <div class="min-h-screen bg-[#F1F4F8]">
    <main class="container mx-auto px-4 py-8">
      <h1 class="text-4xl font-bold text-[#434289] mb-8">My Content</h1>
      
      <div v-for="category in categories" :key="category.id" class="mb-12">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-[#434289]">{{ category.title }}</h2>
          <div class="flex items-center gap-4">
            <div class="flex gap-2">
              <button 
                @click="scroll(category.id, 'left')"
                class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 transition-colors"
                :disabled="scrollPositions[category.id] <= 0"
                :aria-label="`Scroll ${category.title} left`"
              >
                <ChevronLeft class="h-5 w-5 text-[#434289]" />
              </button>
              <button 
                @click="scroll(category.id, 'right')"
                class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 transition-colors"
                :aria-label="`Scroll ${category.title} right`"
              >
                <ChevronRight class="h-5 w-5 text-[#434289]" />
              </button>
            </div>
            <button 
              class="text-sm font-medium text-[#434289] hover:underline"
              @click="viewMore(category.id)"
            >
              More
            </button>
          </div>
        </div>

        <div 
          class="relative overflow-hidden"
          :ref="el => { if (el) scrollContainers[category.id] = el }"
        >
          <div 
            class="flex gap-4 overflow-x-auto scrollbar-hide scroll-smooth"
            @scroll="updateScrollPosition(category.id, $event)"
          >
            <!-- Upload Card -->
            <div class="flex-none w-[280px]">
              <button 
                @click="initiateUpload(category.id)"
                class="w-full h-full bg-white rounded-lg shadow-sm overflow-hidden transition-transform hover:scale-[1.02] group"
              >
                <div class="aspect-square flex flex-col items-center justify-center p-6 border-2 border-dashed border-[#434289] rounded-lg m-4">
                  <UploadCloud class="h-12 w-12 text-[#434289] mb-4 group-hover:scale-110 transition-transform" />
                  <p class="font-semibold text-[#434289] text-center">Upload {{ category.title }}</p>
                  <p class="text-sm text-gray-600 text-center mt-2">Click to browse or drag and drop</p>
                </div>
              </button>
            </div>

            <!-- Content Items -->
            <div 
              v-for="item in category.items" 
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