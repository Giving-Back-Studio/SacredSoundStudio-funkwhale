import type { Store as VuexStore } from 'vuex'
import type { ArtistsState } from './artists'

// Root state type
export interface RootState {
  artists: ArtistsState
}

// Store type with proper typing
export type Store<S = RootState> = Omit<VuexStore<S>, 'commit' | 'dispatch'> & {
  commit<K extends keyof Mutations>(
    key: K,
    payload?: Parameters<Mutations[K]>[1]
  ): ReturnType<Mutations[K]>
  dispatch<K extends keyof Actions>(
    key: K,
    payload?: Parameters<Actions[K]>[1]
  ): Promise<ReturnType<Actions[K]>>
}

// Mutation types
export interface Mutations {
  'artists/SET_CURRENT_ARTIST': (state: RootState, artist: ArtistsState['currentArtist']) => void
  'artists/SET_LOADING': (state: RootState, isLoading: boolean) => void
  'artists/SET_ERROR': (state: RootState, error: string | null) => void
}

// Action types
export interface Actions {
  'artists/fetchOne': (store: Store, id: string | number) => Promise<ArtistsState['currentArtist']>
}
