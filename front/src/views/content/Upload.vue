<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { useCookies } from '@vueuse/integrations/useCookies'
import { useRouter } from 'vue-router'

import { useStore } from '~/store'
import useLogger from '~/composables/useLogger'
import useErrorHandler from '~/composables/useErrorHandler'

import AttachmentInput from '~/components/common/AttachmentInput.vue'
import TagCategorySelector from '~/components/library/TagCategorySelector.vue'
import TrackCategoryTags from '~/components/content/TrackCategoryTags.vue'
import FileUploadWidget from '~/components/library/FileUploadWidget.vue'
import SemanticModal from '~/components/semantic/Modal.vue'
import content from '~/router/routes/content'
import { Music4Icon, Music2Icon, UploadCloudIcon } from 'lucide-vue-next'


const store = useStore();
const logger = useLogger();
const getCookie = useCookies();
const router = useRouter();

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
const upload = ref()
const showSuccessModal = ref(false);

console.log(store.state.auth.user);

// Album details
const albumDetails = ref({
  title: '',
  description: {text: '', content_type: 'text/plain'},
  cover: null
})

// Track template
const createTrackTemplate = (file) => ({
  title: file ? file.file.name.split('.')[0]: '',
  description: '',
  categoryTags: new Proxy({}, {
    get: (target, name) => name in target ? target[name] : []
  }),
  recordLabel: '',
  releaseDate: '',
  file: file,
  cover: null
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

const isReadyToPublish = computed(() => {
  for (let i = 0; i < uploadedFiles.value.length; i++) {
    if (!uploadedFiles.value[i].response.uuid) {
      return false;
    }
    const track = tracksMetadata.value[i];
    if (!track.title) {
      return false;
    }
  }

  return true;
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

  const artistId = store.state.auth.profile.artist;
  let albumId = null;

  if (uploadType.value === 'album') {
    try {
      albumDetails.value.artist = artistId;
      const response = await axios.post('albums', albumDetails.value);

      albumId = response.data.id;
    } catch (error) {
      //errors.value = (error as BackendError).backendErrors
      console.log(error)
    }
  }
  
  let uploadPromises = [];
  for (let i = 0; i < uploadedFiles.value.length; i++) {
    const track = tracksMetadata.value[i];
    const trackData = {
      title: track.title,
      description: {
        text: track.description,
        content_type: 'text/plain'
      },
      record_label: track.recordLabel,
      release_date: track.releaseDate,
      album: albumId,
      artist: artistId,
      upload: uploadedFiles.value[i].response.uuid
    };

    if (uploadType.value !== 'album') {
      trackData.cover = track.cover;
    }

    const tags = [];
    for (const category in track.categoryTags) {
      for (const tag of track.categoryTags[category]) {
        tags.push({tag: tag, tag_category: category});
      }
    }
    trackData.tagged_items = tags;
    uploadPromises.push(axios.post('tracks', trackData));
  }
  Promise.all(uploadPromises).then(responses => {
    showSuccessModal.value = true;
  });
}

const library = ref()
const fetchLibrary = async () => {
  const measureLoading = logger.time('Fetching library')
  try {
    const response = await axios.get('libraries/?scope=me')
    library.value = response.data.results[0]
  } catch (error) {
    useErrorHandler(error)
    library.value = undefined
  } finally {
    measureLoading()
  }
}
fetchLibrary()

const uploadData = computed(() => ({
  library: library.value ? library.value.uuid: null,
  import_status: 'draft'
  }
))

const inputFile = (newFile) => {
  if (!newFile) return
  newFile.active = true
  tracksMetadata.value.push(createTrackTemplate(newFile))
}

const goToMyContent = () => {
  router.push('/mycontent');
}

</script>

<template>
    <div class="min-h-screen main with-background text-primary p-6">
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
                  class="w-10 h-10 rounded-full flex items-center justify-center z-10 step-circle"
                  :class="currentStep >= step.number ? 'active' : 'border-2 border-gray-600'"
                >
                  {{ step.number }}
                </div>
                <div 
                  class="absolute -bottom-6 w-full text-center text-sm"
                >
                  {{ step.title }}
                </div>
              </div>
              <div 
                v-if="step.number < steps.length" 
                class="absolute top-5 -right-1/2 w-full h-0.5 z-0"
                :class="currentStep > step.number ? 'bg-primary' : 'bg-white'"
              ></div>
            </div>
          </div>
        </div>
  
        <!-- Step 1: Choose Upload Type -->
        <div v-if="currentStep === 1" class="rounded-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">Choose Upload Type</h2>
          <div class="grid grid-cols-2 gap-6">
            <button 
              @click="selectUploadType('album')"
              class="upload-type-button p-6 rounded-lg text-center"
              :class="{ 'selected': uploadType === 'album' }"
            >
              <Music4Icon class="w-8 h-8 mx-auto mb-2" />
              <h3 class="text-xl font-semibold">Album Upload</h3>
              <p class="text-gray-400 mt-2">Upload multiple tracks as an album</p>
            </button>
            <button 
              @click="selectUploadType('individual')"
              class="upload-type-button p-6 rounded-lg text-center"
              :class="{ 'selected': uploadType === 'individual' }"
            >
              <Music2Icon class="w-8 h-8 mx-auto mb-2" />
              <h3 class="text-xl font-semibold">Individual Upload</h3>
              <p class="text-gray-400 mt-2">Upload single or multiple tracks</p>
            </button>
          </div>
        </div>
  
        <!-- Step 2: Upload Content -->
        <div
          class="rounded-lg p-8 mb-6"
          :class="currentStep === 2 ? '' : 'hidden'"
        >
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
                  class="w-full rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
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
                class="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-primary transition-colors"
                :class="{'border-white bg-gray-700': isDraggingCover}"
                @dragenter="isDraggingCover = true"
                @dragleave="isDraggingCover = false"
              >
                <attachment-input
                  v-model="albumDetails.cover"
                  name="cover"
                  imageClass="podcast">
                </attachment-input>
              </div>
              <label for="cover"></label>
            </div>
          </div>
  
          <!-- Content Upload -->
          <div
          @dragover.prevent
          @drop.prevent="handleContentDrop"
          class="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-primary transition-colors"
          :class="{'border-white bg-gray-700': isDragging}"
          @dragenter="isDragging = true"
          @dragleave="isDragging = false"
          >
            <form @submit.stop.prevent>
              <file-upload-widget
                ref="upload"
                v-model="uploadedFiles"
                :class="['ui', 'icon', 'basic', 'w-full']"
                :data="uploadData"
                accept=".wav,.flac,.aiff,.mp4"
                @input-file="inputFile"
              >
            <div>
              <div v-if="uploadedFiles.length === 0">
                <UploadCloudIcon class="w-16 h-16 mx-auto mb-4" />
                <div class="file-requirements rounded-lg p-4 mb-4 mx-auto max-w-lg">
                  <h4 class="font-semibold mb-2">File Requirements:</h4>
                  <div class="text-sm text-left">
                    <p class="mb-2">For audio:</p>
                    <ul class="list-disc list-inside mb-2">
                      <li>File type: WAV, FLAC, AIFF</li>
                      <li>Bit depth: 16-bit min</li>
                      <li>Sample rate: 44.1 kHz min</li>
                    </ul>
                    <p class="mb-2">For video:</p>
                    <ul class="list-disc list-inside">
                      <li>Coming Soon!</li>
                    </ul>
                  </div>
                </div>

                  <button class="ui primary button">
                    Browse Files
                  </button>
              </div>
              <div v-else class="space-y-4">
                <div 
                  v-for="(file, index) in uploadedFiles" 
                  :key="index"
                  class="bg-gray-200 rounded-lg p-4 flex items-center justify-between"
                >
                  <div class="flex items-center">
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
                <button class="ui primary button">
                  Add More Files
                </button>
              </div>
            </div>
          </file-upload-widget>
          </form>
          </div>
          <span class="text-primary text-sm">
            We'll upload your magic while you tell us a little bit more about it.
            Click Next to describe and categorize your content.
          </span>
        </div>
  
        <!-- Step 3: Track Details -->
        <div v-if="currentStep === 3" class="rounded-lg p-8 mb-6">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold">Track Details</h2>
            <span class="text-gray-400 text-sm">{{ currentTrack.file.file.name }}</span>
            <div v-if="uploadedFiles.length > 1" class="flex items-center space-x-4">
              <button 
                @click="previousTrack"
                :disabled="currentTrackIndex === 0"
                class="p-2 rounded-lg hover:bg-gray-700 disabled:opacity-50"
              >
                <i class="left arrow icon" />
              </button>
              <span>Track {{ currentTrackIndex + 1 }} of {{ uploadedFiles.length }}</span>
              <button 
                @click="nextTrack"
                :disabled="currentTrackIndex === uploadedFiles.length - 1"
                class="p-2 rounded-lg hover:bg-gray-700 disabled:opacity-50"
              >
                <i class="right arrow icon" />
              </button>
            </div>
          </div>
  
          <!-- Track Form -->
          <div class="grid grid-cols-2 gap-6">
            <!-- Basic Info -->
            <div>
              <label class="block mb-2">Track Title *</label>
              <input 
                v-model="currentTrack.title"
                type="text"
                class="w-full bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
                placeholder="Enter track title"
              />
            </div>

            <div>
              <label class="block mb-2">Description</label>
              <textarea
                v-model="currentTrack.description"
                class="w-full rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
                placeholder="Enter track description"
                rows="3"
              ></textarea>
            </div>

            <div v-if="uploadType !== 'album'" class="col-span-2">
              <label class="block mb-2">Track Cover</label>
              <div
                @dragover.prevent
                class="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-primary transition-colors"
                :class="{'border-white bg-gray-700': isDraggingCover}"
                @dragenter="isDraggingCover = true"
                @dragleave="isDraggingCover = false"
              >
                <attachment-input
                  v-model="currentTrack.cover"
                  name="cover"
                  imageClass="podcast">
                </attachment-input>
              </div>
              <label for="cover"></label>
            </div>

            <!-- Category Tags -->
            <track-category-tags
              v-model="currentTrack.categoryTags"
              class="col-span-2"
            />

            <!-- Additional Details -->
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
              <label class="block mb-2">Release Date</label>
              <input 
                v-model="currentTrack.releaseDate"
                type="text"
                class="w-full bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-white"
                placeholder="Enter release date"
              />
            </div>
          </div>
        </div>
  
        <!-- Navigation Buttons -->
        <div class="flex justify-end gap-4 mt-6">
          <div class="flex gap-4 ml-auto">
            <button 
              v-if="currentStep > 1"
              @click="previousStep"
              class="ui button secondary px-6"
            >
              Previous
            </button>
            <button 
              v-if="currentStep < 3"
              @click="nextStep"
              class="ui button px-6"
              style="background-color: #434289; color: white;"
              :disabled="!canProceed"
            >
              Next
            </button>
            <div v-else>
              <button
                v-if="isReadyToPublish"
                @click="submitUpload"
                class="ui primary button px-6"
              >
                Publish
              </button>
              <button 
                v-else 
                class="ui primary button px-6" 
                disabled
              >
                Uploading...
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <semantic-modal v-model:show="showSuccessModal" @hide="goToMyContent">
      <header class="header">
        Success!
      </header>
      <section class="content centered text-black">
        <div>Thank you for uploading your magic!</div>
      </section>
    </semantic-modal>
  </template>

<style>
/* Add these new styles */
.i.music.icon::before {
  content: "\f001"; /* Semantic UI music icon unicode */
  font-family: Icons;
  font-style: normal;
}

.i.album.icon::before {
  content: "\f0c9"; /* Semantic UI list/album icon unicode */
  font-family: Icons;
  font-style: normal;
}

/* Add this to your existing styles */
.step-circle.active {
  background-color: var(--primary-color)!important;
  color: white!important;
}

/* Keep existing styles */
.main.with-background {
  background: var(--site-background) !important;
}

.text-primary {
  color: var(--primary-color) !important;
}

/* Keep the active step (number 1) with its current styling */
.step-1 .rounded-full {
  background: var(--primary-color) !important;
  color: white !important;
}

.upload-type-button {
  /* Reset button styles */
  background: transparent !important;
  color: inherit !important;
  border: 2px solid rgb(229, 231, 235) !important;
  transition: all 0.2s ease-in-out !important;
}

/* Hover state */
.upload-type-button:hover {
  border-color: var(--primary-color) !important;
}

/* Selected state */
.upload-type-button.selected {
  border-color: var(--primary-color) !important;
}

.hover\:border-primary:hover {
  border-color: var(--primary-color) !important;
}

.border-primary {
  border-color: var(--primary-color) !important;
}

/* File upload container styles */
.border-2.border-dashed{
  background: transparent !important;
  color: inherit !important;
  border: 2px dashed rgb(229, 231, 235) !important;
  transition: all 0.2s ease-in-out !important;
}

/* Hover state */
.border-2.border-dashed:hover {
  border-color: var(--primary-color) !important;
}

/* Selected/dragging state */
.border-2.border-dashed.border-primary,
.file-upload-widget .border-2.border-dashed.border-primary,
.component-file-upload .border-2.border-dashed.border-primary,
div[class*="border-2"][class*="border-dashed"].border-primary {
  border-color: var(--primary-color) !important;
}

/* File requirements box */
.file-requirements {
  background-color: var(--alternative-color) !important;
  color: white !important;
}

.file-requirements .text-gray-400 {
  color: rgba(255, 255, 255, 0.7) !important;
}

.upload-area {
  /* Reset and set initial styles */
  background: transparent !important;
  color: inherit !important;
  border: 2px dashed var(--primary-color) !important; 
  transition: all 0.2s ease-in-out !important;
  pointer-events: auto !important;
  cursor: pointer !important;
}

.bg-primary {
  background-color: var(--primary-color) !important;
}
</style>
