<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'
import { whenever } from '@vueuse/core'
import SignupForm from '~/components/auth/SignupForm.vue'
import LoginForm from '~/components/auth/LoginForm.vue'
import useLogger from '~/composables/useLogger'

const router = useRouter()
const store = useStore()
const logger = useLogger()
const { t } = useI18n()

// Authentication redirect
whenever(() => store.state.auth.authenticated, () => {
  logger.log('Authenticated, redirecting to /library…')
  router.push('/library')
})

// Modified isArtist watcher
whenever(
  () => store.state.ui.isArtist, 
  (value) => {
    logger.log('isArtist changed to:', value)
  },
  { immediate: true }
)

const isLogin = ref(false)

const toggleForm = () => {
  isLogin.value = !isLogin.value
}

const labels = computed(() => ({
  title: t('views.auth.Login.title')
}))
</script>

<template>
  <div 
    v-title="labels.title"
    class="auth-container min-h-screen flex items-center justify-center"
  >
    <div class="bg-white/10 backdrop-blur-lg rounded-xl p-8 w-full max-w-md shadow-2xl">
      <!-- Header -->
      <div class="text-center mb-8">
        <h2 class="text-3xl font-serif text-white mb-2">
          {{ isLogin ? 'Welcome Back' : 'Join Sacred Sound' }}
        </h2>
        <p class="text-white/80">
          {{ isLogin ? 'Continue your journey' : 'Start your sacred music journey' }}
        </p>
      </div>

      <!-- Form Container -->
      <div class="transition-all duration-300">
        <LoginForm
          v-if="isLogin"
          button-classes="w-full bg-[#5850A9] hover:bg-[#4A4491] text-white py-3 rounded-md transition-colors"
          :show-signup="false"
          next="/mycontent"
        />
        <SignupForm
          v-else
          button-classes="w-full bg-[#5850A9] hover:bg-[#4A4491] text-white py-3 rounded-md transition-colors"
          :show-login="false"
          next="/mycontent"
        />
      </div>

      <!-- Toggle Button -->
      <div class="mt-6 text-center">
        <button
          @click="toggleForm"
          class="text-white/80 hover:text-white transition-colors text-sm"
        >
          {{ isLogin ? 'New to Sacred Sound? Create an account' : 'Already have an account? Log in' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  background: linear-gradient(
    135deg,
    #5850A9 0%,
    #A5C5A9 100%
  );
}

.font-serif {
  font-family: "Playfair Display", serif;
}
</style> 