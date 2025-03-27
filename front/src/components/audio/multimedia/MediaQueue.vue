<script setup lang="ts">
import { ref } from 'vue'
import draggable from 'vuedraggable'
import { usePlayer } from '~/composables/audio/player'
import { useQueue } from '~/composables/audio/queue'
import { useTracks } from '~/composables/audio/tracks'
import Favorite from '~/components/audio/multimedia/Favorite.vue'

const {
  isPlaying,
  currentTime,
  duration,
  bufferProgress,
  seekTo,
  loading: isLoadingAudio,
  errored
} = usePlayer()

const {
  hasNext,
  currentTrack,
  currentIndex,
  queue,
  dequeue,
  playTrack,
  reorder,
  endsIn,
  clear
} = useQueue()

const { currentSound } = useTracks()

const props = defineProps({
  toggleQueueEvent: {
    type: Function,
    required: true
  }
})

const play = async (index: number) => {
  isPlaying.value = true
  props.toggleQueueEvent()
  return playTrack(index)
}

const reorderTracks = (event: { oldIndex: number, newIndex: number }) => {
  reorder(event.oldIndex, event.newIndex)
}

</script>

<template>
  <div class="bg-gray-900 p-4 text-white w-96">
    <div class="flex justify-between items-center mb-4">
      <div class="">
        <h2 class="text-lg font-semibold">
          Queue
        </h2>
        <p class="text-xs text-gray-300">
          <span>Track {{ currentIndex + 1 }} of {{ queue.length }} </span>
          <span class="middle pipe symbol" />
          <span>Ends {{ endsIn }}</span>
        </p>
      </div>

      <button
        class="bg-red-500 px-3 py-1 rounded"
        @click="clear"
      >
        Clear
      </button>
    </div>
    <ul class="h-full overflow-auto">
      <draggable
        v-model="queue"
        item-key="id"
        class="space-y-2"
        ghost-class="ghost"
        @end="reorderTracks"
      >
        <template #item="{ element, index }">
          <li class="flex items-center justify-between bg-gray-800 p-2 rounded-md shadow">
            <div class="flex items-center space-x-2">
              <span class="text-xl cursor-grab">☰</span>
              <img
                :src="element.coverUrl"
                class="w-10 h-10 rounded cursor-pointer"
              >
              <div
                class="leading-1 cursor-pointer"
                @click="play(index)"
              >
                <p class="font-medium cursor-pointer">
                  {{ element.title }}
                </p>
                <p class="text-sm text-gray-300 cursor-pointer">
                  {{ element.artistName }}
                </p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <Favorite :track="element" />
              <button
                class="p-2 bg-gray-700 rounded-full hover:bg-gray-600"
                @click="dequeue"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="lucide lucide-x"
                ><path d="M18 6 6 18" /><path d="m6 6 12 12" /></svg>
              </button>
            </div>
          </li>
        </template>
      </draggable>
    </ul>
  </div>
</template>

<style scoped>
.ghost {
  opacity: 0.5;
}
</style>
