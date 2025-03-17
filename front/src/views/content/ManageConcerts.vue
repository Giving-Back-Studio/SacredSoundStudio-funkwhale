<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStore } from '~/store'
import type { Concert } from '~/store/concerts'

const store = useStore()
const concerts = ref<Concert[]>([])
const showForm = ref(false)
const isEditing = ref(false)
const currentConcert = ref<Concert | null>(null)

onMounted(() => {
  store.dispatch('concerts/fetchConcerts').then(() => {
    concerts.value = store.state.concerts.concerts
  })
})

const openForm = (concert: Concert | null = null) => {
  currentConcert.value = concert
  isEditing.value = !!concert
  showForm.value = true
}

const saveConcert = async () => {
  if (currentConcert.value) {
    if (isEditing.value) {
      await store.dispatch('concerts/updateConcert', currentConcert.value)
    } else {
      await store.dispatch('concerts/createConcert', currentConcert.value)
    }
    showForm.value = false
    concerts.value = store.state.concerts.concerts
  }
}

const deleteConcert = async (concertId: number) => {
  await store.dispatch('concerts/deleteConcert', concertId)
  concerts.value = store.state.concerts.concerts
}
</script>

<template>
  <div>
    <h1>Manage Concerts</h1>
    <button @click="openForm()">Create New Concert</button>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Description</th>
          <th>Date</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="concert in concerts" :key="concert.id">
          <td>{{ concert.name }}</td>
          <td>{{ concert.description }}</td>
          <td>{{ concert.date }}</td>
          <td>
            <button @click="openForm(concert)">Edit</button>
            <button @click="deleteConcert(concert.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="showForm" class="modal">
      <div class="modal-content">
        <h2>{{ isEditing ? 'Edit Concert' : 'Create Concert' }}</h2>
        <form @submit.prevent="saveConcert">
          <div class="form-group">
            <label for="name">Name:</label>
            <input v-model="currentConcert.name" id="name" type="text" required />
          </div>
          <div class="form-group">
            <label for="description">Description:</label>
            <textarea v-model="currentConcert.description" id="description" required></textarea>
          </div>
          <div class="form-group">
            <label for="date">Date:</label>
            <input v-model="currentConcert.date" id="date" type="datetime-local" required />
          </div>
          <div class="form-group">
            <label for="isStreaming">Is Streaming:</label>
            <input v-model="currentConcert.isStreaming" id="isStreaming" type="checkbox" />
          </div>
          <div class="form-group">
            <label for="playbackId">Playback ID:</label>
            <input v-model="currentConcert.playbackId" id="playbackId" type="text" />
          </div>
          <div class="form-group">
            <label for="artistName">Artist Name:</label>
            <input v-model="currentConcert.artist.name" id="artistName" type="text" required />
          </div>
          <div class="form-group">
            <label for="artistImage">Artist Image:</label>
            <input v-model="currentConcert.artist.image" id="artistImage" type="text" required />
          </div>
          <div class="form-group">
            <label for="venue">Venue:</label>
            <input v-model="currentConcert.venue" id="venue" type="text" required />
          </div>
          <div class="form-actions">
            <button type="submit">{{ isEditing ? 'Update' : 'Create' }}</button>
            <button type="button" @click="showForm = false">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Modal styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.form-group input[type="checkbox"] {
  width: auto;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.form-actions button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.form-actions button[type="submit"] {
  background: #4caf50;
  color: white;
}

.form-actions button[type="button"] {
  background: #f44336;
  color: white;
}
</style>