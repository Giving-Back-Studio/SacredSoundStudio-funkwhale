<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
    <!-- Hero Section with Banner and Profile -->
    <div class="relative">
      <!-- Banner Image -->
      <div class="relative w-full h-[300px] md:h-[400px]">
        <img 
          :src="artist?.attachment_cover?.urls?.original || '/placeholder.svg?height=1200&width=2000'" 
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
              :src="artist?.channel?.actor?.avatar?.urls?.original || '/placeholder.svg?height=400&width=400'" 
              :alt="artist?.name"
              class="w-full h-full object-cover"
            />
          </div>

          <!-- Artist Info -->
          <div class="flex-grow">
            <h1 class="text-3xl md:text-4xl font-bold mb-2">{{ artist?.name }}</h1>
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
                {{ thanksCount.toLocaleString() }} thanks received
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
              {{ artist?.description?.content || 'No bio available.' }}
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
              v-if="showFullBio && artist?.channel?.actor?.urls?.length"
              class="mt-4 flex flex-wrap gap-4"
            >
              <a
                v-for="link in artist?.channel?.actor?.urls"
                :key="link.url"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-full hover:bg-gray-700 transition-colors"
              >
                <component :is="getLinkIcon(link.type)" class="w-5 h-5" />
                {{ link.type }}
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
              v-for="album in filteredAlbums"
              :key="album.id"
              class="group"
            >
              <div class="relative aspect-square mb-3">
                <img 
                  :src="album.attachment_cover?.urls?.original || '/placeholder.svg?height=300&width=300'" 
                  :alt="album.title"
                  class="w-full h-full object-cover rounded-lg"
                />
                <div class="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                  <button 
                    class="p-4 bg-white text-black rounded-full hover:bg-gray-200 transition-colors"
                    :aria-label="'Play ' + album.title"
                    @click="playAlbum(album)"
                  >
                    <PlayIcon class="w-6 h-6" />
                  </button>
                </div>
              </div>
              <h3 class="font-medium line-clamp-1">{{ album.title }}</h3>
              <p class="text-sm text-gray-400">{{ formatReleaseDate(album.release_date) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from '~/store'
import type { Artist, Album } from '~/store/artists'
import { 
  HeartIcon,
  PlayIcon,
  GlobeIcon,
  InstagramIcon,
  YoutubeIcon,
  FacebookIcon
} from 'lucide-vue-next'

interface IconMap {
  [key: string]: typeof GlobeIcon
}

type FilterValue = 'all' | 'album' | 'single'
interface Filter {
  label: string
  value: FilterValue
}

const route = useRoute()
const store = useStore()

// Bio toggle state
const showFullBio = ref(false)
const bioText = ref<HTMLParagraphElement | null>(null)
const bioNeedsToggle = ref(false)

// Current music filter
const currentFilter = ref<FilterValue>('all')

// Filter options
const filters: Filter[] = [
  { label: 'All', value: 'all' },
  { label: 'Albums', value: 'album' },
  { label: 'Singles', value: 'single' }
]

// Mock data for now
const thanksCount = ref(0)

// Fetch artist data
const artist = ref<Artist | null>(null)
const fetchArtist = async () => {
  try {
    const id = typeof route.params.id === 'string' ? route.params.id : route.params.id[0]
    const response = await store.dispatch('artists/fetchOne', id)
    artist.value = response
  } catch (error) {
    console.error('Error fetching artist:', error)
  }
}

// Computed
const filteredAlbums = computed(() => {
  if (!artist.value?.albums) return []
  if (currentFilter.value === 'all') return artist.value.albums
  return artist.value.albums.filter(album => album.type === currentFilter.value)
})

// Methods
const toggleBio = () => {
  showFullBio.value = !showFullBio.value
}

const giveThanks = () => {
  // UI only for now
  thanksCount.value++
  console.log('Thanks given!')
}

const playAlbum = (album: Album) => {
  // TODO: Implement album playback
  console.log('Playing album:', album.title)
}

const formatReleaseDate = (date: string | undefined) => {
  if (!date) return ''
  return new Date(date).getFullYear()
}

const getLinkIcon = (type: string) => {
  const icons: IconMap = {
    'website': GlobeIcon,
    'instagram': InstagramIcon,
    'youtube': YoutubeIcon,
    'facebook': FacebookIcon
  }
  return icons[type.toLowerCase()] || GlobeIcon
}

// Lifecycle
onMounted(async () => {
  await fetchArtist()
  
  // Check if bio needs toggle button
  nextTick(() => {
    const element = bioText.value as HTMLParagraphElement | null
    if (element) {
      const style = window.getComputedStyle(element)
      const lineHeight = parseInt(style.lineHeight)
      const height = element.getBoundingClientRect().height
      bioNeedsToggle.value = height > lineHeight * 2
    }
  })
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
