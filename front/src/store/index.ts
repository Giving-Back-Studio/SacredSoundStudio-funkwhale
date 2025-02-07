import { createStore } from 'vuex'
import type { RootState, Store } from './types'
import artists from './artists'

const debug = import.meta.env.MODE !== 'production'

export const store = createStore<RootState>({
  strict: debug,
  modules: {
    artists
  }
})

export function useStore(): Store {
  return store
}

export default store

// Type augmentation for Vuex
declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $store: Store
  }
}
