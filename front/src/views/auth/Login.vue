<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'

import LoginForm from '~/components/auth/LoginForm.vue'
import { useRouter } from 'vue-router'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from '~/store'
import { whenever } from '@vueuse/core'

interface Props {
  next?: RouteLocationRaw
}

const props = withDefaults(defineProps<Props>(), {
  next: '/search'
})

const { t } = useI18n()
const labels = computed(() => ({
  title: t('views.auth.Login.title')
}))

const store = useStore()
const router = useRouter()
whenever(() => store.state.auth.authenticated, () => {
  const resolved = router.resolve(props.next)
  router.push(resolved.name === '404' ? '/search' : props.next)
})
</script>

<template>
  <main
    v-title="labels.title"
    class="main pusher"
  >
    <section class="ui vertical stripe segment">
      <div class="ui small text container">
        <h2>
          {{ $t('views.auth.Login.header.login') }}
        </h2>
        <login-form :next="next" />
      </div>
    </section>
  </main>
</template>
