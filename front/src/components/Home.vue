<script setup lang="ts">
import { ref } from 'vue'
import { MusicIcon, UsersIcon, GraduationCapIcon } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useStore } from '~/store'
import { whenever } from '@vueuse/core'
import useLogger from '~/composables/useLogger'

// Authentication setup
const router = useRouter()
const store = useStore()
const logger = useLogger()

whenever(() => store.state.auth.authenticated, () => {
  logger.log('Authenticated, redirecting to /library…')
  router.push('/library')
})

const navigateToAuth = () => {
  try {
    logger.log('Setting isArtist to true...')
    store.commit('ui/setIsArtist', true)
    logger.log('Navigating to /auth...')
    
    // Use router.replace instead of push and remove setTimeout
    router.replace('/auth').catch(error => {
      logger.error('Navigation error:', error)
    })
  } catch (error) {
    logger.error('Navigation error:', error)
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#F1F4F8]">
    <!-- Hero Section -->
    <header class="relative h-screen min-h-[600px] overflow-hidden">
      <img 
        :src="'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Image-ZbMIUxZdtR8zNg0ssDa7KOyZNW1iFC.png'" 
        alt="Sacred gongs in a meditation space"
        class="absolute inset-0 w-full h-full object-cover"
      />
      <div class="absolute inset-0 bg-black/40">
        <nav class="container mx-auto px-4 py-6">
          <div class="flex items-center justify-between">
            <img 
              :src="'https://hebbkx1anhila5yf.public.blob.vercel-storage.com/SS-Logo-xFTJTuPTR704RYU0yrafPlvc9iJuF0.png'" 
              alt="Sacred Sound Logo" 
              class="h-20 w-60"
            />
            <button 
              @click="navigateToAuth"
              class="bg-[#5850A9] hover:bg-[#4A4491] px-6 py-2 text-white rounded-md transition-colors"
            >
              Join Now
            </button>
          </div>
        </nav>
        <div class="container mx-auto px-4 h-full flex items-center justify-center text-center">
          <div class="max-w-3xl">
            <h1 class="text-5xl md:text-6xl font-serif text-white mb-4">
              Resonate with higher vibrations.
            </h1>
            <p class="text-xl text-white/90 mb-8">
              Connect with sacred music and artists that inspire you.
            </p>
            <button 
              @click="navigateToAuth"
              class="bg-[#5850A9] hover:bg-[#4A4491] px-8 py-3 text-white rounded-md transition-colors"
            >
              JOIN THE PLATFORM
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main>
      <!-- Features Section -->
      <section class="py-20">
        <div class="container mx-auto px-4">
          <h2 class="text-4xl md:text-5xl font-serif text-[#5850A9] text-center mb-16">
            It's time to elevate sacred music together.
          </h2>
          
          <div class="grid md:grid-cols-3 gap-12">
            <div>
              <h3 class="text-2xl font-serif text-[#5850A9] mb-4">Discover</h3>
              <p class="text-gray-600">
                Immerse yourself in a curated collection of transformative sacred music from diverse artists.
              </p>
            </div>
            <div>
              <h3 class="text-2xl font-serif text-[#5850A9] mb-4">Connect</h3>
              <p class="text-gray-600">
                Engage with fellow community members, share insights, and foster connections in a supportive space.
              </p>
            </div>
            <div>
              <h3 class="text-2xl font-serif text-[#5850A9] mb-4">Elevate</h3>
              <p class="text-gray-600">
                Unlock premium content, live sessions, and behind-the-scenes experiences.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Community Section -->
      <section class="py-20">
        <div class="container mx-auto px-4">
          <div class="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 class="text-4xl font-serif text-[#5850A9] mb-6">
                Join the Sacred Sound Community
              </h2>
              <p class="text-gray-600 mb-6">
                We understand what it's like to long for a better way to connect with sacred music. We are creating a space that raises the vibration of humanity through quality and diverse sacred music, and intimate connection with artists.
              </p>
            </div>
            <div class="bg-black rounded-lg aspect-video">
              <video 
                class="w-full h-full rounded-lg"
                controls
                :src="'Sacred-Sound-Explainer-Video.mp4'"
              ></video>
            </div>
          </div>
        </div>
      </section>

      <!-- Sanctuary Section -->
      <section class="bg-[#A5C5A9] py-20">
        <div class="container mx-auto px-4">
          <div class="grid md:grid-cols-2 gap-12">
            <div>
              <h2 class="text-4xl font-serif text-white mb-4">
                Your Spiritual Sanctuary
              </h2>
              <p class="text-white/90">
                Designed to inspire high vibrations.
              </p>
            </div>
            <div class="space-y-8">
              <div>
                <h3 class="flex items-center text-2xl font-serif text-white mb-2">
                  <MusicIcon class="h-6 w-6 mr-2" />
                  For sacred music seekers
                </h3>
                <p class="text-white/90">
                  Discover new music and enjoy mindfully curated content on Sacred Sound's library and online concert hall.
                </p>
              </div>
              <div>
                <h3 class="flex items-center text-2xl font-serif text-white mb-2">
                  <UsersIcon class="h-6 w-6 mr-2" />
                  For workshop leaders
                </h3>
                <p class="text-white/90">
                  Enhance your next offering with our expansive library of meditations, sound journeys, and even DJ sets.
                </p>
              </div>
              <div>
                <h3 class="flex items-center text-2xl font-serif text-white mb-2">
                  <GraduationCapIcon class="h-6 w-6 mr-2" />
                  For students and emerging artists
                </h3>
                <p class="text-white/90">
                  Develop your craft by connecting with lessons, offerings, and events created by the artists who inspire you.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Join Section -->
      <section class="py-20">
        <div class="container mx-auto px-4 max-w-xl text-center">
          <h2 class="text-4xl font-serif text-[#5850A9] mb-12">
            Join Sacred Sound Today
          </h2>
          <button 
            @click="navigateToAuth"
            class="bg-[#5850A9] hover:bg-[#4A4491] px-8 py-3 text-white rounded-md transition-colors"
          >
            GET STARTED
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.font-serif {
  font-family: "Playfair Display", serif;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}

/* Smooth transitions */
.transition-colors {
  transition: all 0.3s ease;
}
</style>