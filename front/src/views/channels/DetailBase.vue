<template>
  <main
    v-title="labels.title"
    class="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white"
  >
    <div
      v-if="isLoading"
      class="flex justify-center items-center py-8"
    >
      <div class="ui centered active inline loader" />
    </div>
    <template v-if="object && !isLoading">
      <!-- Hero Section with Banner and Profile -->
      <div class="relative">
        <!-- Banner Image -->
        <div class="relative w-full h-[300px] md:h-[400px]">
          <img 
            v-if="object.artist?.cover"
            :src="$store.getters['instance/absoluteUrl'](object.artist.cover.urls.original)"
            :alt="object.artist?.name"
            class="w-full h-full object-cover"
          >
          <div v-else class="w-full h-full bg-gray-800" />
          <div class="absolute inset-0 bg-gradient-to-b from-transparent to-gray-900"></div>
        </div>

        <!-- Profile Section -->
        <div class="container mx-auto px-4">
          <div class="relative -mt-24 md:-mt-32 flex flex-col md:flex-row items-start md:items-end gap-6 mb-8">
            <!-- Profile Image -->
            <div class="w-32 h-32 md:w-48 md:h-48 rounded-full overflow-hidden border-4 border-gray-900 shrink-0">
              <img 
                v-if="object.artist?.cover"
                :src="$store.getters['instance/absoluteUrl'](object.artist.cover.urls.medium_square_crop)"
                :alt="object.artist?.name"
                class="w-full h-full object-cover"
              >
              <i
                v-else
                class="huge circular inverted users violet icon"
              />
            </div>

            <!-- Artist Info -->
            <div class="flex-grow">
              <h1 class="text-3xl md:text-4xl font-bold mb-2">{{ object.artist?.name }}</h1>

              <!-- Stats -->
              <div class="mt-4 flex flex-wrap gap-4 text-gray-400">
                <template v-if="totalTracks > 0">
                  <span v-if="isPodcast">
                    {{ $t('views.channels.DetailBase.meta.episodes', totalTracks) }}
                  </span>
                  <span v-else>
                    {{ $t('views.channels.DetailBase.meta.tracks', totalTracks) }}
                  </span>
                </template>
              </div>

              <!-- Action Buttons -->
              <div class="mt-6 flex flex-wrap gap-4">
                <play-button
                  :is-playable="isPlayable"
                  class="px-6 py-2 bg-primary text-black rounded-full hover:bg-gray-200 transition-colors flex items-center gap-2"
                  :artist="object.artist"
                >
                  {{ $t('views.channels.DetailBase.button.play') }}
                </play-button>

                <subscribe-button
                  :channel="object"
                  class="px-6 py-2 bg-white text-black rounded-full hover:bg-gray-200 transition-colors"
                  @subscribed="updateSubscriptionCount(1)"
                  @unsubscribed="updateSubscriptionCount(-1)"
                />

                <!-- More Actions Dropdown -->
                <button
                  ref="dropdown"
                  v-dropdown="{direction: 'downward'}"
                  class="px-6 py-2 bg-gray-800 text-white rounded-full hover:bg-gray-700 transition-colors"
                >
                  <i class="ellipsis vertical icon" />
                  <div class="menu">
                    <a
                      v-for="obj in getReportableObjects({account: object.attributed_to, channel: object})"
                      :key="obj.target.type + obj.target.id"
                      href=""
                      class="basic item"
                      @click.stop.prevent="report(obj)"
                    >
                      <i class="share icon" /> {{ obj.label }}
                    </a>

                    <template v-if="isOwner">
                      <div class="divider" />
                      <a
                        class="item"
                        href=""
                        @click.stop.prevent="showEditModal = true"
                      >
                        <i class="edit icon" />
                        {{ $t('views.channels.DetailBase.button.edit') }}
                      </a>
                    </template>
                    <template v-if="$store.state.auth.availablePermissions['library']">
                      <div class="divider" />
                      <router-link
                        class="basic item"
                        :to="{name: 'manage.channels.detail', params: {id: object.uuid}}"
                      >
                        <i class="wrench icon" />
                        {{ $t('views.channels.DetailBase.link.moderation') }}
                      </router-link>
                    </template>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <!-- Description -->
          <div class="max-w-3xl mb-12" v-if="$store.getters['ui/layoutVersion'] === 'large'">
            <rendered-description
              :content="object.artist?.description"
              :update-url="`channels/${object.uuid}/`"
              :can-update="false"
              @updated="object = $event"
            />
          </div>

          <!-- Tags -->
          <div class="mb-8">
            <tags-list
              v-if="object.artist?.tags && object.artist?.tags.length > 0"
              :tags="object.artist.tags"
              class="flex flex-wrap gap-2"
            />
          </div>

          <!-- Navigation -->
          <div class="mb-8">
            <nav class="flex justify-center border-b border-gray-800">
              <router-link
                class="px-6 py-3 text-gray-400 hover:text-white transition-colors border-b-2 border-transparent"
                :class="{'border-white text-white': $route.name === 'channels.detail'}"
                :to="{name: 'channels.detail', params: {id: id}}"
              >
                {{ $t('views.channels.DetailBase.link.channelOverview') }}
              </router-link>
              <router-link
                class="px-6 py-3 text-gray-400 hover:text-white transition-colors border-b-2 border-transparent"
                :class="{'border-white text-white': $route.name === 'channels.detail.episodes'}"
                :to="{name: 'channels.detail.episodes', params: {id: id}}"
              >
                <span v-if="isPodcast">
                  {{ $t('views.channels.DetailBase.link.channelEpisodes') }}
                </span>
                <span v-else>
                  {{ $t('views.channels.DetailBase.link.channelTracks') }}
                </span>
              </router-link>
            </nav>
          </div>

          <!-- Content -->
          <router-view
            v-if="object"
            :object="object"
            @tracks-loaded="totalTracks = $event"
          />
        </div>
      </div>
    </template>

    <!-- Modals -->
    <semantic-modal
      v-model:show="showSubscribeModal"
      class="tiny"
    >
      <h4 class="header">
        {{ $t('views.channels.DetailBase.modal.subscribe.header') }}
      </h4>
      <div class="scrollable content">
        <div class="description">
          <template v-if="$store.state.auth.authenticated">
            <h3>
              <i class="user icon" />
              {{ $t('views.channels.DetailBase.modal.subscribe.funkwhale.header') }}
            </h3>
            <subscribe-button
              :channel="object"
              @subscribed="updateSubscriptionCount(1)"
              @unsubscribed="updateSubscriptionCount(-1)"
            />
          </template>
          <template v-if="object.rss_url">
            <h3>
              <i class="feed icon" />
              {{ $t('views.channels.DetailBase.modal.subscribe.rss.header') }}
            </h3>
            <p>
              {{ $t('views.channels.DetailBase.modal.subscribe.rss.content.help') }}
            </p>
            <copy-input :value="object.rss_url" />
          </template>
          <template v-if="object.actor">
            <h3>
              <i class="bell icon" />
              {{ $t('views.channels.DetailBase.modal.subscribe.fediverse.header') }}
            </h3>
            <p>
              {{ $t('views.channels.DetailBase.modal.subscribe.fediverse.content.help') }}
            </p>
            <copy-input
              id="copy-tag"
              :value="`@${object.actor.full_username}`"
            />
          </template>
        </div>
      </div>
      <div class="actions">
        <button class="ui basic deny button">
          {{ $t('views.channels.DetailBase.button.cancel') }}
        </button>
      </div>
    </semantic-modal>

    <semantic-modal
      v-if="totalTracks > 0"
      v-model:show="showEmbedModal"
    >
      <h4 class="header">
        {{ $t('views.channels.DetailBase.modal.embed.header') }}
      </h4>
      <div class="scrolling content">
        <div class="description">
          <embed-wizard
            :id="object.artist!.id"
            type="artist"
          />
        </div>
      </div>
      <div class="actions">
        <button class="ui basic deny button">
          {{ $t('views.channels.DetailBase.button.cancel') }}
        </button>
      </div>
    </semantic-modal>

    <semantic-modal
      v-if="isOwner"
      v-model:show="showEditModal"
    >
      <h4 class="header">
        <span v-if="object.artist?.content_category === 'podcast'">
          {{ $t('views.channels.DetailBase.header.podcastChannel') }}
        </span>
        <span v-else>
          {{ $t('views.channels.DetailBase.header.artistChannel') }}
        </span>
      </h4>
      <div class="scrolling content">
        <channel-form
          ref="editForm"
          :object="object"
          @loading="edit.loading = $event"
          @submittable="edit.submittable = $event"
          @updated="fetchData"
        />
        <div class="ui hidden divider" />
      </div>
      <div class="actions">
        <button class="ui left floated basic deny button">
          {{ $t('views.channels.DetailBase.button.cancel') }}
        </button>
        <button
          :class="['ui', 'primary', 'confirm', {loading: edit.loading}, 'button']"
          :disabled="!edit.submittable"
          @click.stop="editForm?.submit"
        >
          {{ $t('views.channels.DetailBase.button.updateChannel') }}
        </button>
      </div>
    </semantic-modal>
  </main>
</template>

<script setup lang="ts">
import type { Channel } from '~/types'

import { onBeforeRouteUpdate, useRoute, useRouter } from 'vue-router'
import { computed, ref, reactive, watch, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'

import axios from 'axios'

import SubscribeButton from '~/components/channels/SubscribeButton.vue'
import ChannelForm from '~/components/audio/ChannelForm.vue'
import EmbedWizard from '~/components/audio/EmbedWizard.vue'
import SemanticModal from '~/components/semantic/Modal.vue'
import PlayButton from '~/components/audio/PlayButton.vue'
import TagsList from '~/components/tags/List.vue'

import useErrorHandler from '~/composables/useErrorHandler'
import useReport from '~/composables/moderation/useReport'

interface Events {
  (e: 'deleted'): void
}

interface Props {
  id: number
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()
const { report, getReportableObjects } = useReport()
const store = useStore()

const object = ref<Channel | null>(null)
const editForm = ref()
const totalTracks = ref(0)

const edit = reactive({
  submittable: false,
  loading: false
})

const showEmbedModal = ref(false)
const showEditModal = ref(false)
const showSubscribeModal = ref(false)

const isOwner = computed(() => store.state.auth.authenticated && object.value?.attributed_to.full_username === store.state.auth.fullUsername)
const isPodcast = computed(() => object.value?.artist?.content_category === 'podcast')
const isPlayable = computed(() => totalTracks.value > 0)

const { t } = useI18n()
const labels = computed(() => ({
  title: t('views.channels.DetailBase.title')
}))

onBeforeRouteUpdate((to) => {
  to.meta.preserveScrollPosition = true
})

const router = useRouter()
const isLoading = ref(false)
const fetchData = async () => {
  showEditModal.value = false
  edit.loading = false
  isLoading.value = true

  try {
    const response = await axios.get(`channels/${props.id}`, { params: { refresh: 'true' } })
    object.value = response.data
    totalTracks.value = response.data.artist.tracks_count

    if (props.id === response.data.uuid && response.data.actor) {
      // replace with the pretty channel url if possible
      const actor = response.data.actor
      if (actor.is_local) {
        await router.replace({ name: 'channels.detail', params: { id: actor.preferred_username } })
      } else {
        await router.replace({ name: 'channels.detail', params: { id: actor.full_username } })
      }
    }
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false
}

watch(() => props.id, fetchData, { immediate: true })

const uuid = computed(() => store.state.channels.latestPublication?.channel.uuid)
watch([uuid, object], ([uuid, object], [lastUuid, lastObject]) => {
  if (object?.uuid && object.uuid === lastObject?.uuid) return

  if (uuid && uuid === object?.uuid) {
    fetchData()
  }
})

const route = useRoute()
watchEffect(() => {
  if (!object.value) return
  if (!store.state.auth.authenticated && store.getters['instance/domain'] !== object.value.actor.domain) {
    router.push({ name: 'login', query: { next: route.fullPath } })
  }
})

const remove = async () => {
  isLoading.value = true
  try {
    await axios.delete(`channels/${object.value?.uuid}`)
    emit('deleted')
    return router.push({ name: 'profile.overview', params: { username: store.state.auth.username } })
  } catch (error) {
    useErrorHandler(error as Error)
  }
}

const updateSubscriptionCount = (delta: number) => {
  if (object.value) {
    object.value.subscriptions_count += delta
  }
}
</script>
