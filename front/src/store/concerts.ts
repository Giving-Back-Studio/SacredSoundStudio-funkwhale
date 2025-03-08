import type { Module } from 'vuex'
import type { RootState } from '~/store/index'
import axios from 'axios'

import type { Artist } from '~/types'

export interface Concert {
  id: number
  title: string
  description: string
  start_time: string
  end_time: string
  cover: string
  mux_playback_id: string | null
  mux_live_stream_id: string | null
  artist: Artist
}

export interface State {
  concerts: Concert[]
  featuredConcert: Concert | null
  nextConcerts: Concert[]
}

const store: Module<State, RootState> = {
  namespaced: true,
  state: {
    concerts: [],
    featuredConcert: null,
    nextConcerts: []
  },
  mutations: {
    setConcerts (state, concerts: Concert[]) {
      state.concerts = concerts
    },
    setFeaturedConcert (state, concert: Concert) {
      state.featuredConcert = concert
    },
    setNextConcerts (state, concerts: Concert[]) {
      state.nextConcerts = concerts
    },
    addConcert (state, concert: Concert) {
      state.concerts.push(concert)
    },
    updateConcert (state, updatedConcert: Concert) {
      const index = state.concerts.findIndex(concert => concert.id === updatedConcert.id)
      if (index !== -1) {
        state.concerts.splice(index, 1, updatedConcert)
      }
    },
    deleteConcert (state, concertId: number) {
      state.concerts = state.concerts.filter(concert => concert.id !== concertId)
    }
  },
  actions: {
    async fetchConcerts ({ commit }) {
      try {
        const response = await axios.get('/concerts/')
        const concerts = response.data.results
        commit('setConcerts', concerts)
        if (concerts.length > 0) {
          commit('setFeaturedConcert', concerts[0])
          commit('setNextConcerts', concerts.slice(1))
        }
      } catch (error) {
        console.error('Error fetching concerts:', error)
      }
    },
    async createConcert ({ commit }, concert: Concert) {
      try {
        const response = await axios.post('/concerts/', concert)
        commit('addConcert', response.data)
      } catch (error) {
        console.error('Error creating concert:', error)
      }
    },
    async updateConcert ({ commit }, concert: Concert) {
      try {
        const response = await axios.put(`/concerts/${concert.id}/`, concert)
        commit('updateConcert', response.data)
      } catch (error) {
        console.error('Error updating concert:', error)
      }
    },
    async deleteConcert ({ commit }, concertId: number) {
      try {
        await axios.delete(`/concerts/${concertId}/`)
        commit('deleteConcert', concertId)
      } catch (error) {
        console.error('Error deleting concert:', error)
      }
    }
  }
}

export default store
