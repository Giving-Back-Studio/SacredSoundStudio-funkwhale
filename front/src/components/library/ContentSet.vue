<script setup lang="ts">

import type { Album, Track, ContentType } from '~/types'
import ContentCard from '~/components/audio/ContentCard.vue'

interface Props {
  title: string
  type: ContentType
  content: Album | Track
}

const props = defineProps<Props>()
</script>

<template>
  <div v-if="props.content.length > 0" class="ui segment">
    <div class="ui horizontal divider">{{ props.title }}</div>
    <div class="ui grid">
      <content-card class="four wide column" v-for="(contentItem, index) in props.content" :key="index" :type="props.type" :content="contentItem"/>
    </div>
  </div>
</template>