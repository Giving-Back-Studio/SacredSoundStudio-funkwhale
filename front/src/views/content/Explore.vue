<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useRouteQuery } from '@vueuse/router'
import { syncRef } from '@vueuse/core'

import axios from 'axios'

import store from '~/store'

import useErrorHandler from '~/composables/useErrorHandler'
import ContentCard from '~/components/audio/ContentCard.vue'
import ContentSet from '~/components/library/ContentSet.vue'
import PlayButton from '~/components/audio/PlayButton.vue'

const q = useRouteQuery('q', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })
const isLoading = ref(false)

const activeFilters = ref([])
const openFilterCategory = ref(null)

const searchInput = ref(null)
const searchResultsArtists = ref([])
const searchResultsAlbums = ref([])
const searchResultsTracks = ref([])

const hotTracks = ref([])
const recentlyUploadedAlbums = ref([])

const noResults = ref(false)

const focusSearchInput = () => {
  nextTick(() => {
    searchInput.value.focus()
  })
}

const clearQuery = () => {
  query.value = ''
  search()
}

const search = async () => {
  if (!query.value && activeFilters.value.length === 0) {
    searchResultsArtists.value = []
    searchResultsAlbums.value = []
    searchResultsTracks.value = []
    noResults.value = false
    return
  }

  isLoading.value = true
  const response = await axios.get('/search', {
    params: {
      q: query.value,
      tags: activeFilters.value.map((filter) => (filter.value)).join(',')
    }
  })

  searchResultsArtists.value = response.data.artists
  searchResultsAlbums.value = response.data.albums
  searchResultsTracks.value = response.data.tracks

  noResults.value = (
    response.data.artists.length === 0 &&
    response.data.albums.length === 0 &&
    response.data.tracks.length === 0
  )
  isLoading.value = false
}

const contentCategories = ref([])

const fetchContentCategories = async () => {
  try {
    const response = await axios.get('tag-categories/')

    contentCategories.value = response.data.results
  } catch (error) {
    useErrorHandler(error)
    contentCategories.value = []
  }
}

const fetchRecentActivity = async () => {
  try {
    const activityResponse = await axios.get('activity/')
    const allActivity = activityResponse.data.results

    // Use a Set to track unique tracks
    const uniqueTracks = new Set()
    const filteredActivities = []

    for (const activity of allActivity) {
      if (!uniqueTracks.has(activity.object.local_id)) {
        uniqueTracks.add(activity.object.local_id)
        filteredActivities.push(activity)
      }
    }

    // Slice to take the top 12 unique activities
    const latestActivity = filteredActivities.slice(0, 12)
    const trackIds = latestActivity.map(activity => activity.object.local_id)

    const tracksResponse = await axios.get('tracks/?id__in=' + trackIds.join(','))

    hotTracks.value = tracksResponse.data.results
  } catch (error) {
    useErrorHandler(error)
  }
}

onMounted(() => {
  fetchContentCategories()
  focusSearchInput()
  fetchRecentActivity()
})

// Filter search state
const filterSearch = ref('')

// Get filtered options based on search input
const filteredOptions = computed(() => {
  if (!filterSearch.value) {
    return getFilterOptions(openFilterCategory.value)
  }

  const options = getFilterOptions(openFilterCategory.value)
  return options.filter(option =>
    option.toLowerCase().includes(filterSearch.value.toLowerCase())
  )
})

// Filter functions
const toggleFilterCategory = (category) => {
  if (openFilterCategory.value === category) {
    openFilterCategory.value = null
  } else {
    openFilterCategory.value = category
    // Reset filter search when changing categories
    filterSearch.value = ''
  }
}

const removeFilter = (index) => {
  activeFilters.value.splice(index, 1)
  search()
}

const getFilterOptions = (category) => {
  const found = contentCategories.value.find(c => c.name === category)
  return found ? found.options : []
}

// Check if a filter is already selected
const isFilterSelected = (type, value) => {
  return activeFilters.value.some(filter =>
    filter.type === type && filter.value === value
  )
}

// Toggle a filter on/off
const toggleFilter = (type, value) => {
  const index = activeFilters.value.findIndex(filter =>
    filter.type === type && filter.value === value
  )

  if (index !== -1) {
    activeFilters.value.splice(index, 1)
  } else {
    activeFilters.value.push({ type, value })
  }

  search()
}

const getAlbumCover = (album) => {
  if (album.cover) {
    return album.cover.urls.medium_square_crop
  }
}

const getTrackCover = (track) => {
  if (track.cover) {
    return track.cover.urls.medium_square_crop
  }
  return getAlbumCover(track.album)
}

const getArtistCover = (artist) => {
  if (artist.cover && artist.cover.urls) {
    return store.getters['instance/absoluteUrl'](artist.cover.urls.medium_square_crop)
  }
  const album = artist.albums.find(album => !!album.cover?.urls.original)
  if (album) {
    return getAlbumCover(album)
  }
}

const translateActivityType = (activityType) => {
  // TODO possibly use translation dict lookup?
  return {"Listen": "listened to", "Like": "liked"}[activityType]
}

</script>

<template>
  <div class="min-h-screen main with-background">
    <main class="container mx-auto px-4 py-8">
      <div class="mb-8 ui fluid big left icon input" :class="{ 'right action': query}">
        <i class="search icon"></i>
        <input
          v-model="query"
          @keypress.enter="search"
          ref="searchInput"
          type="text"
          class="w-full p-2 border border-gray-300 rounded"
          placeholder="Search for artists, albums, or tracks..."
        />
        <button v-if="query" class="ui icon button" @click="clearQuery"><i class="ml-2 close icon"></i></button>
      </div>

      <!-- Active Filters -->
      <div v-if="activeFilters.length > 0" class="active-filters">
        <div
          v-for="(filter, index) in activeFilters"
          :key="index"
          class="active-filter"
        >
          <span>{{ filter.type }}: {{ filter.value }}</span>
          <button @click="removeFilter(index)" class="remove-filter">
            <i class="close icon"></i>
          </button>
        </div>
      </div>

      <!-- Filter Categories -->
      <div class="filter-categories">
        <div class="filter-scroll-container">
          <button
            v-for="(category, index) in contentCategories"
            :key="index"
            class="filter-category"
            :class="{ 'active': openFilterCategory === category.name }"
            @click="toggleFilterCategory(category.name)"
          >
            {{ category.name }}
            <i
              class="icon angle"
              :class="{ 'up': openFilterCategory === category.name, 'down': openFilterCategory !== category.name }" />
          </button>
        </div>
      </div>

      <!-- Filter Dropdown -->
      <div v-if="openFilterCategory" class="filter-dropdown">
        <h3 class="text-lg font-playfair mb-2">{{ openFilterCategory }}</h3>

        <!-- Filter search input -->
        <div class="filter-search-container mb-3">
          <input
            v-model="filterSearch"
            type="text"
            class="filter-search-input"
            placeholder="Search..."
          />
        </div>

        <!-- Available options -->
        <div class="filter-options">
          <div
            v-for="(option, index) in filteredOptions"
            :key="index"
            class="filter-option"
            :class="{ 'selected': isFilterSelected(openFilterCategory, option) }"
            @click="toggleFilter(openFilterCategory, option)"
          >
            {{ option }}
          </div>
        </div>
      </div>

      <div v-if="isLoading">
        <div class="ui inverted active dimmer" >
          <div class="ui loader" />
        </div>
      </div>
      <empty-state v-else-if="noResults" />

      <div v-if="searchResultsArtists.length" class="ui segment">
        <div class="ui horizontal divider">Artists</div>
        <div class="results-scroll-container">
          <div v-for="(artist, index) in searchResultsArtists" :key="index" class="artist-card">
            <router-link
              class="discrete link"
              :to="{name: 'library.artists.detail', params: {id: artist.id}}"
            >
              <div class="artist-image">
                <img :src="getArtistCover(artist)" :alt="artist.name" />
              </div>
              <div class="artist-name">{{ artist.name }}</div>
            </router-link>
          </div>
        </div>
      </div>

      <content-set title="Albums" :content="searchResultsAlbums" type="album"/>

      <content-set title="Tracks" :content="searchResultsTracks" type="track"/>

      <content-set v-if="!query && activeFilters.length === 0"
        title="Trending Tracks"
        :content="hotTracks"
        type="track"
      />
    </main>
  </div>
</template>

<style>
.main.with-background {
  background: var(--site-background) !important;
}

.segment .ui.card {
  background: none !important;
}

/* Active Filters */
.active-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.active-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #eef3e6;
  padding: 0.5rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
}

.remove-filter {
  background: none;
  border: none;
  cursor: pointer;
  color: #e7922f;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Filter Categories */
.filter-categories {
  margin-bottom: 1rem;
  overflow: hidden;
}

.filter-scroll-container {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  scrollbar-width: thin;
  scrollbar-color: #1c8085 #F1F4F8;
}

.filter-scroll-container::-webkit-scrollbar {
  height: 4px;
}

.filter-scroll-container::-webkit-scrollbar-track {
  background: #F1F4F8;
}

.filter-scroll-container::-webkit-scrollbar-thumb {
  background-color: #eef3e6;
  border-radius: 20px;
}

.filter-category {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: white;
  border: 1px solid #D9D9E7;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  white-space: nowrap;
  transition: all 0.2s;
}

.filter-category:hover {
  border-color: #A3C4A3;
}

.filter-category.active {
  background-color: #1c8085;
  color: white;
  border-color: #1c8085;
}

/* Filter Search */
.filter-search-container {
  position: relative;
}

.filter-search-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #D9D9E7;
  border-radius: 4px;
  font-family: 'Montserrat', sans-serif;
}

.filter-search-input:focus {
  outline: none;
  border-color: #A3C4A3;
}

/* Filter Dropdown */
.filter-dropdown {
  background-color: white;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.filter-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.5rem;
}

.filter-option {
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
}

.filter-option:hover {
  background-color: #eef3e6;
}

/* Selected filter option */
.filter-option.selected {
  background-color: #eef3e6;
  font-weight: 500;
}

.filter-option.custom-option {
  display: flex;
  align-items: center;
  border: 1px dashed #A3C4A3;
  background-color: rgba(163, 196, 163, 0.1);
}

/* Search Results */
.search-results {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.result-section {
  margin-bottom: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.view-all {
  color: #A3C4A3;
  font-size: 0.875rem;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
}

.results-scroll-container {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding-bottom: 1rem;
  scrollbar-width: thin;
  scrollbar-color: #A3C4A3 #F1F4F8;
}

.results-scroll-container::-webkit-scrollbar {
  height: 4px;
}

.results-scroll-container::-webkit-scrollbar-track {
  background: #F1F4F8;
}

.results-scroll-container::-webkit-scrollbar-thumb {
  background-color: #A3C4A3;
  border-radius: 20px;
}

.view-all-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1.5rem;
}

.artist-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 150px;
  max-width: 150px;
}

.artist-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.artist-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.artist-name {
  text-align: center;
  font-weight: 500;
}
</style>
