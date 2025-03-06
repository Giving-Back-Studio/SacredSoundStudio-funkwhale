<script setup lang="ts">
import type { Track, Album } from '~/types'

import PlayButton from '~/components/audio/PlayButton.vue'
import { computed } from 'vue'
import { useStore } from '~/store'

interface Props {
  track?: Track
  album?: Album
}

const props = defineProps<Props>()
const store = useStore()

const content = computed(() => (props.track || props.album))

const imageUrl = computed(() => {
  if (content.value.cover) {
    return store.getters['instance/absoluteUrl'](content.value.cover.urls.medium_square_crop)
  }
  if (props.track && props.track.album && props.track.album.cover) {
    return store.getters['instance/absoluteUrl'](props.track.album.cover.urls.medium_square_crop)
  }
})

const tagList = computed(() => {
    return [...new Set(Object.values(content.value.tags).flat())] 
})
</script>

<template>
  <div class="ui card center aligned text">
    <slot />
    <router-link :to="{name: track ? 'library.tracks.detail' : 'library.albums.detail', params: {id: content.id}}">{{ content.title }}</router-link>
    <div>
      by
      <router-link :to="{name: 'channels.detail', params: {id: content.artist.channel.actor.preferred_username }}">
        {{ content.artist.name }}
      </router-link>
    </div>
    <div class="track-cover middle aligned">
      <img :src="imageUrl" :alt="content.title" />
      <div class="play-overlay">
        <router-link
            v-for="tag in tagList"
            :to="{name: 'library.tags.detail', params: {id: tag}}"
        >
          #{{ tag }}
        </router-link>
      </div>
    </div>
    <div class="horizontal center aligned">
      <human-duration class="mr-2"
        v-if="track && track.uploads[0] && track.uploads[0].duration"
        :duration="track.uploads[0].duration"
      />
      <play-button
        id="playmenu"
        class="play-button basic icon"
        :is-playable="content.is_playable"
        :hidePlayText="true"
        :track="track"
        :album="album"
      />
    </div>
  </div>
</template>

<style>

.ui.card {
    box-shadow: none !important;
}

.track-cover {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.track-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(67, 66, 137, 0.3);
  display: flex;
  opacity: 0;
  transition: opacity 0.2s;
  flex-wrap: wrap;
  place-content: space-evenly;
}

.track-cover:hover .play-overlay {
  opacity: 1;
}
</style>