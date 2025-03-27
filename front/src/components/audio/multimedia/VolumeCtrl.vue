<script setup lang="ts">

import { usePlayer } from '~/composables/audio/player'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTimeoutFn } from '@vueuse/core'
import { VolumeX, Volume1, Volume2, Volume } from 'lucide-vue-next'

const { volume, mute } = usePlayer()
const expanded = ref(false)

const { t } = useI18n()
const labels = computed(() => ({
  unmute: t('components.audio.VolumeControl.button.unmute'),
  mute: t('components.audio.VolumeControl.button.mute'),
  slider: t('components.audio.VolumeControl.label.slider')
}))

const { start, stop } = useTimeoutFn(() => (expanded.value = false), 500, { immediate: false })

const handleOver = () => {
  stop()
  expanded.value = true
}

const handleLeave = () => {
  stop()
  start()
}

const scroll = (event: WheelEvent) => {
  volume.value += -Math.sign(event.deltaY) * 0.05
}

const volumeIcon = computed(() => {
  if (volume.value === 0) return VolumeX
  if (volume.value > 0 && volume.value <= 0.33) return Volume
  if (volume.value > 0.33 && volume.value <= 0.66) return Volume1
  return Volume2
})

</script>

<template>
  <div class="flex items-center gap-1">
    <button
      class="p-2 bg-gray-700 rounded-full hover:bg-gray-600 circular control button"
      :class="['component-volume-control', {'expanded': expanded}]"
      @click.prevent.stop=""
      @mouseover="handleOver"
      @mouseleave="handleLeave"
      @wheel.stop.prevent="scroll"
    >
      <component
        :is="volumeIcon"
        class="w-6 h-6 text-white"
      />
    </button>
    <div
      class="popup"
    >
      <label
        for="volume-slider"
        class="visually-hidden"
      >{{ labels.slider }}</label>
      <input
        id="volume-slider"
        v-model="volume"
        class="cursor-pointer accent-green-500"
        type="range"
        step="any"
        min="0"
        max="1"
      >
    </div>
  </div>
</template>

<style scoped>
</style>
