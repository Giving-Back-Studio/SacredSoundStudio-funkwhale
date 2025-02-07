import type { Module } from 'vuex'
import type { RootState } from './types'
import axios from 'axios'

interface ErrorResponse {
  response?: {
    data?: {
      detail?: string
    }
  }
}

export interface Artist {
  id: number
  name: string
  description?: {
    content: string
  }
  attachment_cover?: {
    urls: {
      original: string
    }
  }
  channel?: {
    actor?: {
      avatar?: {
        urls: {
          original: string
        }
      }
      urls?: Array<{
        type: string
        url: string
      }>
    }
  }
  albums?: Album[]
}

export interface Album {
  id: number
  title: string
  type: 'album' | 'single'
  release_date?: string
  attachment_cover?: {
    urls: {
      original: string
    }
  }
}

export interface ArtistsState {
  currentArtist: Artist | null
  isLoading: boolean
  error: string | null
}

const state: ArtistsState = {
  currentArtist: null,
  isLoading: false,
  error: null
}

const artists: Module<ArtistsState, RootState> = {
  namespaced: true,
  state,
  mutations: {
    SET_CURRENT_ARTIST(state, artist: Artist) {
      state.currentArtist = artist
    },
    SET_LOADING(state, isLoading: boolean) {
      state.isLoading = isLoading
    },
    SET_ERROR(state, error: string | null) {
      state.error = error
    }
  },
  actions: {
    async fetchOne({ commit }, id: string | number) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      try {
        const response = await axios.get(`/api/v1/artists/${id}/`)
        commit('SET_CURRENT_ARTIST', response.data)
        return response.data
      } catch (error: unknown) {
        const err = error as ErrorResponse
        const message = err.response?.data?.detail || 'Error fetching artist'
        commit('SET_ERROR', message)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    }
  },
  getters: {
    currentArtist: state => state.currentArtist,
    isLoading: state => state.isLoading,
    error: state => state.error
  }
}

export default artists
