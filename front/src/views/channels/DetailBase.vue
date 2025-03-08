<template>
  <main v-title="labels.title" class="ui inverted segment">
    <div v-if="isLoading" class="ui basic segment">
      <div class="ui active centered inline loader"></div>
    </div>
    <template v-if="object && !isLoading">
      <!-- Hero Section with Banner and Profile -->
      <div class="ui grid">
        <!-- Banner Image -->
        <div class="sixteen wide column">
          <div class="ui fluid image">
            <img 
              v-if="object.artist?.cover"
              :src="$store.getters['instance/absoluteUrl'](object.artist.cover.urls.original)"
              :alt="object.artist?.name"
              class="ui image"
            >
            <div v-else class="ui placeholder"></div>
          </div>
        </div>

        <!-- Profile Section -->
        <div class="sixteen wide column">
          <div class="ui basic segment">

            <!-- Artist Info -->
            <div class="ui inverted">
              <h1 class="ui huge header">{{ object.artist?.name }}</h1>

              <!-- Action Buttons -->
              <play-button
                :is-playable="isPlayable"
                class="ui primary button"
                style="margin-right: 0.25rem"
                :artist="object.artist"
              >
                {{ $t('views.channels.DetailBase.button.play') }}
              </play-button>

              <subscribe-button
                :channel="object"
                @subscribed="updateSubscriptionCount(1)"
                @unsubscribed="updateSubscriptionCount(-1)"
              />

              <router-link v-if="isOwner" to="/mychannel" class="ui icon labeled button">
                <i class="edit icon" />
                Edit My Channel
              </router-link>
            </div>
          </div>

          <!-- Description -->
          <div class="ui basic segment" v-if="$store.getters['ui/layoutVersion'] === 'large'">
            <rendered-description
              :content="object.artist?.description"
              :update-url="`channels/${object.uuid}/`"
              :can-update="false"
              @updated="object = $event"
            />
          </div>

          <!-- Tags -->
          <div class="ui basic segment">
            <tags-list
              v-if="object.artist?.tags && object.artist?.tags.length > 0"
              :tags="object.artist.tags"
              class="ui labels"
            />
          </div>

          <!-- Navigation -->
          <div class="ui secondary pointing menu">
            <router-link
              class="item"
              :class="{'active': $route.name === 'channels.detail'}"
              :to="{name: 'channels.detail', params: {id: id}}"
            >
              {{ $t('views.channels.DetailBase.link.channelOverview') }}
            </router-link>
            <router-link
              class="item"
              :class="{'active': $route.name === 'channels.detail.episodes'}"
              :to="{name: 'channels.detail.episodes', params: {id: id}}"
            >
              <span v-if="isPodcast">
                {{ $t('views.channels.DetailBase.link.channelEpisodes') }}
              </span>
              <span v-else>
                {{ $t('views.channels.DetailBase.link.channelTracks') }}
              </span>
            </router-link>
          </div>

          <!-- Content -->
          <div class="ui basic segment">
            <router-view
              v-if="object"
              :object="object"
              @tracks-loaded="totalTracks = $event"
            />
          </div>
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
