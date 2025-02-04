<template>
  <div class="min-h-screen site-background">
    <main class="container mx-auto px-4 py-8">
      <div v-for="category in categories" :key="category.id" class="mb-12">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-primary">{{ category.title }}</h2>
          <div class="flex items-center gap-4">
            <div class="flex gap-2">
              <button 
                @click="scroll(category.id, 'left')"
                class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 transition-colors"
                :disabled="scrollPositions[category.id] <= 0"
                :aria-label="`Scroll ${category.title} left`"
              >
                <ChevronLeft class="h-5 w-5 chevron-icon" />
              </button>
              <button 
                @click="scroll(category.id, 'right')"
                class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 transition-colors"
                :disabled="isRightScrollDisabled(category.id)"
                :aria-label="`Scroll ${category.title} right`"
              >
                <ChevronRight class="h-5 w-5 chevron-icon" />
              </button>
            </div>
            <button 
              class="text-base font-semibold text-primary hover:underline bg-transparent hover:bg-transparent"
              @click="viewMore(category.id)"
            >
              More
            </button>
          </div>
        </div>

        <div 
          class="relative overflow-hidden no-scroll"
          :ref="el => { if (el) scrollContainers[category.id] = el }"
        >
          <div 
            class="flex gap-4 overflow-x-auto scrollbar-hide scroll-smooth no-scroll"
            @scroll="updateScrollPosition(category.id, $event)"
          >
            <div 
              v-for="item in category.items" 
              :key="item.id"
              class="flex-none w-[280px]"
            >
              <div class="bg-white rounded-lg shadow-sm overflow-hidden transition-transform hover:scale-[1.02]">
                <div class="aspect-square relative">
                  <img 
                    :src="item.cover" 
                    :alt="item.title"
                    class="w-full h-full object-cover"
                  />
                </div>
                <div class="p-4">
                  <h3 class="font-semibold text-[#434289] mb-1">{{ item.title }}</h3>
                  <p class="text-sm text-gray-600">{{ item.artist }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const scrollContainers = ref({})
const scrollPositions = ref({})

const categories = ref([
  {
    id: 'studio',
    title: 'Studio Production',
    items: Array.from({ length: 10 }, (_, i) => ({
      id: `studio-${i}`,
      title: `Studio Track ${i + 1}`,
      artist: `Artist ${i + 1}`,
      cover: `/placeholder.svg?height=280&width=280`
    }))
  },
  {
    id: 'meditation',
    title: 'Meditation',
    items: Array.from({ length: 10 }, (_, i) => ({
      id: `meditation-${i}`,
      title: `Meditation Session ${i + 1}`,
      artist: `Guide ${i + 1}`,
      cover: `/placeholder.svg?height=280&width=280`
    }))
  },
  {
    id: 'djset',
    title: 'DJ Set',
    items: Array.from({ length: 10 }, (_, i) => ({
      id: `djset-${i}`,
      title: `DJ Set ${i + 1}`,
      artist: `DJ ${i + 1}`,
      cover: `/placeholder.svg?height=280&width=280`
    }))
  },
  {
    id: 'live',
    title: 'Live Recording',
    items: Array.from({ length: 10 }, (_, i) => ({
      id: `live-${i}`,
      title: `Live Session ${i + 1}`,
      artist: `Performer ${i + 1}`,
      cover: `/placeholder.svg?height=280&width=280`
    }))
  }
])

const isRightScrollDisabled = (categoryId) => {
  const container = scrollContainers.value[categoryId]
  if (!container) return true
  
  return container.scrollLeft + container.clientWidth >= container.scrollWidth
}

const scroll = (categoryId, direction) => {
  const container = scrollContainers.value[categoryId]
  if (!container) return
  
  const scrollAmount = container.clientWidth * 0.8 // 80% of container width
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
  // Implement view more functionality
  console.log(`View more for ${categoryId}`)
}

onMounted(() => {
  // Initialize scroll positions
  categories.value.forEach(category => {
    scrollPositions.value[category.id] = 0
  })
})
</script>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

:deep(.chevron-icon) {
  color: var(--primary-color);
}

.no-scroll {
  -webkit-overflow-scrolling: none;
  -ms-overflow-style: none;
  scrollbar-width: none;
  overflow: hidden;
  overscroll-behavior: none; /* Prevents scroll chaining */
  touch-action: none; /* Prevents touch scrolling */
}

.site-background {
  overflow-y: auto;
  overscroll-behavior-y: auto;
  height: 100vh;
}
</style>