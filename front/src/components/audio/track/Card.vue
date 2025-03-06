<script setup lang="ts">
import type { Track } from '~/types'

import PlayButton from '~/components/audio/PlayButton.vue'
import { computed } from 'vue'
import { useStore } from '~/store'

interface Props {
  track: Track
}

const props = defineProps<Props>()
const store = useStore()

const imageUrl = computed(() => {
  if (props.track.cover) {
    return store.getters['instance/absoluteUrl'](props.track.cover.urls.medium_square_crop)
  }
  if (props.track.album.cover) {
    return store.getters['instance/absoluteUrl'](props.track.album.cover.urls.medium_square_crop)
  }
})
</script>

<template>
  <div class="track-card">
    <div class="track-cover">
      <img :src="imageUrl" :alt="track.title" />
      <div class="play-overlay">
        <play-button
          id="playmenu"
          class="primary"
          :discrete="true"
          :is-playable="track.is_playable"
          :track="track"
        />
      </div>
    </div>
    <div class="track-title">{{ track.title }}</div>
    <div class="track-artist">{{ track.artist.name }}</div>
    <div class="track-metadata">
      <span class="track-genre">{{ track.tags.Genre[0] }}</span>
      <span class="track-duration">
        <human-duration
          v-if="track.uploads[0] && track.uploads[0].duration"
          :duration="track.uploads[0].duration"
        />
      </span>
    </div>
  </div>
</template>