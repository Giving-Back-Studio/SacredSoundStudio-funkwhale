<script setup lang="ts">
import type { TagCategory } from '~/types'
import { ref, onMounted } from 'vue'
import axios from 'axios'
import TagCategorySelector from '~/components/library/TagCategorySelector.vue'
import useLogger from '~/composables/useLogger'
import useErrorHandler from '~/composables/useErrorHandler'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const logger = useLogger()
const trackCategories = ref<TagCategory[]>([])

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
    trackCategories.value = []
  } finally {
    measureLoading()
  }
}

onMounted(() => {
  fetchTrackCategories()
})

const updateTags = (category: string, tags: string[]) => {
  const newValue = { ...props.modelValue }
  newValue[category] = tags
  emit('update:modelValue', newValue)
}
</script>

<template>
  <div class="grid grid-cols-2 gap-6">
    <div
      v-for="category in trackCategories"
      :key="category.name">
      <label class="block mb-2">{{ category.name }}{{ category.required ? ' *' : '' }}</label>
      <tag-category-selector
        :model-value="modelValue[category.name] || []"
        @update:model-value="tags => updateTags(category.name, tags)"
        :category="category.name"
        :maxTags="category.max_tags"
        class="w-full" />
    </div>
  </div>
</template>
