<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { UsersIcon, MusicIcon, HeartIcon, ChevronDownIcon } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useStore } from '~/store'
import { whenever } from '@vueuse/core'
import useLogger from '~/composables/useLogger'

// Authentication setup
const router = useRouter()
const store = useStore()
const logger = useLogger()

// Set up meta information
const pageTitle = 'Amplify Abundance - Sacred Sound Artist Platform'
const pageDescription = 'Connect intimately with listeners that go deep. Join Sacred Sound to share your sacred music and receive support from listeners you inspire.'

onMounted(() => {
  // Update document title
  document.title = pageTitle
  
  // Update meta tags programmatically
  const updateMetaTag = (name: string, content: string) => {
    let meta = document.querySelector(`meta[name="${name}"]`) ||
               document.querySelector(`meta[property="${name}"]`)
    if (!meta) {
      meta = document.createElement('meta')
      meta.setAttribute(name.includes('og:') ? 'property' : 'name', name)
      document.head.appendChild(meta)
    }
    meta.setAttribute('content', content)
  }

  updateMetaTag('description', pageDescription)
  updateMetaTag('og:title', pageTitle)
  updateMetaTag('og:description', pageDescription)
})

whenever(() => store.state.auth.authenticated, () => {
  logger.log('Authenticated, redirecting to /mycontent')
  router.push('/mycontent')
})

// FAQ functionality
const openFaq = ref(null)

const toggleFaq = (index) => {
  openFaq.value = openFaq.value === index ? null : index
}

const faqs = [
  {
    question: "What forms of content do you accept?",
    answer: "We accept studio recordings, music videos, meditations, video lessons, behind the scenes, and live concerts. For more information, check out our QA Guidelines."
  },
  {
    question: "What are Thanks coins and how can I use them?",
    answer: "Thanks coins are our platform's token system that listeners can award to artists. These can be redeemed for studio services and other benefits."
  },
  {
    question: "Will I get paid for music streamed on Sacred Sound?",
    answer: "Yes, artists receive compensation for every minute their content is streamed on our platform."
  }
]

const navigateToAuth = () => {
  try {
    logger.log('Setting isArtist to true...')
    store.commit('ui/setIsArtist', true)
    logger.log('Navigating to /auth...')
    
    // Force navigation to happen in the next tick
    setTimeout(() => {
      router.push({ 
        path: '/auth',
        query: { isArtist: 'true' },
        replace: true
      }).catch(error => {
        logger.error('Navigation error:', error)
      })
    }, 0)
  } catch (error) {
    logger.error('Navigation error:', error)
  }
}
</script>

<template>
  <div class="min-h-screen bg-black text-white">
    <!-- Hero Section -->
    <header class="relative h-screen min-h-[600px] overflow-hidden">
      <img 
        src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Rectangle%2019-gi2ntXIbZzkfFGdI8gl0c8G4dZ7vMD.png"
        alt="Sacred instrument being played"
        class="absolute inset-0 w-full h-full object-cover"
      />
      <div class="absolute inset-0 bg-black/50">
        <nav class="container mx-auto px-4 py-6">
          <div class="flex items-center">
            <img src="/android-chrome-192x192.png" alt="Sacred Sound Logo" class="h-20" />
            <h3 class="text-white text-xl">Sacred Sound</h3>
          </div>
        </nav>
        <div class="container mx-auto px-4 h-full flex items-center">
          <div class="max-w-2xl">
            <h1 class="text-5xl md:text-6xl font-serif mb-4">Amplify Abundance</h1>
            <p class="text-xl mb-8">Connect intimately with listeners that go deep.</p>
            <button 
              @click="navigateToAuth"
              class="bg-[#1c8085] hover:bg-[#e5f1f2] px-8 py-3 rounded-md transition-colors"
            >
              GET STARTED
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Platform Introduction -->
    <section class="py-20 bg-white">
      <div class="container mx-auto px-4">
        <div class="grid md:grid-cols-2 gap-12 items-center">
          <div class="text-black">
            <h2 class="text-4xl font-serif mb-6 text-[#1c8085]">
              A platform designed for your journey as a sacred music artist.
            </h2>
            <p class="text-gray-600">
              We pay artists directly and provide professional support to enhance the value of what you create.
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

    <!-- Cloud Studio Section -->
    <section class="py-20 bg-[#e5f1f2]">
      <div class="container mx-auto px-4">
        <div class="grid md:grid-cols-2 gap-12">
          <div class="bg-[#1c8085] p-12 rounded-lg">
            <h2 class="text-4xl font-serif text-white mb-4">
              Welcome to Your<br/>
              <em>Cloud Studio</em>
            </h2>
            <p class="text-white/90">
              A platform for new cash flow streams, direct connection to listeners, and professional studio support from Sacred Sound Studios.
            </p>
          </div>
          <div class="space-y-8 text-black">
            <div>
              <h3 class="text-2xl font-serif text-[#1c8085] mb-2">Create new revenue streams with your content.</h3>
              <p class="text-gray-600">Upload your magic into our sacred music library and get paid for every minute of content that gets viewed.</p>
            </div>
            <div>
              <h3 class="text-2xl font-serif text-[#1c8085] mb-2">Expand through more intimate connection.</h3>
              <p class="text-gray-600">Invite your listeners along deeper into your creative process through video lessons, events, behind the scenes, and more!</p>
            </div>
            <div>
              <h3 class="text-2xl font-serif text-[#1c8085] mb-2">Earn professional studio support through your music.</h3>
              <p class="text-gray-600">Gain tokens, Thanks coins, directly from listeners as they gain inspiration, which you can redeem for studio services.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-20 bg-white text-black">
      <div class="container mx-auto px-4">
        <h2 class="text-4xl font-serif text-center text-[#1c8085] mb-4">Let's Create Magic Together</h2>
        <p class="text-center text-gray-600 mb-12">Share sacred music and receive support from listeners you inspire.</p>
        
        <div class="grid md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="mb-4 flex justify-center">
              <UsersIcon class="h-12 w-12 text-[#1c8085]" />
            </div>
            <h3 class="text-xl font-serif text-[#1c8085] mb-2">Join the Artist Collective</h3>
            <p class="text-gray-600">Be one of up to 100 artists selected to join the Sacred Sound Artist Collective.</p>
          </div>
          
          <div class="text-center">
            <div class="mb-4 flex justify-center">
              <MusicIcon class="h-12 w-12 text-[#1c8085]" />
            </div>
            <h3 class="text-xl font-serif text-[#1c8085] mb-2">Publish Your Magic</h3>
            <p class="text-gray-600">Reach the right audience for you and get paid for every minute of content that gets viewed.</p>
          </div>
          
          <div class="text-center">
            <div class="mb-4 flex justify-center">
              <HeartIcon class="h-12 w-12 text-[#1c8085]" />
            </div>
            <h3 class="text-xl font-serif text-[#1c8085] mb-2">Get Support</h3>
            <p class="text-gray-600">Unlock studio time and services to continue enhancing the potency of every item that you publish.</p>
          </div>
        </div>

        <div class="text-center mt-12">
          <button 
            @click="navigateToAuth"
            class="bg-[#1c8085] text-white hover:bg-[#e5f1f2] px-8 py-3 rounded-md transition-colors"
          >
            GET STARTED
          </button>
        </div>
      </div>
    </section>

    <!-- FAQ Section -->
    <section class="py-20 bg-gray-50">
      <div class="container mx-auto px-4">
        <h2 class="text-4xl font-serif text-center text-[#1c8085] mb-12">FAQ</h2>
        
        <div class="max-w-2xl mx-auto space-y-4">
          <div v-for="(item, index) in faqs" :key="index" class="border-b border-gray-200">
            <button
              class="w-full py-4 text-left text-black flex justify-between items-center"
              @click="toggleFaq(index)"
            >
              <span class="text-lg font-serif">{{ item.question }}</span>
              <ChevronDownIcon 
                class="h-5 w-5 text-[#1c8085] transition-transform"
                :class="{ 'rotate-180': openFaq === index }"
              />
            </button>
            <div
              v-show="openFaq === index"
              class="pb-4 text-gray-600"
            >
              {{ item.answer }}
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.font-serif {
  font-family: "Playfair Display", serif;
}
</style>
