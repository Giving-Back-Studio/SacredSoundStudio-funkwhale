<script setup lang="ts">
import { usePlayer } from '~/composables/audio/player'
import { useQueue } from '~/composables/audio/queue'

import { useMouse, useWindowSize } from '@vueuse/core'
import { computed, ref } from 'vue'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'

import onKeyboardShortcut from '~/composables/onKeyboardShortcut'
import time from '~/utils/time'

import TrackFavoriteIcon from '~/components/favorites/TrackFavoriteIcon.vue'
import TrackPlaylistIcon from '~/components/playlists/TrackPlaylistIcon.vue'
import PlayerControls from '../PlayerControls.vue'
import VolumeControl from '../VolumeControl.vue'
import Favorite from '~/components/audio/multimedia/Favorite.vue'

const {
  LoopingMode,
  initializeFirstTrack,
  isPlaying,
  mute,
  volume,
  toggleLooping,
  looping,
  seekBy,
  seekTo,
  currentTime,
  duration,
  bufferProgress,
  loading: isLoadingAudio
} = usePlayer()

const {
  playPrevious,
  playNext,
  hasNext,
  queue,
  currentIndex,
  currentTrack,
  isShuffled,
  shuffle,
  clear
} = useQueue()

const store = useStore()
const { t } = useI18n()

const toggleMobilePlayer = () => {
  store.commit('ui/queueFocused', ['queue', 'player'].includes(store.state.ui.queueFocused as string) ? null : 'player')
}

// Key binds
onKeyboardShortcut('e', toggleMobilePlayer)
onKeyboardShortcut('p', () => {
  isPlaying.value = !isPlaying.value
  run()
})
onKeyboardShortcut('s', shuffle)
onKeyboardShortcut('q', clear)
onKeyboardShortcut('m', mute)
onKeyboardShortcut('l', toggleLooping)
onKeyboardShortcut('f', () => store.dispatch('favorites/toggle', currentTrack.value?.id))
onKeyboardShortcut('escape', () => store.commit('ui/queueFocused', null))

onKeyboardShortcut(['shift', 'up'], () => (volume.value += 0.1), true)
onKeyboardShortcut(['shift', 'down'], () => (volume.value -= 0.1), true)

onKeyboardShortcut('right', () => seekBy(5), true)
onKeyboardShortcut(['shift', 'right'], () => seekBy(30), true)
onKeyboardShortcut('left', () => seekBy(-5), true)
onKeyboardShortcut(['shift', 'left'], () => seekBy(-30), true)

onKeyboardShortcut(['ctrl', 'shift', 'left'], playPrevious, true)
onKeyboardShortcut(['ctrl', 'shift', 'right'], playNext, true)

const labels = computed(() => ({
  audioPlayer: t('components.audio.Player.label.audioPlayer'),
  previous: t('components.audio.Player.label.previousTrack'),
  play: t('components.audio.Player.label.play'),
  pause: t('components.audio.Player.label.pause'),
  next: t('components.audio.Player.label.nextTrack'),
  unmute: t('components.audio.Player.label.unmute'),
  mute: t('components.audio.Player.label.mute'),
  expandQueue: t('components.audio.Player.label.expandQueue'),
  shuffle: t('components.audio.Player.label.shuffleQueue'),
  clear: t('components.audio.Player.label.clearQueue'),
  addArtistContentFilter: t('components.audio.Player.label.addArtistContentFilter')
}))

const switchTab = () => {
  store.commit('ui/queueFocused', store.state.ui.queueFocused === 'player' ? 'queue' : 'player')
}

const progressBar = ref<HTMLDivElement | null>(null)
const { x } = useMouse({ type: 'client' })
const { width: screenWidth } = useWindowSize({ includeScrollbar: false })

const handleProgressClick = (event: MouseEvent) => {
  if (progressBar.value) {
    const rect = progressBar.value.getBoundingClientRect()
    const clickPosition = event.clientX - rect.left
    const newTime = (clickPosition / rect.width) * duration.value
    seekTo(newTime)
  }
}

const progressBarWidth = computed(() => {
  return (currentTime.value / duration.value) * 100
})

initializeFirstTrack()

const loopingTitle = computed(() => {
  const mode = looping.value
  return mode === LoopingMode.None
    ? t('components.audio.Player.label.loopingDisabled')
    : mode === LoopingMode.LoopTrack
      ? t('components.audio.Player.label.loopingTrack')
      : t('components.audio.Player.label.loopingQueue')
})

const hideArtist = () => {
  if (currentTrack.value.artistId !== -1) {
    return store.dispatch('moderation/hide', {
      type: 'artist',
      target: {
        id: currentTrack.value.artistId,
        name: currentTrack.value.artistName
      }
    })
  }
}

const run = () => {
  console.log('bufferProgress:', bufferProgress)
  console.log('x:', x)
  console.log('screenWidth:', screenWidth)

  console.log(`${bufferProgress.value - 100}%`)
  console.log(`${x.value / screenWidth.value * 100 - 100}%`)
}

</script>

<template>
  <section
    v-if="currentTrack"
    role="complementary"
    class="bg-gray-900 text-white custom-fixed bottom-0 w-full p-4 z-50"
    aria-labelledby="player-label"
  >
    <h1
      id="player-label"
      class="sr-only"
    >
      Player
    </h1>

    <!-- Player Controls -->
    <div class="flex flex-col md:flex-row items-center justify-between gap-4 mt-2">
      <div class="flex items-center gap-4">
        <!-- Track Cover -->
        <div
          class="w-12 h-12 bg-gray-600 rounded overflow-hidden"
          @click.stop.prevent="$router.push({name: 'library.tracks.detail', params: {id: currentTrack.id }})"
        >
          <img
            :src="$store.getters['instance/absoluteUrl'](currentTrack.coverUrl)"
            alt="Track Cover"
            class="w-full h-full object-cover"
          >
        </div>

        <!-- Track Info -->
        <div class="min-w-0 text-center md:text-left">
          <strong class="block text-sm truncate">
            <router-link
              :to="{name: 'library.tracks.detail', params: {id: currentTrack.id }}"
            >
              {{ currentTrack.title }}
            </router-link>
          </strong>
          <div class="text-xs text-gray-400 truncate">
            <router-link
              :to="{name: 'library.artists.detail', params: {id: currentTrack.artistId }}"
            >
              {{ currentTrack.artistName ?? $t('components.audio.Player.meta.unknownArtist') }}
            </router-link>
            <span class="mx-1">•</span>
            <router-link
              :to="{name: 'library.albums.detail', params: {id: currentTrack.albumId }}"
            >
              {{ currentTrack.albumTitle ?? $t('components.audio.Player.meta.unknownAlbum') }}
            </router-link>
          </div>
        </div>

        <!--  Favorite icon button -->
        <Favorite :track="currentTrack" />
      </div>

      <!-- Progress Bar, Timestamps & Playback Controls -->
      <div class="grow flex-col items-center gap-4">
        <!-- Progress Bar and Timestamps -->
        <div class="flex items-center justify-between gap-2 w-full md:w-3/4 lg:w-3/5 mx-auto">
          <span class="text-xs text-gray-400">{{ time.parse(Math.round(currentTime)) }}</span>
          <div
            ref="progressBar"
            class="relative flex-1 h-2 bg-gray-700 cursor-pointer mx-2 rounded"
            @click.stop.prevent="handleProgressClick"
          >
            <div
              class="absolute top-0 left-0 h-full bg-gray-500 rounded transition-all duration-300"
              :style="{ 'width': `${bufferProgress}%` }"
            />
            <div
              class="absolute top-0 left-0 h-full bg-green-500 rounded transition-all duration-300"
              :style="{ 'width': `${progressBarWidth}%` }"
            />
          </div>
          <span class="text-xs text-gray-400">{{ time.parse(Math.round(duration)) }}</span>
        </div>

        <!-- Playback Controls -->
        <div class="flex items-center justify-center gap-4">
          <!-- Shuffle -->
          <button
            :class="['p-2', 'rounded-full', isShuffled ? 'bg-green-500 hover:bg-green-600' : 'bg-gray-700', 'hover:bg-gray-600']"
            :disabled="queue.length === 0"
            :title="labels.shuffle"
            :aria-label="labels.shuffle"
            @click.stop.prevent="shuffle()"
          >
            <svg
              class="w-5 h-5 text-white"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 512 512"
            ><path d="M403.8 34.4c12-5 25.7-2.2 34.9 6.9l64 64c6 6 9.4 14.1 9.4 22.6s-3.4 16.6-9.4 22.6l-64 64c-9.2 9.2-22.9 11.9-34.9 6.9s-19.8-16.6-19.8-29.6l0-32-32 0c-10.1 0-19.6 4.7-25.6 12.8L284 229.3 244 176l31.2-41.6C293.3 110.2 321.8 96 352 96l32 0 0-32c0-12.9 7.8-24.6 19.8-29.6zM164 282.7L204 336l-31.2 41.6C154.7 401.8 126.2 416 96 416l-64 0c-17.7 0-32-14.3-32-32s14.3-32 32-32l64 0c10.1 0 19.6-4.7 25.6-12.8L164 282.7zm274.6 188c-9.2 9.2-22.9 11.9-34.9 6.9s-19.8-16.6-19.8-29.6l0-32-32 0c-30.2 0-58.7-14.2-76.8-38.4L121.6 172.8c-6-8.1-15.5-12.8-25.6-12.8l-64 0c-17.7 0-32-14.3-32-32s14.3-32 32-32l64 0c30.2 0 58.7 14.2 76.8 38.4L326.4 339.2c6 8.1 15.5 12.8 25.6 12.8l32 0 0-32c0-12.9 7.8-24.6 19.8-29.6s25.7-2.2 34.9 6.9l64 64c6 6 9.4 14.1 9.4 22.6s-3.4 16.6-9.4 22.6l-64 64z" /></svg>
          </button>
          <!-- Previous -->
          <button
            class="p-2 bg-gray-700 rounded-full hover:bg-gray-600"
            :title="labels.previous"
            :aria-label="labels.previous"
            @click.prevent.stop="playPrevious()"
          >
            <svg
              class="w-5 h-5 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M18 5v14l-8.5-7L18 5zm-9 14V5H7v14h2z" />
            </svg>
          </button>
          <!-- Play/Pause -->
          <button
            class="p-4 bg-green-500 rounded-full hover:bg-green-600"
            @click.prevent.stop="isPlaying = !isPlaying"
          >
            <svg
              v-if="!isPlaying"
              class="w-6 h-6 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M8 5v14l11-7L8 5z" />
            </svg>
            <svg
              v-else
              class="w-6 h-6 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M6 5h4v14H6zm8 0h4v14h-4z" />
            </svg>
          </button>
          <!-- Next -->
          <button
            class="p-2 bg-gray-700 rounded-full hover:bg-gray-600"
            :title="labels.next"
            :aria-label="labels.next"
            :disabled="!hasNext"
            @click.prevent.stop="playNext()"
          >
            <svg
              class="w-5 h-5 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M6 19l8.5-7L6 5v14zm9-14v14h2V5h-2z" />
            </svg>
          </button>
          <!-- Repeat -->
          <button class="p-2 bg-gray-700 rounded-full hover:bg-gray-600">
            <svg
              class="w-5 h-5 text-white"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 512 512"
            ><path d="M463.5 224l8.5 0c13.3 0 24-10.7 24-24l0-128c0-9.7-5.8-18.5-14.8-22.2s-19.3-1.7-26.2 5.2L413.4 96.6c-87.6-86.5-228.7-86.2-315.8 1c-87.5 87.5-87.5 229.3 0 316.8s229.3 87.5 316.8 0c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0c-62.5 62.5-163.8 62.5-226.3 0s-62.5-163.8 0-226.3c62.2-62.2 162.7-62.5 225.3-1L327 183c-6.9 6.9-8.9 17.2-5.2 26.2s12.5 14.8 22.2 14.8l119.5 0z" /></svg>
          </button>
        </div>
      </div>

      <!-- Playlist Buttons -->
      <div class="flex gap-2 md:gap-3 mt-2">
        <!-- Hide song -->
        <button class="p-2 bg-gray-700 rounded-full hover:bg-gray-600">
          <svg
            class="w-5 h-5 text-white"
            fill="currentColor"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 640 512"
          ><path d="M38.8 5.1C28.4-3.1 13.3-1.2 5.1 9.2S-1.2 34.7 9.2 42.9l592 464c10.4 8.2 25.5 6.3 33.7-4.1s6.3-25.5-4.1-33.7L525.6 386.7c39.6-40.6 66.4-86.1 79.9-118.4c3.3-7.9 3.3-16.7 0-24.6c-14.9-35.7-46.2-87.7-93-131.1C465.5 68.8 400.8 32 320 32c-68.2 0-125 26.3-169.3 60.8L38.8 5.1zM223.1 149.5C248.6 126.2 282.7 112 320 112c79.5 0 144 64.5 144 144c0 24.9-6.3 48.3-17.4 68.7L408 294.5c8.4-19.3 10.6-41.4 4.8-63.3c-11.1-41.5-47.8-69.4-88.6-71.1c-5.8-.2-9.2 6.1-7.4 11.7c2.1 6.4 3.3 13.2 3.3 20.3c0 10.2-2.4 19.8-6.6 28.3l-90.3-70.8zM373 389.9c-16.4 6.5-34.3 10.1-53 10.1c-79.5 0-144-64.5-144-144c0-6.9 .5-13.6 1.4-20.2L83.1 161.5C60.3 191.2 44 220.8 34.5 243.7c-3.3 7.9-3.3 16.7 0 24.6c14.9 35.7 46.2 87.7 93 131.1C174.5 443.2 239.2 480 320 480c47.8 0 89.9-12.9 126.2-32.5L373 389.9z" /></svg>
        </button>
        <!-- Volume -->
        <button class="p-2 bg-gray-700 rounded-full hover:bg-gray-600">
          <svg
            class="w-5 h-5 text-white"
            fill="currentColor"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 640 512"
          ><path d="M533.6 32.5C598.5 85.2 640 165.8 640 256s-41.5 170.7-106.4 223.5c-10.3 8.4-25.4 6.8-33.8-3.5s-6.8-25.4 3.5-33.8C557.5 398.2 592 331.2 592 256s-34.5-142.2-88.7-186.3c-10.3-8.4-11.8-23.5-3.5-33.8s23.5-11.8 33.8-3.5zM473.1 107c43.2 35.2 70.9 88.9 70.9 149s-27.7 113.8-70.9 149c-10.3 8.4-25.4 6.8-33.8-3.5s-6.8-25.4 3.5-33.8C475.3 341.3 496 301.1 496 256s-20.7-85.3-53.2-111.8c-10.3-8.4-11.8-23.5-3.5-33.8s23.5-11.8 33.8-3.5zm-60.5 74.5C434.1 199.1 448 225.9 448 256s-13.9 56.9-35.4 74.5c-10.3 8.4-25.4 6.8-33.8-3.5s-6.8-25.4 3.5-33.8C393.1 284.4 400 271 400 256s-6.9-28.4-17.7-37.3c-10.3-8.4-11.8-23.5-3.5-33.8s23.5-11.8 33.8-3.5zM301.1 34.8C312.6 40 320 51.4 320 64l0 384c0 12.6-7.4 24-18.9 29.2s-25 3.1-34.4-5.3L131.8 352 64 352c-35.3 0-64-28.7-64-64l0-64c0-35.3 28.7-64 64-64l67.8 0L266.7 40.1c9.4-8.4 22.9-10.4 34.4-5.3z" /></svg>
        </button>
        <!-- Playlist -->
        <button class="p-2 bg-gray-700 rounded-full hover:bg-gray-600">
          <svg
            class="w-5 h-5 text-white"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M4 4h16v2H4V4zm0 14h16v2H4v-2zM12 11h8v2h-8v-2z" />
          </svg>
        </button>
        <!-- Queue -->
        <button class="p-2 bg-gray-700 rounded-full hover:bg-gray-600">
          <svg
            class="w-5 h-5 text-white"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M3 3h18v2H3V3zm0 4h18v2H3V7zm0 4h18v2H3v-2zm0 4h18v2H3v-2zm0 4h18v2H3v-2z" />
          </svg>
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>

.custom-fixed {
  position: fixed;
}
</style>
