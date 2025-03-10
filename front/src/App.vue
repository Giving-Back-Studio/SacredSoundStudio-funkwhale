<script setup lang="ts">
import type { QueueTrack } from '~/composables/audio/queue'

import { useIntervalFn, useStyleTag, useToggle, useWindowSize } from '@vueuse/core'
import { computed, nextTick, onMounted, ref, watchEffect, defineAsyncComponent } from 'vue'

import { useQueue } from '~/composables/audio/queue'
import { useStore } from '~/store'

import onKeyboardShortcut from '~/composables/onKeyboardShortcut'
import useLogger from '~/composables/useLogger'

const ChannelUploadModal = defineAsyncComponent(() => import('~/components/channels/UploadModal.vue'))
const PlaylistModal = defineAsyncComponent(() => import('~/components/playlists/PlaylistModal.vue'))
const FilterModal = defineAsyncComponent(() => import('~/components/moderation/FilterModal.vue'))
const ReportModal = defineAsyncComponent(() => import('~/components/moderation/ReportModal.vue'))
const SetInstanceModal = defineAsyncComponent(() => import('~/components/SetInstanceModal.vue'))
const ServiceMessages = defineAsyncComponent(() => import('~/components/ServiceMessages.vue'))
const ShortcutsModal = defineAsyncComponent(() => import('~/components/ShortcutsModal.vue'))
const AudioPlayer = defineAsyncComponent(() => import('~/components/audio/Player.vue'))
const Sidebar = defineAsyncComponent(() => import('~/components/Sidebar.vue'))
const Queue = defineAsyncComponent(() => import('~/components/Queue.vue'))

const logger = useLogger()
logger.debug('App setup()')

const store = useStore()

// Tracks
const { currentTrack, tracks } = useQueue()
const getTrackInformationText = (track: QueueTrack | undefined) => {
  if (!track) {
    return null
  }

  return `♫ ${track.title} – ${track.artistName} ♫`
}

// Update title
const initialTitle = document.title
watchEffect(() => {
  const parts = [
    getTrackInformationText(currentTrack.value),
    store.state.ui.pageTitle,
    initialTitle || 'Funkwhale'
  ]

  document.title = parts.filter(i => i).join(' – ')
})

// Styles
const customStylesheets = computed(() => {
  return store.state.instance.frontSettings.additionalStylesheets ?? []
})

useStyleTag(computed(() => store.state.instance.settings.ui.custom_css.value))

// Fake content
onMounted(async () => {
  await nextTick()
  document.getElementById('fake-content')?.classList.add('loaded')
})

// Time ago
useIntervalFn(() => {
  // used to redraw ago dates every minute
  store.commit('ui/computeLastDate')
}, 1000 * 60)

// Shortcuts
const [showShortcutsModal, toggleShortcutsModal] = useToggle(false)
onKeyboardShortcut('h', () => toggleShortcutsModal())

const { width } = useWindowSize()
const showSetInstanceModal = ref(false)

// Fetch user data on startup
// NOTE: We're not checking if we're authenticated in the store,
//       because we want to learn if we are authenticated at all
store.dispatch('auth/fetchUser')

const isSidebarCollapsed = ref(false)

const handleSidebarCollapse = (collapsed: boolean) => {
  isSidebarCollapsed.value = collapsed
}
</script>

<template>
  <div
    :key="store.state.instance.instanceUrl"
    :class="{
      'has-bottom-player': tracks.length > 0,
      'queue-focused': store.state.ui.queueFocused
    }"
  >
    <!-- here, we display custom stylesheets, if any -->
    <link
      v-for="url in customStylesheets"
      :key="url"
      rel="stylesheet"
      property="stylesheet"
      :href="url"
    >

    <sidebar @update:collapsed="handleSidebarCollapse" :width="width" />
    <main id="main" :class="['main', 'pusher', { 'sidebar-collapsed': isSidebarCollapsed }, { 'small': width < 1024}]">
      <set-instance-modal v-model:show="showSetInstanceModal" />
      <service-messages />
      <transition name="queue">
        <queue v-show="store.state.ui.queueFocused" />
      </transition>

      <router-view v-slot="{ Component }">
        <template v-if="Component">
          <keep-alive :max="1">
            <Suspense>
              <component :is="Component" />
              <template #fallback>
                <!-- TODO (wvffle): Add loader -->
                {{ $t('App.loading') }}
              </template>
            </Suspense>
          </keep-alive>
        </template>
      </router-view>
    </main>

    <audio-player />
    <playlist-modal v-if="store.state.auth.authenticated" />
    <channel-upload-modal v-if="store.state.auth.authenticated" />
    <filter-modal v-if="store.state.auth.authenticated" />
    <report-modal />
    <shortcuts-modal v-model:show="showShortcutsModal" />
  </div>
</template>
