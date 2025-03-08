<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useStore } from '~/store'
import '@mux/mux-player'

const store = useStore()

const featuredConcert = ref(null)
const nextConcerts = ref([])

// Format date to readable string
const formatDate = (date) => {
  const options = {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short'
  }
  return new Date(date).toLocaleDateString('en-US', options)
}

const isLive = computed(() => {
  if (!featuredConcert.value) return false
  const now = new Date()
  const concertStartTime = new Date(featuredConcert.value.start_time)
  return now >= concertStartTime
})

onMounted(() => {
  store.dispatch('concerts/fetchConcerts')
})

watch(
  () => store.state?.concerts?.featuredConcert,
  (newFeaturedConcert) => {
    featuredConcert.value = newFeaturedConcert
  }
)

watch(
  () => store.state?.concerts?.nextConcerts,
  (newNextConcerts) => {
    nextConcerts.value = newNextConcerts
  }
)

// Check if the user is an administrator
const isAdmin = computed(() => store.state.auth.profile.is_superuser)

// Share concert function
const shareConcert = (concert) => {

  if (navigator.share) {
    navigator.share({
      title: concert.title,
      text: `Check out this concert: ${concert.title} at ${concert.venue}`,
      url: window.location.href,
    })
    .catch((error) => console.log('Error sharing', error))
  } else {
    // Fallback for browsers that don't support the Web Share API
    alert(`Share this concert: ${concert.title}`)
  }
}

</script>

<template>
  <div class="ui container">
    <section v-if="featuredConcert" class="ui segment">
      <div class="ui fluid">
        <div v-if="isLive" class="ui embed">
          <mux-player
            :playback-id="featuredConcert.mux_playback_id"
            :metadata-video-id="featuredConcert.id"
            :metadata-video-title="featuredConcert.title"
            :metadata-viewer-user-id="store.state.auth.profile.username"
            controls
            muted
          />
          <span class="ui primary label" style="position: absolute; top: 1.5rem; right: 1.5rem;">LIVE</span>
        </div>
        <img
          v-else
          class="ui fluid image"
          :src="featuredConcert.cover"
          :alt="featuredConcert.title"
        />
      </div>

      <div class="ui basic segment">
        <div class="ui grid">
          <div class="fourteen wide column">
            <h1 class="ui header">{{ featuredConcert.title }}</h1>
            <div v-if="featuredConcert.artist" class="ui segment basic">
              <div class="ui items">
                <div class="item">
                  <div class="middle aligned content">
                    <router-link
                      :to="{ name: 'library.artists.detail', params: { id: featuredConcert.artist.id } }"
                    >
                      <img v-if="featuredConcert.artist.attachment_cover"
                        class="ui avatar image"
                        :src="featuredConcert.artist.attachment_cover.urls.medium_square_crop"
                        :alt="featuredConcert.artist.name"
                      />
                      {{ featuredConcert.artist.name }}
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
            <p class="ui text grey">
              {{ formatDate(featuredConcert.start_time) }}
            </p>
          </div>
          <div class="two wide column right aligned">
            <button class="ui circular icon button" @click="shareConcert(featuredConcert)">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-share-2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
            </button>
          </div>
        </div>

        <p class="ui text">{{ featuredConcert.description }}</p>
      </div>
    </section>
    <section v-else class="ui segment">
      <p>No featured concert available.</p>
    </section>

    <!-- Next Concerts -->
    <section class="ui segment">
      <h2 class="ui header">Upcoming Concerts</h2>
      <div v-if="nextConcerts?.length > 0" class="ui stackable cards">
        <div v-for="concert in nextConcerts" :key="concert.id" class="ui fluid card">
          <div class="image">
            <img
              :src="concert.cover"
              :alt="concert.title"
            />
          </div>
          <div class="content">
            <div class="ui grid">
              <div class="fourteen wide column">
                <div class="header">{{ concert.title }}</div>
                <div class="meta">
                  <span>{{ formatDate(concert.start_time) }}</span>
                </div>
              </div>
              <div class="two wide column right aligned">
                <button class="ui circular icon button" @click="shareConcert(concert)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-share-2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
                </button>
              </div>
            </div>
            <div class="description">
              {{ concert.description }}
            </div>
            <div class="extra content">
              <p class="ui text grey">Led by</p>
              <div class="ui items">
                <div class="item">
                  <img v-if="concert.artist.attachment_cover"
                    class="ui avatar image"
                    :src="concert.artist.attachment_cover.urls.medium_square_crop"
                    :alt="concert.artist.name"
                  />
                  <div class="middle aligned content">
                    <div class="header">{{ concert.artist.name }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <p>No upcoming concerts available.</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.ui.header {
  font-family: 'Playfair Display', serif;
}
</style>
