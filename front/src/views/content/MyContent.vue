<script setup>
import { computed, watch } from 'vue'
import store from '~/store'
import ContentList from '~/components/content/ContentList.vue'

const artistFilter = computed(() => store.state.auth.profile.artist)
</script>

<template>
  <div class="min-h-screen main with-background">
    <main class="container mx-auto px-4 py-8">
      <h1 class="text-4xl mb-8 font-serif">My Content</h1>
      <content-list :artist-filter="artistFilter" />
    </main>
  </div>
</template>

<style>
.main.with-background {
  background: var(--site-background) !important;
}
</style>
