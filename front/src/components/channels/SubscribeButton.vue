<script setup lang="ts">
import type { Channel } from '~/types'

import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { useStore } from '~/store'

import LoginModal from '~/components/common/LoginModal.vue'

interface Events {
  (e: 'unsubscribed'): void
  (e: 'subscribed'): void
}

interface Props {
  channel: Channel
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const { t } = useI18n()
const store = useStore()

const isSubscribed = computed(() => store.getters['channels/isSubscribed'](props.channel.uuid))
const title = computed(() => isSubscribed.value
  ? 'Unfollow'
  : 'Follow'
)

const message = computed(() => ({
  authMessage: t('components.channels.SubscribeButton.help.auth')
}))

const toggle = async () => {
  await store.dispatch('channels/toggle', props.channel.uuid)

  if (isSubscribed.value) emit('unsubscribed')
  else emit('subscribed')
}

const loginModal = ref()
</script>

<template>
  <button
    v-if="$store.state.auth.authenticated"
    :class="['ui', 'alternative', {'inverted': isSubscribed}, {'favorited': isSubscribed}, 'icon', 'labeled', 'button']"
    @click.stop="toggle"
  >
    <i class="heart icon" />
    {{ title }}
  </button>
  <button
    v-else
    :class="['ui', 'alternative', 'icon', 'labeled', 'button']"
    @click="loginModal.show = true"
  >
    <i class="heart icon" />
    {{ title }}
    <login-modal
      ref="loginModal"
      class="small"
      :next-route="$route.fullPath"
      :message="message.authMessage"
      :cover="channel.artist?.cover!"
      @created="loginModal.show = false"
    />
  </button>
</template>
