<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { ChevronLeft, ChevronRight, Edit2, Trash2, Clock } from 'lucide-vue-next'
import moment from 'moment'

import { useStore } from '~/store'
import PlayButton from '~/components/audio/PlayButton.vue'
import ContentCard from '~/components/audio/ContentCard.vue'
import useLogger from '~/composables/useLogger'
import useErrorHandler from '~/composables/useErrorHandler'

const store = useStore()

const props = defineProps({
  artistFilter: {
    type: Number,
    default: null
  }
})

const logger = useLogger()

const scrollContainers = ref({})
const scrollPositions = ref({})
const selectedCategory = ref("Category")

const content = ref([])

// Load TaggedItems with optional artist filter
const fetchContent = async () => {
  const params = {}
  if (props.artistFilter) {
    params.artist = props.artistFilter
  }

  const measureLoading = logger.time('Fetching Content')
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

onMounted(fetchContent)

// Watch for changes in artist filter
watch(() => props.artistFilter, fetchContent)

const trackCategories = ref([])

const fetchTrackCategories = async () => {
  const params = {
    content_type__model: 'track'
  }

  const measureLoading = logger.time('Fetching track categories')
  try {
    const response = await axios.get('tag-categories/', {
      params,
      paramsSerializer: {
        indexes: null
      }
    })

    trackCategories.value = response.data.results
  } catch (error) {
    useErrorHandler(error)
    trackCategories.value = undefined
  } finally {
    measureLoading()
  }
}

onMounted(fetchTrackCategories)

const categories = computed(() => {
  const NONE = "None"
  const cats = {}

  for (const item of content.value) {
    let duration = 0;
    if (item.uploads.length > 0) {
      duration = item.uploads[0].duration
    }

    for (const tagCategoryIdx in trackCategories.value) {
      const tagCategory = trackCategories.value[tagCategoryIdx].name
      if (tagCategory == selectedCategory.value) {
        const tags = item.tags[tagCategory]
        if (!tags) {
          if (!cats[NONE]) cats[NONE] = []
          cats[NONE].push(item)
          scrollPositions.value[NONE] = 0
          continue
        }

        for (const tag of tags) {
          if (cats[tag] && !cats[tag].includes(item)) {
            cats[tag].push(item)
          } else {
            cats[tag] = [item]
            scrollPositions.value[tag] = 0
          }
        }
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

const deleteContent = (item) => {
  console.log('Delete content:', item)
  axios.delete(`/tracks/${item.id}`)
    .then(() => {
      content.value = content.value.filter(i => i.id !== item.id)
    })
    .catch(useErrorHandler)
}
</script>

<template>
  <div>
    <div>
      <label class="mr-2" for="category">Explore By:</label>
      <select
        id="category"
        v-model="selectedCategory"
        class="ui dropdown"
      >
        <option
          v-for="category in trackCategories"
          :key="category.id"
          :value="category.name"
        >
        {{ category.name }}
        </option>
      </select>
    </div>
    <div class="ui divider"></div>
    <div v-for="([category, items]) in categories" :key="category" class="mb-12">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-serif">{{ category }}</h2>
        <div v-if="items.length > 4" class="flex items-center gap-4">
          <div class="flex gap-2">
            <button 
              @click="scroll(category, 'left')"
              class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 transition-colors"
              :disabled="scrollPositions[category] <= 0"
              :aria-label="`Scroll ${category} left`"
            >
              <ChevronLeft class="h-5 w-5" />
            </button>
            <button 
              @click="scroll(category, 'right')"
              class="p-2 rounded-full bg-white shadow-sm hover:bg-gray-50 transition-colors"
              :aria-label="`Scroll ${category} right`"
            >
              <ChevronRight class="h-5 w-5" />
            </button>
          </div>
          <button 
            class="text-sm font-medium hover:underline"
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
          class="ui stackable cards"
          @scroll="updateScrollPosition(category, $event)"
        >
          <content-card
            v-for="item in items" 
            :key="item.id"
            :track="item"
          />
        </div>
      </div>
    </div>
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

:deep(h1), :deep(h2) {
  color: var(--primary-color);
}

:deep(.text-primary) {
  color: var(--primary-color);
}

:deep(button), :deep(.button) {
  color: var(--primary-color);
}

:deep(.bg-primary) {
  background-color: var(--primary-color);
}

:deep(.content-card) {
  background: var(--form-background);
}

button:hover {
  background-color: white !important;
}
</style>
