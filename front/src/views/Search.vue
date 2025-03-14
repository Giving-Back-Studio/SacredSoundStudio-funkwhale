<script setup lang="ts">
import type { RadioConfig } from '~/store/radios'

import { ref, reactive, computed, watch } from 'vue'
import { useRouteQuery } from '@vueuse/router'
import { useI18n } from 'vue-i18n'
import { syncRef } from '@vueuse/core'

import axios from 'axios'

import PlaylistCardList from '~/components/playlists/CardList.vue'
import RemoteSearchForm from '~/components/RemoteSearchForm.vue'
import ArtistCard from '~/components/audio/artist/Card.vue'
import TrackTable from '~/components/audio/track/Table.vue'
import AlbumCard from '~/components/audio/album/Card.vue'
import Pagination from '~/components/vui/Pagination.vue'
import RadioButton from '~/components/radios/Button.vue'
import RadioCard from '~/components/radios/Card.vue'
import TagsList from '~/components/tags/List.vue'

import useErrorHandler from '~/composables/useErrorHandler'
import useLogger from '~/composables/useLogger'

type QueryType = 'artists' | 'albums' | 'tracks' | 'playlists' | 'tags' | 'radios' | 'podcasts' | 'series' | 'rss'

const type = useRouteQuery<QueryType>('type', 'artists')
const id = useRouteQuery<string>('id')

const pageQuery = useRouteQuery<string>('page', '1')
const page = ref(+pageQuery.value)
syncRef(pageQuery, page, {
  transform: {
    ltr: (left) => +left,
    rtl: (right) => right.toString()
  },
  direction: 'both'
})

const logger = useLogger()

const q = useRouteQuery('q', '')
const query = ref(q.value)
syncRef(q, query, { direction: 'ltr' })

type ResponseType = { count: number, results: any[] }
const results = reactive({
  artists: null,
  albums: null,
  tracks: null,
  playlists: null,
  radios: null,
  tags: null,
  podcasts: null,
  series: null
} as Record<QueryType, null | ResponseType>)

const paginateBy = ref(25)

const { t } = useI18n()

interface SearchType {
  id: QueryType
  label: string
  includeChannels?: boolean
  contentCategory?: string
  endpoint?: string
}

const types = computed(() => [
  {
    id: 'artists',
    label: t('views.Search.label.artists'),
    includeChannels: true,
    contentCategory: 'music'
  },
  {
    id: 'albums',
    label: t('views.Search.label.albums'),
    includeChannels: true,
    contentCategory: 'music'
  },
  {
    id: 'tracks',
    label: t('views.Search.label.tracks')
  },
  {
    id: 'tags',
    label: t('views.Search.label.tags')
  },
] as SearchType[])

const currentType = computed(() => types.value.find(({ id }) => id === type.value))

const axiosParams = computed(() => {
  const params = new URLSearchParams({
    q: query.value,
    page: pageQuery.value,
    page_size: paginateBy.value as unknown as string
  })

  if (currentType.value?.contentCategory) params.append('content_category', currentType.value.contentCategory)
  if (currentType.value?.includeChannels) params.append('include_channels', currentType.value.includeChannels as unknown as string)

  return params
})

const currentResults = computed(() => results[currentType.value?.id ?? 'artists'])

const isLoading = ref(false)
const search = async () => {
  if (!currentType.value) return

  q.value = query.value

  if (!query.value) {
    for (const type of types.value) {
      results[type.id] = null
    }

    return
  }

  isLoading.value = true

  try {
    const response = await axios.get(currentType.value.endpoint ?? currentType.value.id, {
      params: axiosParams.value
    })

    results[currentType.value.id] = response.data
  } catch (error) {
    useErrorHandler(error as Error)
  }

  isLoading.value = false

  // TODO (wvffle): Resolve race condition
  for (const type of types.value) {
    if (type.id !== currentType.value.id) {
      axios.get(type.endpoint ?? type.id, {
        params: {
          q: query.value,
          page_size: 1,
          content_category: type.contentCategory,
          include_channels: type.includeChannels
        }
      }).then(response => {
        results[type.id] = response.data
      }).catch(() => undefined)
    }
  }
}

watch(type, () => {
  if (page.value === 1) return search()
  page.value = 1
})

// NOTE: When we watch `page`, the `pageQuery` value is never updated for some reason
watch(pageQuery, search)
search()

const labels = computed(() => ({
  title: id.value
    ? (
        type.value === 'rss'
          ? t('views.Search.header.rss')
          : t('views.Search.header.remote')
      )
    : t('views.Search.header.search'),
  submitSearch: t('views.Search.button.submit')
}))

const radioConfig = computed(() => {
  const results = Object.values(currentResults.value?.results ?? {})
  if (results.length) {
    switch (currentType.value?.id) {
      case 'tags':
        return {
          type: 'tag',
          names: results.map(({ name }) => name)
        } as RadioConfig

      case 'playlists':
      case 'artists':
        return {
          type: currentType.value.id.slice(0, -1),
          ids: results.map(({ id }) => id)
        } as RadioConfig
    }

    logger.warn('This type is not yet supported for radio')
  }

  return null
})
</script>

<template>
  <main
    v-title="labels.title"
    class="main pusher"
  >
    <section class="ui vertical stripe segment">
      <div
        v-if="id"
        class="ui small text container"
      >
        <h2>{{ labels.title }}</h2>
        <remote-search-form
          :initial-id="id"
          :initial-type="type === 'rss' ? 'rss' : 'artists'"
        />
      </div>
      <div
        v-else
        class="ui container"
      >
        <h2>
          <label for="query">
            {{ $t('views.Search.header.search') }}
          </label>
        </h2>
        <div class="ui two column doubling stackable grid container">
          <div class="column">
            <form
              class="ui form"
              @submit.prevent="page = 1; search()"
            >
              <div class="ui field">
                <div class="ui action input">
                  <input
                    id="query"
                    v-model="query"
                    class="ui input"
                    name="query"
                    type="text"
                  >
                  <button
                    :aria-label="labels.submitSearch"
                    type="submit"
                    class="ui icon button"
                  >
                    <i class="search icon" />
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
        <div class="ui secondary pointing menu">
          <a
            v-for="th in types"
            :key="th.id"
            :class="['item', {active: type === th.id}]"
            href=""
            @click.prevent="type = th.id"
          >
            {{ th.label }}
            <span
              v-if="results[th.id]"
              class="ui circular mini right floated label"
            >
              {{ results[th.id]?.count ?? 0 }}
            </span>
          </a>
        </div>
        <div v-if="isLoading">
          <div
            v-if="isLoading"
            class="ui inverted active dimmer"
          >
            <div class="ui loader" />
          </div>
        </div>

        <empty-state
          v-else-if="!currentResults || currentResults.count === 0"
          :refresh="true"
          @refresh="search"
        />

        <div
          v-else-if="type === 'artists' || type === 'podcasts'"
          class="ui five app-cards cards"
        >
          <artist-card
            v-for="artist in currentResults.results"
            :key="artist.id"
            :artist="artist"
          />
        </div>

        <div
          v-else-if="type === 'albums' || type === 'series'"
          class="ui five app-cards cards"
        >
          <album-card
            v-for="album in currentResults.results"
            :key="album.id"
            :album="album"
          />
        </div>
        <track-table
          v-else-if="type === 'tracks'"
          :tracks="currentResults.results"
        />
        <playlist-card-list
          v-else-if="type === 'playlists'"
          :playlists="currentResults.results"
        />
        <div
          v-else-if="type === 'radios'"
          class="ui cards"
        >
          <radio-card
            v-for="radio in currentResults.results"
            :key="radio.id"
            type="custom"
            :custom-radio="radio"
          />
        </div>
        <tags-list
          v-else-if="type === 'tags'"
          :truncate-size="200"
          :limit="paginateBy"
          :tags="currentResults.results.map(t => {return t.name })"
        />

        <pagination
          v-if="currentResults && currentResults.count > paginateBy"
          v-model:current="page"
          :paginate-by="paginateBy"
          :total="currentResults.count"
        />
      </div>
    </section>
  </main>
</template>
