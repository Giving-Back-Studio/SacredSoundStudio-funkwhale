<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouteQuery } from '@vueuse/router'
import { syncRef } from '@vueuse/core'

import axios from 'axios'

import store from '~/store'

import useErrorHandler from '~/composables/useErrorHandler'
import AlbumCard from '~/components/audio/album/Card.vue'
import PlayButton from '~/components/audio/PlayButton.vue'

const q = useRouteQuery('q', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

const activeFilters = ref([])
const openFilterCategory = ref(null)

const searchResultsArtists = ref([])
const searchResultsAlbums = ref([])
const searchResultsTracks = ref([])

const search = async () => {
  const response = await axios.get('/search', {
    params: {
      q: query.value,
      tags: activeFilters.value.map((filter) => (filter.value)).join(',')
    }
  })

  searchResultsArtists.value = response.data.artists
  searchResultsAlbums.value = response.data.albums
  searchResultsTracks.value = response.data.tracks
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


onMounted(() => {
  fetchContentCategories()
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

const getTrackDuration = (track) => {
  if (track.uploads.length > 0) {
    return track.uploads[0].duration
  }
}

</script>

<template>
  <div class="min-h-screen main with-background">
    <main class="container mx-auto px-4 py-8">
      <h1 class="text-4xl mb-8 font-serif">Explore Sacred Sounds</h1>
      <div class="mb-8 ui fluid big right icon left icon input">
        <i class="search icon"></i>
        <input
          v-model="query"
          @keypress.enter="search"
          type="text"
          class="w-full p-2 border border-gray-300 rounded"
          placeholder="Search for artists, albums, or tracks..."
        />
        <button class="ui icon button" @click="query = ''"><i class="ml-2 close icon"></i></button>
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
            <span>{{ option }}</span>
            <i v-if="isFilterSelected(openFilterCategory, option)" class="check icon ml-auto" />
          </div>
        </div>
      </div>

      <div v-if="searchResultsArtists.length" class="mb-6">
        <h2 class="header text-4xl mb-2">Artists</h2>
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

      <div v-if="searchResultsAlbums.length" class="mb-6">
        <h2 class="header text-4xl mb-2">Albums</h2>
        <div class="ui five app-cards cards">
          <album-card
            v-for="album in searchResultsAlbums"
            :key="album.id"
            :album="album"
          />
        </div>
      </div>

      <div v-if="searchResultsTracks.length" class="mb-6">
        <h2 class="header text-4xl mb-2">Tracks</h2>
        <div class="view-all-grid">
          <div v-for="(track, index) in searchResultsTracks" :key="index" class="track-card">
            <div class="track-cover">
              <img :src="getTrackCover(track)" :alt="track.title" />
              <div class="play-overlay">
                <play-button
                  id="playmenu"
                  class="primary"
                  :discrete="true"
                  :is-playable="track.is_playable"
                  :track="track"
                />
              </div>
            </div>
            <div class="track-title">{{ track.title }}</div>
            <div class="track-artist">{{ track.artist.name }}</div>
            <div class="track-metadata">
              <span class="track-genre">{{ track.tags.Genre[0] }}</span>
              <span class="track-duration">
                <human-duration
                  v-if="track.uploads[0] && track.uploads[0].duration"
                  :duration="track.uploads[0].duration"
                />
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style>
.main.with-background {
  background: var(--site-background) !important;
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
  background-color: #D9D9E7;
  padding: 0.5rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
}

.remove-filter {
  background: none;
  border: none;
  cursor: pointer;
  color: #434289;
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
  scrollbar-color: #A3C4A3 #F1F4F8;
}

.filter-scroll-container::-webkit-scrollbar {
  height: 4px;
}

.filter-scroll-container::-webkit-scrollbar-track {
  background: #F1F4F8;
}

.filter-scroll-container::-webkit-scrollbar-thumb {
  background-color: #A3C4A3;
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
  background-color: #434289;
  color: white;
  border-color: #434289;
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
}

.filter-option:hover {
  background-color: #D9D9E7;
}

/* Selected filter option */
.filter-option.selected {
  background-color: #D9D9E7;
  font-weight: 500;
  display: flex;
  align-items: center;
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

.back-button {
  display: flex;
  align-items: center;
  color: #434289;
  font-size: 0.875rem;
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

/* Track Card */
.track-card {
  display: flex;
  flex-direction: column;
  min-width: 200px;
  max-width: 200px;
}

.track-cover {
  position: relative;
  width: 200px;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.track-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(67, 66, 137, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.track-cover:hover .play-overlay {
  opacity: 1;
}

.play-icon {
  color: white;
  width: 48px;
  height: 48px;
}

.track-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-artist {
  font-size: 0.875rem;
  color: #434289;
  opacity: 0.8;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-metadata {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #434289;
  opacity: 0.6;
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
