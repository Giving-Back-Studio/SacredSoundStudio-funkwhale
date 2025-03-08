<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { ChevronLeft, ChevronRight, Edit2, Trash2, Clock } from 'lucide-vue-next'
import moment from 'moment'

import { useStore } from '~/store'
import PlayButton from '~/components/audio/PlayButton.vue'
import ContentCard from '~/components/audio/ContentCard.vue'
import ContentSet from '~/components/library/ContentSet.vue'
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
          continue
        }

        for (const tag of tags) {
          if (cats[tag] && !cats[tag].includes(item)) {
            cats[tag].push(item)
          } else {
            cats[tag] = [item]
          }
        }
      }
    }
  }

  return Object.entries(cats).sort((a, b) => b[1].length - a[1].length)
})

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
  <content-set
    v-for="([category, items]) in categories"
    :content="items"
    type="track"
    :title="category"
  />
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
