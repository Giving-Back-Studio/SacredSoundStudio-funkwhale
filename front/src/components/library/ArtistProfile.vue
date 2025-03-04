<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
    <!-- Hero Section with Banner and Profile -->
    <div class="relative">
      <!-- Banner Image -->
      <div class="relative w-full h-[300px] md:h-[400px]">
        <img 
          :src="artist.bannerUrl" 
          alt=""
          class="w-full h-full object-cover"
        />
        <div class="absolute inset-0 bg-gradient-to-b from-transparent to-gray-900"></div>
      </div>

      <!-- Profile Section -->
      <div class="container mx-auto px-4">
        <div class="relative -mt-24 md:-mt-32 flex flex-col md:flex-row items-start md:items-end gap-6 mb-8">
          <!-- Profile Image -->
          <div class="w-32 h-32 md:w-48 md:h-48 rounded-full overflow-hidden border-4 border-gray-900 shrink-0">
            <img 
              :src="artist.profileUrl" 
              :alt="artist.name"
              class="w-full h-full object-cover"
            />
          </div>

          <!-- Artist Info -->
          <div class="flex-grow">
            <h1 class="text-3xl md:text-4xl font-bold mb-2">{{ artist.name }}</h1>
            <div class="flex flex-wrap gap-4 items-center">
              <button 
                class="px-6 py-2 bg-white text-black rounded-full hover:bg-gray-200 transition-colors"
                @click="giveThanks"
              >
                <span class="flex items-center gap-2">
                  <HeartIcon class="w-5 h-5" />
                  Give Thanks
                </span>
              </button>
              <div class="text-gray-400">
                {{ artist.thanksCount.toLocaleString() }} thanks received
              </div>
            </div>
          </div>
        </div>

        <!-- Bio Section -->
        <div class="max-w-3xl mb-12">
          <div class="relative">
            <p 
              ref="bioText"
              class="text-gray-300"
              :class="{ 'line-clamp-2': !showFullBio }"
            >
              {{ artist.bio }}
            </p>
            
            <!-- Show More/Less Button -->
            <button
              v-if="bioNeedsToggle"
              @click="toggleBio"
              class="mt-2 text-gray-400 hover:text-white transition-colors"
            >
              {{ showFullBio ? 'Show less' : 'Show more' }}
            </button>

            <!-- Social Links -->
            <div 
              v-if="showFullBio"
              class="mt-4 flex flex-wrap gap-4"
            >
              <a
                v-for="link in artist.links"
                :key="link.url"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-full hover:bg-gray-700 transition-colors"
              >
                <component :is="link.icon" class="w-5 h-5" />
                {{ link.title }}
              </a>
            </div>
          </div>
        </div>

        <!-- Music Section -->
        <div class="mb-12">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold">Discography</h2>
            <div class="flex gap-2">
              <button
                v-for="filter in filters"
                :key="filter.value"
                @click="currentFilter = filter.value"
                class="px-4 py-2 rounded-full text-sm transition-colors"
                :class="currentFilter === filter.value 
                  ? 'bg-white text-black' 
                  : 'bg-gray-800 hover:bg-gray-700'"
              >
                {{ filter.label }}
              </button>
            </div>
          </div>

          <!-- Music Grid -->
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            <div
              v-for="release in filteredReleases"
              :key="release.id"
              class="group"
            >
              <div class="relative aspect-square mb-3">
                <img 
                  :src="release.coverUrl" 
                  :alt="release.title"
                  class="w-full h-full object-cover rounded-lg"
                />
                <div class="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                  <button 
                    class="p-4 bg-white text-black rounded-full hover:bg-gray-200 transition-colors"
                    :aria-label="'Play ' + release.title"
                  >
                    <PlayIcon class="w-6 h-6" />
                  </button>
                </div>
              </div>
              <h3 class="font-medium line-clamp-1">{{ release.title }}</h3>
              <p class="text-sm text-gray-400">{{ release.year }}</p>
            </div>
          </div>
        </div>

        <!-- Events Section -->
        <div class="mb-12">
          <h2 class="text-2xl font-bold mb-6">Upcoming Events</h2>
          
          <div class="grid gap-4">
            <div
              v-for="event in events"
              :key="event.id"
              class="bg-gray-800 rounded-lg p-4 md:p-6 flex flex-col md:flex-row gap-4 md:items-center"
            >
              <!-- Date -->
              <div class="md:w-36 text-center shrink-0">
                <div class="text-2xl font-bold">{{ formatEventDate(event.date, 'day') }}</div>
                <div class="text-gray-400">{{ formatEventDate(event.date, 'month') }}</div>
              </div>

              <!-- Event Details -->
              <div class="flex-grow">
                <h3 class="text-xl font-semibold mb-2">{{ event.title }}</h3>
                <p class="text-gray-400 mb-2">{{ event.venue }}</p>
                <p class="text-gray-400">{{ event.location }}</p>
              </div>

              <!-- Action -->
              <div class="shrink-0">
                <a
                  :href="event.ticketUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-block px-6 py-2 bg-white text-black rounded-full hover:bg-gray-200 transition-colors"
                >
                  Get Tickets
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  HeartIcon,
  PlayIcon,
  InstagramIcon,
  GlobeIcon,
  YoutubeIcon,
  FacebookIcon
} from 'lucide-vue-next'

// Bio toggle state
const showFullBio = ref(false)
const bioText = ref(null)
const bioNeedsToggle = ref(false)

// Current music filter
const currentFilter = ref('all')

// Filter options
const filters = [
  { label: 'All', value: 'all' },
  { label: 'Albums', value: 'album' },
  { label: 'Singles', value: 'single' }
]

// Mock artist data
const artist = {
  name: 'Sacred Sound Artist',
  profileUrl: '/placeholder.svg?height=400&width=400',
  bannerUrl: '/placeholder.svg?height=1200&width=2000',
  bio: `Sacred sound artist bringing ancient wisdom through music. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.`,
  thanksCount: 15420,
  links: [
    { title: 'Website', url: 'https://example.com', icon: GlobeIcon },
    { title: 'Instagram', url: 'https://instagram.com', icon: InstagramIcon },
    { title: 'YouTube', url: 'https://youtube.com', icon: YoutubeIcon },
    { title: 'Facebook', url: 'https://facebook.com', icon: FacebookIcon }
  ]
}

// Mock releases data
const releases = [
  {
    id: 1,
    title: 'Sacred Mantras Vol. 1',
    coverUrl: '/placeholder.svg?height=300&width=300',
    type: 'album',
    year: '2024'
  },
  {
    id: 2,
    title: 'Morning Meditation',
    coverUrl: '/placeholder.svg?height=300&width=300',
    type: 'single',
    year: '2024'
  },
  {
    id: 3,
    title: 'Divine Chants',
    coverUrl: '/placeholder.svg?height=300&width=300',
    type: 'album',
    year: '2023'
  },
  {
    id: 4,
    title: 'Peace Mantras',
    coverUrl: '/placeholder.svg?height=300&width=300',
    type: 'single',
    year: '2023'
  },
  {
    id: 5,
    title: 'Sacred Journey',
    coverUrl: '/placeholder.svg?height=300&width=300',
    type: 'album',
    year: '2023'
  }
]

// Mock events data
const events = [
  {
    id: 1,
    title: 'Sacred Sound Journey',
    date: '2024-03-15T19:00:00',
    venue: 'Meditation Center',
    location: 'Los Angeles, CA',
    ticketUrl: '#'
  },
  {
    id: 2,
    title: 'Divine Mantras Live',
    date: '2024-04-01T20:00:00',
    venue: 'Yoga Temple',
    location: 'New York, NY',
    ticketUrl: '#'
  },
  {
    id: 3,
    title: 'Sacred Music Festival',
    date: '2024-04-15T18:00:00',
    venue: 'Peace Garden',
    location: 'San Francisco, CA',
    ticketUrl: '#'
  }
]

// Computed
const filteredReleases = computed(() => {
  if (currentFilter.value === 'all') return releases
  return releases.filter(release => release.type === currentFilter.value)
})

// Methods
const toggleBio = () => {
  showFullBio.value = !showFullBio.value
}

const giveThanks = () => {
  // Implement give thanks functionality
  console.log('Thanks given!')
}

const formatEventDate = (dateString, part) => {
  const date = new Date(dateString)
  if (part === 'day') {
    return date.getDate()
  }
  return date.toLocaleString('default', { month: 'short' })
}

// Lifecycle
onMounted(() => {
  // Check if bio needs toggle button
  if (bioText.value) {
    const lineHeight = parseInt(window.getComputedStyle(bioText.value).lineHeight)
    const height = bioText.value.offsetHeight
    bioNeedsToggle.value = height > lineHeight * 2
  }
})
</script>

<style>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>