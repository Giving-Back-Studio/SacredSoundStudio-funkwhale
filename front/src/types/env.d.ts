/// <reference types="vite/client" />

import type { Store } from '~/store/types'

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  readonly MODE: string
  readonly DEV: boolean
  readonly PROD: boolean
  readonly SSR: boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $store: Store
  }
}
