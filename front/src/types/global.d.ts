/// <reference types="vite/client" />
/// <reference types="vue/ref-macros" />
/// <reference types="vuex" />
/// <reference types="@vue/runtime-core" />

import type { Store } from 'vuex'
import type { RouteLocationNormalizedLoaded, Router } from 'vue-router'
import type { RootState } from '~/store/types'

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $store: Store<RootState>
    $router: Router
    $route: RouteLocationNormalizedLoaded
  }
}

// Vuex module augmentation
declare module 'vuex' {
  export * from 'vuex/types/index.d.ts'
  export * from 'vuex/types/helpers.d.ts'
  export * from 'vuex/types/logger.d.ts'
  export * from 'vuex/types/vue.d.ts'
}

// Environment variables
interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  // more env variables...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// Lucide icons
declare module 'lucide-vue-next' {
  import type { FunctionComponent, SVGAttributes } from 'vue'
  
  export const HeartIcon: FunctionComponent<SVGAttributes>
  export const PlayIcon: FunctionComponent<SVGAttributes>
  export const GlobeIcon: FunctionComponent<SVGAttributes>
  export const InstagramIcon: FunctionComponent<SVGAttributes>
  export const YoutubeIcon: FunctionComponent<SVGAttributes>
  export const FacebookIcon: FunctionComponent<SVGAttributes>
}
