<script setup lang="ts">
import type { Tag } from '~/types'

import { ref, watch, onMounted, nextTick } from 'vue'
import { isEqual } from 'lodash-es'
import { useStore } from '~/store'

import $ from 'jquery'

interface Events {
  (e: 'update:modelValue', tags: string[]): void
}

interface Props {
  modelValue: string[],
  category: string,
  maxTags: number
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const store = useStore()

const dropdown = ref()
watch(() => props.modelValue, (value) => {
  const current = $(dropdown.value).dropdown('get value').split(',').sort()

  if (!isEqual([...value].sort(), current)) {
    $(dropdown.value).dropdown('set exactly', value)
  }
})

const handleUpdate = () => {
  const $dropdown = $(dropdown.value);
  let value = $dropdown.dropdown('get value').split(',')

  if (props.category === 'Vocals' && value.includes('Instrumental')) {
    value = ['Instrumental'];
  }
  emit('update:modelValue', value)

  if (!$dropdown.hasClass('multiple')) {
    $dropdown.dropdown('hide')
  }
  return value
}

onMounted(async () => {
  await nextTick()

  $(dropdown.value).dropdown({
    keys: { delimiter: 32 },
    forceSelection: false,
    saveRemoteData: false,
    filterRemoteData: true,
    preserveHTML: false,
    maxSelections: props.maxTags,
    apiSettings: {
      url: store.getters['instance/absoluteUrl']('/api/v1/tags/?categories__name='+props.category),
      beforeXHR: function (xhrObject) {
        if (store.state.auth.oauth.accessToken) {
          xhrObject.setRequestHeader('Authorization', store.getters['auth/header'])
        }
        return xhrObject
      },
      onResponse (response) {
        response = { results: [], ...response }

        // @ts-expect-error Semantic UI
        const currentSearch: string = $(dropdown.value).dropdown('get query')

        if (currentSearch) {
          const existingTag = response.results.find((result: Tag) => result.name === currentSearch)

          if (existingTag) {
            if (response.results.indexOf(existingTag) !== 0) {
              response.results = [existingTag, ...response.results]
              response.results.splice(response.results.indexOf(existingTag) + 1, 1)
            }
          } else {
            response.results = [{ name: currentSearch }, ...response.results]
          }
        }
        return response
      }
    },
    fields: { remoteValues: 'results', value: 'name' },
    allowAdditions: true,
    minCharacters: 0,
    onAdd: handleUpdate,
    onRemove: handleUpdate,
    onLabelRemove: handleUpdate,
    onChange: handleUpdate
  })

  $(dropdown.value).dropdown('set exactly', props.modelValue)
})
</script>

<template>
  <div
    ref="dropdown"
    class="ui search selection dropdown"
    :class="{ multiple: props.maxTags > 1 }"
  >
    <input type="hidden">
    <i class="dropdown icon" />
    <input
      id="tags-search"
      type="text"
      class="search"
    >
    <div class="default text">
      {{ $t('components.library.TagSelector.placeholder.search') }}
    </div>
  </div>
</template>
