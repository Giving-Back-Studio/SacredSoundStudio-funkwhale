<script setup>
import { ref, computed } from 'vue'

// Steps configuration
const steps = [
  { number: 1, title: 'Choose Type' },
  { number: 2, title: 'Upload Content' },
  { number: 3, title: 'Track Details' }
]

// State
const currentStep = ref(1)
const uploadType = ref('')
const isDragging = ref(false)
const isDraggingCover = ref(false)
const uploadedFiles = ref([])
const currentTrackIndex = ref(0)

// Album details
const albumDetails = ref({
  name: '',
  description: '',
  cover: null,
  coverPreview: null
})

// Options for metadata
const categories = [
  'Studio production',
  'Music video',
  'Meditation',
  'DJ set',
  'Behind the scenes',
  'Concert',
  'Live recording',
  'Video lesson'
]

const genres = ['Classical', 'Kirtan', 'Mantra', 'Meditation', 'World']
const instruments = ['Harmonium', 'Tabla', 'Guitar', 'Sitar', 'Flute']
const languages = ['Sanskrit', 'Hindi', 'English', 'Bengali']
const traditions = ['Bhakti', 'Vedic', 'Buddhist', 'Sufi']
const deities = ['Krishna', 'Shiva', 'Devi', 'Ganesh']
const intentions = ['Healing', 'Peace', 'Love', 'Devotion']
const moods = ['Peaceful', 'Energetic', 'Meditative', 'Joyful']
const tags = ['Sacred', 'Spiritual', 'Traditional', 'Modern']
const countries = ['India', 'USA', 'UK', 'Australia']

const vocalOptions = {
  instrumental: 'Instrumental',
  male: 'Male',
  female: 'Female',
  choir: 'Choir',
  circle: 'Circle'
}

// Track template
const createTrackTemplate = () => ({
  name: '',
  description: '',
  category: '',
  genre: '',
  featuredInstruments: [],
  primaryInstrument: '',
  languages: [],
  traditions: [],
  deities: [],
  intentions: [],
  moods: [],
  tags: [],
  vocals: {
    instrumental: false,
    male: false,
    female: false,
    choir: false,
    circle: false
  },
  recordLabel: '',
  recordingCountry: '',
  releaseDate: '',
  uploadedBy: 'Current User',
  uploadedTime: new Date().toISOString()
})

// Tracks metadata
const tracksMetadata = ref([])

// Computed
const currentTrack = computed({
  get: () => tracksMetadata.value[currentTrackIndex.value] || createTrackTemplate(),
  set: (value) => {
    tracksMetadata.value[currentTrackIndex.value] = value
  }
})

const canProceed = computed(() => {
  if (currentStep.value === 1) return !!uploadType.value
  if (currentStep.value === 2) {
    if (uploadType.value === 'album') {
      return !!albumDetails.value.name && !!albumDetails.value.cover && uploadedFiles.value.length > 0
    }
    return uploadedFiles.value.length > 0
  }
  return true
})

const isValid = computed(() => {
  // Add validation logic for the final step
  return true
})

// Methods
const selectUploadType = (type) => {
  uploadType.value = type
}

const handleCoverDrop = (e) => {
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    handleCoverFile(file)
  }
  isDraggingCover.value = false
}

const handleCoverSelect = (e) => {
  const file = e.target.files[0]
  if (file) handleCoverFile(file)
}

const handleCoverFile = (file) => {
  albumDetails.value.cover = file
  albumDetails.value.coverPreview = URL.createObjectURL(file)
}

const removeCover = () => {
  albumDetails.value.cover = null
  albumDetails.value.coverPreview = null
}

const handleContentDrop = (e) => {
  const files = Array.from(e.dataTransfer.files)
  handleFiles(files)
  isDragging.value = false
}

const handleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  handleFiles(files)
}

const handleFiles = (files) => {
  const validFiles = files.filter(file => 
    file.type.startsWith('audio/') || file.type.startsWith('video/')
  )

  validFiles.forEach(file => {
    uploadedFiles.value.push({
      name: file.name,
      size: file.size,
      type: file.type,
      progress: 0,
      file
    })
    tracksMetadata.value.push(createTrackTemplate())
    
    // Simulate upload progress
    const interval = setInterval(() => {
      const index = uploadedFiles.value.findIndex(f => f.name === file.name)
      if (index !== -1) {
        uploadedFiles.value[index].progress += 10
        if (uploadedFiles.value[index].progress >= 100) {
          clearInterval(interval)
        }
      }
    }, 200)
  })
}

const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
  tracksMetadata.value.splice(index, 1)
  if (currentTrackIndex.value >= uploadedFiles.value.length) {
    currentTrackIndex.value = Math.max(0, uploadedFiles.value.length - 1)
  }
}

const formatFileSize = (size) => {
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(1)} ${units[i]}`
}

const handleVocalChange = (key) => {
  if (key === 'instrumental' && currentTrack.value.vocals.instrumental) {
    Object.keys(currentTrack.value.vocals).forEach(k => {
      if (k !== 'instrumental') currentTrack.value.vocals[k] = false
    })
  } else if (key !== 'instrumental' && currentTrack.value.vocals[key]) {
    currentTrack.value.vocals.instrumental = false
  }
}

const previousTrack = () => {
  if (currentTrackIndex.value > 0) currentTrackIndex.value--
}

const nextTrack = () => {
  if (currentTrackIndex.value < uploadedFiles.value.length - 1) currentTrackIndex.value++
}

const previousStep = () => {
  if (currentStep.value > 1) currentStep.value--
}

const nextStep = () => {
  if (currentStep.value < steps.length) currentStep.value++
}

const submitUpload = () => {
  console.log('Submitting upload:', {
    uploadType: uploadType.value,
    albumDetails: uploadType.value === 'album' ? albumDetails.value : null,
    tracks: tracksMetadata.value
  })
}
</script>

<template>
    <div class="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-6">
      <div class="max-w-4xl mx-auto">
        <!-- Stepper -->
        <div class="mb-8">
          <div class="flex justify-between items-center">
            <div v-for="step in steps" :key="step.number" class="flex-1 relative">
              <div 
                class="flex items-center justify-center"
                :class="{'border-white': currentStep >= step.number}"
              >
                <div 
                  class="w-10 h-10 rounded-full flex items-center justify-center"
                  :class="currentStep >= step.number ? 'bg-white text-black' : 'border-2 border-gray-600'"
                >
                  {{ step.number }}
                </div>
                <div 
                  class="absolute -bottom-6 w-full text-center text-sm"
                  :class="currentStep >= step.number ? 'text-white' : 'text-gray-500'"
                >
                  {{ step.title }}
                </div>
              </div>
              <div 
                v-if="step.number < steps.length" 
                class="absolute top-5 -right-1/2 w-full h-0.5"
                :class="currentStep > step.number ? 'bg-white' : 'bg-gray-600'"
              ></div>
            </div>
          </div>
        </div>
  
        <!-- Step 1: Choose Upload Type -->
        <div v-if="currentStep === 1" class="bg-gray-800 rounded-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">Choose Upload Type</h2>
          <div class="grid grid-cols-2 gap-6">
            <button 
              @click="selectUploadType('album')"
              class="p-6 rounded-lg border-2 text-center transition-all"
              :class="uploadType === 'album' ? 'border-white bg-gray-700' : 'border-gray-600 hover:border-gray-400'"
            >
              <i class="list icon" />
              <h3 class="text-xl font-semibold">Album Upload</h3>
              <p class="text-gray-400 mt-2">Upload multiple tracks as an album</p>
            </button>
            <button 
              @click="selectUploadType('individual')"
              class="p-6 rounded-lg border-2 text-center transition-all"
              :class="uploadType === 'individual' ? 'border-white bg-gray-700' : 'border-gray-600 hover:border-gray-400'"
            >
              <i class="music icon" />
              <h3 class="text-xl font-semibold">Individual Upload</h3>
              <p class="text-gray-400 mt-2">Upload single or multiple tracks</p>
            </button>
          </div>
        </div>
  
        <!-- Step 2: Upload Content -->
        <div v-if="currentStep === 2" class="bg-gray-800 rounded-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">
            {{ uploadType === 'album' ? 'Album Details & Content' : 'Upload Content' }}
          </h2>
  
          <!-- Album Details -->
          <div v-if="uploadType === 'album'" class="mb-8">
            <div class="grid grid-cols-2 gap-6 mb-6">
              <edit-form
                v-else
                :object-type="objectType"
                :object="object"
              />
            </div>
            
            <!-- Album Cover Upload -->
            <div class="mb-6">
              <label class="block mb-2">Album Cover*</label>
              <div 
                @dragover.prevent
                @drop.prevent="handleCoverDrop"
                class="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-white transition-colors"
                :class="{'border-white bg-gray-700': isDraggingCover}"
                @dragenter="isDraggingCover = true"
                @dragleave="isDraggingCover = false"
              >
                <div v-if="albumDetails.cover">
                  <img 
                    :src="albumDetails.coverPreview" 
                    class="w-48 h-48 object-cover mx-auto rounded-lg mb-4"
                  />
                  <button 
                    @click.prevent="removeCover"
                    class="text-red-400 hover:text-red-300"
                  >
                    Remove Cover
                  </button>
                </div>
                <div v-else>
                  <i class="image icon" />
                  <p class="text-gray-400">Drag and drop your album cover here or click to browse</p>
                  <input 
                    type="file"
                    @change="handleCoverSelect"
                    accept="image/*"
                    class="hidden"
                    ref="coverInput"
                  />
                  <button 
                    @click="$refs.coverInput.click()"
                    class="mt-4 px-4 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    Browse Files
                  </button>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Content Upload -->
          <div>
            <label class="block mb-2">Upload Content*</label>
            <div 
              @dragover.prevent
              @drop.prevent="handleContentDrop"
              class="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-white transition-colors"
              :class="{'border-white bg-gray-700': isDragging}"
              @dragenter="isDragging = true"
              @dragleave="isDragging = false"
            >
              <div v-if="uploadedFiles.length === 0">
                <i class="image icon" />
                <p class="text-gray-400 mb-4">Drag and drop your files here or click to browse</p>
                <div class="bg-gray-700 rounded-lg p-4 mb-4 mx-auto max-w-lg">
                  <h4 class="font-semibold mb-2">File Requirements:</h4>
                  <div class="text-sm text-gray-400 text-left">
                    <p class="mb-2">For audio:</p>
                    <ul class="list-disc list-inside mb-2">
                      <li>File type: WAV, FLAC, AIFF</li>
                      <li>Bit depth: 16-bit min</li>
                      <li>Sample rate: 44.1 kHz min</li>
                    </ul>
                    <p class="mb-2">For video:</p>
                    <ul class="list-disc list-inside">
                      <li>File type: MP4</li>
                      <li>Highest resolution :)</li>
                    </ul>
                  </div>
                </div>
                <input 
                  type="file"
                  @change="handleFileSelect"
                  accept="audio/*,video/*"
                  multiple
                  class="hidden"
                  ref="fileInput"
                />
                <button 
                  @click="$refs.fileInput.click()"
                  class="px-4 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Browse Files
                </button>
              </div>
              <div v-else class="space-y-4">
                <div 
                  v-for="(file, index) in uploadedFiles" 
                  :key="index"
                  class="bg-gray-700 rounded-lg p-4 flex items-center justify-between"
                >
                  <div class="flex items-center">
                    <i class="music icon" />
                    <div>
                      <p class="font-medium">{{ file.name }}</p>
                      <p class="text-sm text-gray-400">{{ formatFileSize(file.size) }}</p>
                    </div>
                  </div>
                  <div class="flex items-center space-x-4">
                    <div v-if="file.progress < 100" class="w-24">
                      <div class="h-2 bg-gray-600 rounded-full">
                        <div 
                          class="h-2 bg-white rounded-full transition-all duration-300"
                          :style="{ width: `${file.progress}%` }"
                        ></div>
                      </div>
                    </div>
                    <button 
                      @click="removeFile(index)"
                      class="text-red-400 hover:text-red-300"
                    >
                    <i class="remove icon" />
                    </button>
                  </div>
                </div>
                <button 
                  @click="$refs.fileInput.click()"
                  class="px-4 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Add More Files
                </button>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Step 3: Track Details -->
        <div v-if="currentStep === 3" class="bg-gray-800 rounded-lg p-8 mb-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold">Track Details</h2>
            <div v-if="uploadedFiles.length > 1" class="flex items-center space-x-4">
              <button 
                @click="previousTrack"
                :disabled="currentTrackIndex === 0"
                class="p-2 rounded-lg hover:bg-gray-700 disabled:opacity-50"
              >
                <i class="left icon" />
              </button>
              <span>Track {{ currentTrackIndex + 1 }} of {{ uploadedFiles.length }}</span>
              <button 
                @click="nextTrack"
                :disabled="currentTrackIndex === uploadedFiles.length - 1"
                class="p-2 rounded-lg hover:bg-gray-700 disabled:opacity-50"
              >
                <i class="right icon" />
              </button>
            </div>
          </div>
  
          <!-- Track Form -->
          <div class="grid grid-cols-2 gap-6">
            <!-- Basic Info -->
            <div class="space-y-4">
              <div>
                <label class="block mb-2">Track Name*</label>
                <input 
                  v-model="currentTrack.name"
                  type="text"
                  class="w-full bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
                  placeholder="Enter track name"
                />
              </div>
              <div>
                <label class="block mb-2">Description</label>
                <textarea
                  v-model="currentTrack.description"
                  class="w-full bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
                  placeholder="Enter track description"
                  rows="3"
                ></textarea>
              </div>
              <div>
                <label class="block mb-2">Category*</label>
                <select 
                  v-model="currentTrack.category"
                  class="w-full bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
                >
                  <option value="">Select category</option>
                  <option v-for="category in categories" :key="category" :value="category">
                    {{ category }}
                  </option>
                </select>
              </div>
            </div>
  
            <!-- Metadata -->
            <div class="space-y-4">
              <div>
                <label class="block mb-2">Genre*</label>
                <SearchableSelect
                  v-model="currentTrack.genre"
                  :options="genres"
                  placeholder="Select or add genre"
                  allow-new
                />
              </div>
              <div>
                <label class="block mb-2">Featured Instruments*</label>
                <SearchableSelect
                  v-model="currentTrack.featuredInstruments"
                  :options="instruments"
                  placeholder="Select or add instruments"
                  multiple
                  allow-new
                />
              </div>
              <div>
                <label class="block mb-2">Primary Instrument</label>
                <SearchableSelect
                  v-model="currentTrack.primaryInstrument"
                  :options="instruments"
                  placeholder="Select or add primary instrument"
                  allow-new
                />
              </div>
            </div>
  
            <!-- Additional Metadata -->
            <div class="col-span-2 grid grid-cols-2 gap-6">
              <div>
                <label class="block mb-2">Language*</label>
                <SearchableSelect
                  v-model="currentTrack.languages"
                  :options="languages"
                  placeholder="Select or add languages"
                  multiple
                  allow-new
                />
              </div>
              <div>
                <label class="block mb-2">Tradition</label>
                <SearchableSelect
                  v-model="currentTrack.traditions"
                  :options="traditions"
                  placeholder="Select or add traditions"
                  multiple
                  allow-new
                />
              </div>
              <div>
                <label class="block mb-2">Deity</label>
                <SearchableSelect
                  v-model="currentTrack.deities"
                  :options="deities"
                  placeholder="Select or add deities"
                  multiple
                  allow-new
                />
              </div>
              <div>
                <label class="block mb-2">Intention</label>
                <SearchableSelect
                  v-model="currentTrack.intentions"
                  :options="intentions"
                  placeholder="Select or add intentions"
                  multiple
                  allow-new
                />
              </div>
              <div>
                <label class="block mb-2">Mood</label>
                <SearchableSelect
                  v-model="currentTrack.moods"
                  :options="moods"
                  placeholder="Select or add moods"
                  multiple
                  allow-new
                />
              </div>
              <div>
                <label class="block mb-2">Tags (max 5)</label>
                <SearchableSelect
                  v-model="currentTrack.tags"
                  :options="tags"
                  placeholder="Select or add tags"
                  multiple
                  :max-items="5"
                  allow-new
                />
              </div>
            </div>
  
            <!-- Vocals Section -->
            <div class="col-span-2">
              <h3 class="text-lg font-semibold mb-4">Vocals*</h3>
              <div class="grid grid-cols-3 gap-4">
                <div v-for="(option, key) in vocalOptions" :key="key" class="flex items-center space-x-2">
                  <input
                    :id="key"
                    type="checkbox"
                    v-model="currentTrack.vocals[key]"
                    class="w-4 h-4 rounded border-gray-600 text-white focus:ring-2 focus:ring-white"
                    @change="handleVocalChange(key)"
                  />
                  <label :for="key">{{ option }}</label>
                </div>
              </div>
            </div>
  
            <!-- Additional Details -->
            <div class="col-span-2 grid grid-cols-2 gap-6">
              <div>
                <label class="block mb-2">Record Label</label>
                <input 
                  v-model="currentTrack.recordLabel"
                  type="text"
                  class="w-full bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
                  placeholder="Enter record label"
                />
              </div>
              <div>
                <label class="block mb-2">Recording Country</label>
                <SearchableSelect
                  v-model="currentTrack.recordingCountry"
                  :options="countries"
                  placeholder="Select recording country"
                  allow-new
                />
              </div>
              <div>
                <label class="block mb-2">Release Date</label>
                <input 
                  v-model="currentTrack.releaseDate"
                  type="date"
                  class="w-full bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
                />
              </div>
            </div>
          </div>
        </div>
  
        <!-- Navigation Buttons -->
        <div class="flex justify-between">
          <button 
            v-if="currentStep > 1"
            @click="previousStep"
            class="px-6 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
          >
            Previous
          </button>
          <button 
            v-if="currentStep < 3"
            @click="nextStep"
            class="px-6 py-2 bg-white text-black rounded-lg hover:bg-gray-200 transition-colors ml-auto"
            :disabled="!canProceed"
          >
            Next
          </button>
          <button 
            v-else
            @click="submitUpload"
            class="px-6 py-2 bg-white text-black rounded-lg hover:bg-gray-200 transition-colors ml-auto"
            :disabled="!isValid"
          >
            Publish
          </button>
        </div>
      </div>
    </div>
  </template>