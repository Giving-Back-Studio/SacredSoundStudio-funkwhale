<script setup lang="ts">
import type { Track, Album, ContentType } from '~/types'

import PlayButton from '~/components/audio/PlayButton.vue'
import { computed } from 'vue'
import { useStore } from '~/store'

interface Props {
  content: Album | Track,
  type: ContentType
}

const props = defineProps<Props>()
const store = useStore()

const isTrack = computed(() => {
  return props.type === "track"
})

const imageUrl = computed(() => {
  if (props.content.cover) {
    return store.getters['instance/absoluteUrl'](props.content.cover.urls.medium_square_crop)
  }
  if (isTrack.value && props.content.album && props.content.album.cover) {
    return store.getters['instance/absoluteUrl'](props.content.album.cover.urls.medium_square_crop)
  }
})

const tagList = computed(() => {
    return [...new Set(Object.values(props.content.tags).flat())]
})
</script>

<template>
  <div class="ui center aligned">
    <div class="content-cover middle aligned">
      <img :src="imageUrl" :alt="props.content.title" />
      <div class="play-overlay">
        <router-link
            v-for="tag in tagList"
            :to="{name: 'library.tags.detail', params: {id: tag}}"
        >
          #{{ tag }}
        </router-link>
      </div>
    </div>
    <div class="ui content mt-2">
      <router-link
        :to="{name: isTrack ? 'library.tracks.detail' : 'library.albums.detail', params: {id: props.content.id}}">
        <h3 class="ui header title">{{ props.content.title }}</h3>
      </router-link>
      <router-link :to="{name: 'channels.detail', params: {id: props.content.artist.channel.actor.preferred_username }}">
          {{ props.content.artist.name }}
      </router-link>
      <div class="content">
        <play-button
          id="playmenu"
          class="ui play-button primary basic icon"
          :is-playable="props.content.is_playable"
          :track="props.type === 'track' ? props.content : null"
          :album="props.type === 'album' ? props.content : null"
        >
          <human-duration class="ui"
            v-if="isTrack && props.content.uploads[0] && props.content.uploads[0].duration"
            :duration="props.content.uploads[0].duration"
          />
        </play-button>
      </div>
    </div>
  </div>
</template>

<style>

.content-cover {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
}

.content-cover img {
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

.content-cover:hover .play-overlay {
  opacity: 1;
}

.title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%; /* Adjust as needed */
}
</style>