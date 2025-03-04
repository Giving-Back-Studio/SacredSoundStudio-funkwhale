import { createEventHook, refDefault, type EventHookOn, useEventListener } from '@vueuse/core'
import { effectScope, reactive, ref, type Ref } from 'vue'
import useLogger from '~/composables/useLogger'

const logger = useLogger()

export interface VideoSource {
  uuid: string
  mimetype: string
  url: string
}

export interface Video {
  preload(): Promise<void>
  dispose(): Promise<void>

  readonly isErrored: Ref<boolean>
  readonly isLoaded: Ref<boolean>
  readonly isDisposed: Ref<boolean>
  readonly currentTime: number
  readonly playable: boolean
  readonly duration: number
  readonly buffered: number
  looping: boolean
  muted: boolean

  pause(): Promise<void>
  play(): Promise<void>

  seekTo(seconds: number): Promise<void>
  seekBy(seconds: number): Promise<void>

  onVideoEnd: EventHookOn<Video>
  onSoundLoop: EventHookOn<Video>
}

export const videoImplementations = reactive(new Set<Constructor<Video>>())

export const registerVideoImplementation = <T extends Constructor<Video>>(implementation: T) => {
  videoImplementations.add(implementation)
  return implementation
}

// Default Video implementation
@registerVideoImplementation
export class HTMLVideo implements Video {
  #video = document.getElementById('video-delivery')?.appendChild(document.createElement('video')) || document.createElement('video')

  #videoEndEventHook = createEventHook<HTMLVideo>()
  #ignoreError = false
  #scope = effectScope()

  readonly isErrored = ref(false)
  readonly isLoaded = ref(false)
  readonly isDisposed = ref(false)

  onVideoEnd: EventHookOn<HTMLVideo>
  onSoundLoop: EventHookOn<HTMLVideo>

  constructor(sources: VideoSource[]) {
    this.onVideoEnd = this.#videoEndEventHook.on
    this.onSoundLoop = this.#videoEndEventHook.on
    const source = sources[0]?.url
    if (!source) {
      this.isLoaded.value = true
      return
    }

    this.#video.crossOrigin = 'anonymous'
    this.#video.src = source
    this.#video.preload = 'auto'
    this.#video.controls = true
    this.#video.controlsList = 'nodownload'

    logger.log('CREATED VIDEO INSTANCE', this)

    this.#scope.run(() => {
      useEventListener(this.#video, 'ended', () => this.#videoEndEventHook.trigger(this))
      useEventListener(this.#video, 'loadeddata', () => {
        this.isLoaded.value = this.#video.readyState >= 2
      })
      useEventListener(this.#video, 'error', (err) => {
        if (this.#ignoreError) return
        logger.error('>> VIDEO ERRORED', err, this)
        this.isErrored.value = true
        this.isLoaded.value = true
      })
    })
  }

  async preload() {
    this.isDisposed.value = false
    this.isErrored.value = false
    logger.log('CALLING VIDEO PRELOAD ON', this)
    this.#video.load()
  }

  async dispose() {
    if (this.isDisposed.value) return

    this.#scope.stop()
    this.#video.pause()
    this.#video.src = ''
    this.#video.load()
    this.isDisposed.value = true
  }

  async play() {
    try {
      await this.#video.play()
    } catch (err) {
      logger.error('>> VIDEO PLAY ERROR', err, this)
      this.isErrored.value = true
    }
  }

  async pause() {
    return this.#video.pause()
  }

  async seekTo(seconds: number) {
    this.#video.currentTime = seconds
  }

  async seekBy(seconds: number) {
    this.#video.currentTime += seconds
  }

  get playable() {
    return this.#video.src !== '' || this.isErrored.value
  }

  get duration() {
    const { duration } = this.#video
    return isNaN(duration) ? 0 : duration
  }

  get buffered() {
    if (this.duration > 0) {
      const { length } = this.#video.buffered
      for (let i = 0; i < length; i++) {
        if (this.#video.buffered.start(length - 1 - i) < this.#video.currentTime) {
          return this.#video.buffered.end(length - 1 - i)
        }
      }
    }
    return 0
  }

  get currentTime() {
    return this.#video.currentTime
  }

  get looping() {
    return this.#video.loop
  }

  set looping(value: boolean) {
    this.#video.loop = value
  }

  get muted() {
    return this.#video.muted
  }

  set muted(value: boolean) {
    this.#video.muted = value
  }
}

export const videoImplementation = refDefault(ref<Constructor<Video>>(), HTMLVideo)
