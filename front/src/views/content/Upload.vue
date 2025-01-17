<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

import { useStore } from '~/store'

import AttachmentInput from '~/components/common/AttachmentInput.vue'


const store = useStore();


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

console.log(store.state.auth.user);

// Album details
const albumDetails = ref({
  title: '',
  description: {text: '', content_type: 'text/plain'},
  cover: null
})

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
      return !!albumDetails.value.title && !!albumDetails.value.cover && uploadedFiles.value.length > 0
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

const submitUpload = async () => {
  console.log('Submitting upload:', {
    uploadType: uploadType.value,
    albumDetails: uploadType.value === 'album' ? albumDetails.value : null,
    tracks: tracksMetadata.value
  });

  if (uploadType.value === 'album') {
    try {
      de
      albumDetails.value.artist = store.state.auth.profile.id;
      console.log('Uploading album:', albumDetails.value);
      const response = await axios.post('albums', albumDetails.value);
    } catch (error) {
      //errors.value = (error as BackendError).backendErrors
      console.log(error)
    }
  }
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
           <!-- find componenet for this -->
          <div v-if="uploadType === 'album'" class="mb-8">
            <div class="grid grid-cols-2 gap-6 mb-6">
              <div>
                <label class="block mb-2">Album Title*</label>
                <input 
                  v-model="albumDetails.title"
                  type="text"
                  class="w-full bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
                  placeholder="Enter album title"
                />
              </div>
              <div>
                <label class="block mb-2">Album Description</label>
                <textarea
                  v-model="albumDetails.description.text"
                  class="w-full bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
                  placeholder="Enter album description"
                  rows="3"
                ></textarea>
              </div>
            </div>
            
            <!-- Album Cover Upload -->
            <div class="mb-6">
              <label class="block mb-2">Album Cover*</label>
              <div 
                @dragover.prevent
                class="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-white transition-colors"
                :class="{'border-white bg-gray-700': isDraggingCover}"
                @dragenter="isDraggingCover = true"
                @dragleave="isDraggingCover = false"
              >
                <attachment-input
                  v-model="albumDetails.cover"
                  imageClass="podcast">
                </attachment-input>
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
                  accept="audio/wav, audio/flac, audio/aiff, video/mp4"
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
                <!-- need tag component -->
              </div>
              <div>
                <label class="block mb-2">Featured Instruments*</label>
                <!-- need tag component -->
              </div>
              <div>
                <label class="block mb-2">Primary Instrument</label>
                <!-- need tag component -->
              </div>
            </div>
  
            <!-- Additional Metadata -->
            <div class="col-span-2 grid grid-cols-2 gap-6">
              <div>
                <label class="block mb-2">Language*</label>
                <!-- need tag component -->
              </div>
              <div>
                <label class="block mb-2">Tradition</label>
                <!-- need tag component -->
              </div>
              <div>
                <label class="block mb-2">Deity</label>
                <!-- need tag component -->
              </div>
              <div>
                <label class="block mb-2">Intention</label>
                <!-- need tag component -->
              </div>
              <div>
                <label class="block mb-2">Mood</label>
                <!-- need tag component -->
              </div>
              <div>
                <label class="block mb-2">Tags (max 5)</label>
                <!-- need tag component -->
              </div>
            </div>
  
            <!-- Vocals Section -->
            <div class="col-span-2">
              <h3 class="text-lg font-semibold mb-4">Vocals*</h3>
              <div class="grid grid-cols-3 gap-4">
                <!-- need tag component here-->>
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
                <!-- need tag component -->
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