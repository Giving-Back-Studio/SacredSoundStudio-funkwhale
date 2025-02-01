<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const labels = computed(() => ({
  title: t('components.auth.Logout.title')
}))
</script>

<template>
  <main
    v-title="labels.title"
    class="main pusher"
  >
    <section class="ui vertical stripe segment">
      <div
        v-if="$store.state.auth.authenticated"
        class="ui primary small text container"
      >
        <h2 class="ui primary header">
          {{ $t('components.auth.Logout.header.confirm') }}
        </h2>
        <p class="text-primary">
          {{ $t('components.auth.Logout.message.loggedIn', { username: $store.state.auth.username }) }}
        </p>
        <button
          class="ui primary button"
          @click="$store.dispatch('auth/logout')"
        >
          {{ $t('components.auth.Logout.button.logout') }}
        </button>
      </div>
      <div
        v-else
        class="ui primary small text container"
      >
        <h2 class="ui primary header">
          {{ $t('components.auth.Logout.header.unauthenticated') }}
        </h2>
        <router-link
          to="/auth"
          class="ui primary button"
        >
          {{ $t('components.auth.Logout.link.login') }}
        </router-link>
      </div>
    </section>
  </main>
</template>
