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
    hour: '2-digit',
    minute: '2-digit'
  }
  return new Date(date).toLocaleDateString('en-US', options)
}

const isLive = computed(() => {
  if (!featuredConcert.value) return false
  const now = new Date()
  const concertStartTime = new Date(featuredConcert.value.date)
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
      title: concert.name,
      text: `Check out this concert: ${concert.name} at ${concert.venue}`,
      url: window.location.href,
    })
    .catch((error) => console.log('Error sharing', error))
  } else {
    // Fallback for browsers that don't support the Web Share API
    alert(`Share this concert: ${concert.name}`)
  }
}

</script>

<template>
  <div class="concert-hall">

    <!-- Admin Tab -->
    <div v-if="isAdmin" class="admin-tab">
      <h2>Admin Panel</h2>
      <router-link to="/manage-concerts">
        <button>Manage Concerts</button>
      </router-link>
    </div>

    <!-- Featured Concert -->
    <section class="featured-concert" v-if="featuredConcert">
      <!-- Admin comment: This is the featured concert chosen by admin -->
      <div class="concert-media">
        <!-- Show video if concert is streaming, otherwise show banner image -->
<!--  <div v-if="featuredConcert?.isStreaming" class="video-container">-->
          <div v-if="isLive" class="video-container">
          <mux-player
            :playback-id="featuredConcert?.playbackId"
            :metadata-video-id="featuredConcert?.id"
            :metadata-video-title="featuredConcert?.name"
            :metadata-viewer-user-id="store.state.auth.profile.username"
            controls
            muted
          />
          <div class="live-badge">LIVE</div>
        </div>
        <img
          v-else
          class="concert-banner"
          :src="featuredConcert?.cover"
          :alt="featuredConcert?.name"
        />
      </div>

      <div class="concert-details">
        <div class="concert-header">
          <div>
            <h1 class="concert-title">{{ featuredConcert?.name }}</h1>
            <p class="concert-datetime">{{ formatDate(featuredConcert?.date) }}</p>
          </div>
          <button class="share-button" @click="shareConcert(featuredConcert)">
            <span class="icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-share-2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
            </span>
          </button>
        </div>

        <p class="concert-description">{{ featuredConcert?.description }}</p>

        <div class="artist-section">
          <p class="led-by">Led by</p>
          <div class="artist">
            <img
              class="artist-image"
              :src="featuredConcert?.artist.image"
              :alt="featuredConcert?.artist.name"
            />
            <span class="artist-name">{{ featuredConcert?.artist.name }}</span>
          </div>
        </div>
      </div>
    </section>
    <section v-else>
      <p>No featured concert available.</p>
    </section>

   <!-- Next Concerts -->
    <section class="next-concerts">
      <h2 class="section-title">Next Concerts</h2>
      <div v-if="nextConcerts?.length > 0">
        <div v-for="concert in nextConcerts" :key="concert.id" class="concert-card">
          <img
            class="concert-thumbnail"
            :src="concert.cover"
            :alt="concert.name"
          />
          <div class="concert-card-details">
            <div class="concert-card-header">
              <div>
                <h3 class="concert-card-title">{{ concert.name }}</h3>
                <p class="concert-datetime">{{ formatDate(concert.date) }}</p>
              </div>
              <button class="share-button" @click="shareConcert(concert)">
                <span class="icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-share-2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/></svg>
                </span>
              </button>
            </div>
            <p class="concert-description">{{ concert.description }}</p>
            <div class="artist-section">
              <p class="led-by">Led by</p>
              <div class="artist">
                <img
                  class="artist-image"
                  :src="concert.artist.image"
                  :alt="concert.artist.name"
                />
                <span class="artist-name">{{ concert.artist.name }}</span>
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
/* Base styles */
.concert-hall {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
  color: #434289;
  font-family: 'Montserrat', sans-serif;
  background-color: #F1F4F8;
}

/* Featured Concert */
.featured-concert {
  margin-bottom: 3rem;
}

.concert-media {
  position: relative;
  width: 100%;
  margin-bottom: 1.5rem;
}

.concert-banner,
.concert-video {
  width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 0;
  aspect-ratio: 16/9;
}

.video-container {
  position: relative;
}

.live-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background-color: #ff4a4a;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.05em;
}

.concert-details {
  padding: 0 1.5rem;
}

.concert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.concert-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  line-height: 1.2;
}

.concert-datetime {
  font-size: 0.875rem;
  color: #434289;
  opacity: 0.8;
  margin: 0;
}

.share-button {
  background: none;
  border: none;
  cursor: pointer;
  color: #434289;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.share-button:hover {
  background-color: rgba(67, 66, 137, 0.1);
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
}

.concert-description {
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.artist-section {
  margin-top: 1.5rem;
}

.led-by {
  font-size: 0.875rem;
  opacity: 0.7;
  margin-bottom: 0.5rem;
}

.artist {
  display: flex;
  align-items: center;
}

.artist-image {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 0.75rem;
}

.artist-name {
  font-weight: 600;
}

/* Next Concert */
.next-concert {
  padding: 0 1.5rem 3rem;
}

.section-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  font-weight: 700;
}

.concert-card {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.concert-thumbnail {
  width: 100%;
  height: auto;
  object-fit: cover;
  aspect-ratio: 16/9;
}

.concert-card-details {
  padding: 1.5rem;
}

.concert-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.concert-card-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  line-height: 1.2;
}

.admin-tab {
  background-color: #f8f9fa;
  padding: 1rem;
  margin-bottom: 2rem;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
}

/* Responsive styles */
@media (min-width: 768px) {
  .concert-details {
    padding: 0 2rem;
  }

  .next-concert {
    padding: 0 2rem 3rem;
  }

  .concert-title {
    font-size: 2rem;
  }

  .concert-card {
    display: flex;
    align-items: stretch;
  }

  .concert-thumbnail {
    width: 40%;
    height: auto;
    aspect-ratio: auto;
    object-fit: cover;
  }

  .concert-card-details {
    width: 60%;
  }
}

@media (min-width: 1024px) {
  .concert-details {
    padding: 0 3rem;
  }

  .next-concert {
    padding: 0 3rem 4rem;
  }

  .concert-title {
    font-size: 2.5rem;
  }

  .section-title {
    font-size: 1.75rem;
  }

  .concert-card-title {
    font-size: 1.5rem;
  }
}
</style>