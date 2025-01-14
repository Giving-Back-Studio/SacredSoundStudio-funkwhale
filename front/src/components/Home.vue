<script setup lang="ts">
import { get } from 'lodash-es'
import AlbumWidget from '~/components/audio/album/Widget.vue'
import ChannelsWidget from '~/components/audio/ChannelsWidget.vue'
import LoginForm from '~/components/auth/LoginForm.vue'
import SignupForm from '~/components/auth/SignupForm.vue'
import useMarkdown from '~/composables/useMarkdown'
import useLogger from '~/composables/useLogger'
import { humanSize } from '~/utils/filters'
import { useStore } from '~/store'
import { computed } from 'vue'
import { whenever } from '@vueuse/core'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.Home.title')
}))

const store = useStore()
const logger = useLogger()
const nodeinfo = computed(() => store.state.instance.nodeinfo)

const podName = computed(() => get(nodeinfo.value, 'metadata.nodeName') || 'Funkwhale')
const banner = computed(() => get(nodeinfo.value, 'metadata.banner'))
const shortDescription = computed(() => get(nodeinfo.value, 'metadata.shortDescription'))

const headerStyle = computed(() => {
  if (!banner.value) {
    return ''
  }

  return {
    backgroundImage: `url(${store.getters['instance/absoluteUrl'](banner.value)})`
  }
})

// TODO (wvffle): Check if needed
const router = useRouter()
whenever(() => store.state.auth.authenticated, () => {
  logger.log('Authenticated, redirecting to /library…')
  router.push('/library')
})
</script>

<template>
  <main
    v-title="labels.title"
    class="main pusher page-home"
  >
    <section
      :class="['ui', 'head', {'with-background': banner}, 'vertical', 'center', 'aligned', 'stripe', 'segment']"
      :style="headerStyle"
    >
      <div class="segment-content">
        <h1 class="ui center aligned large header">
          <span>
            {{ $t('components.Home.header.welcome', {podName: podName}) }}
          </span>
          <div
            v-if="shortDescription"
            class="sub header"
          >
            {{ shortDescription }}
          </div>
        </h1>
      </div>
    </section>
    <section class="ui vertical stripe segment">
        <div class="four wide column">
          <h3 class="header">
            {{ $t('components.Home.header.login') }}
          </h3>
          <login-form
            button-classes="success"
            :show-signup="false"
          />
          <div class="ui hidden clearing divider" />
        </div>
    </section>
  </main>
</template>
