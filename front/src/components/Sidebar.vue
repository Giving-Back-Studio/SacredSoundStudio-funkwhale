<script setup lang="ts">
import type { RouteRecordName } from 'vue-router'

import { computed, ref, watch, watchEffect, onMounted } from 'vue'
import { setI18nLanguage, SUPPORTED_LOCALES } from '~/init/locale'
import { useCurrentElement } from '@vueuse/core'
import { setupDropdown } from '~/utils/fomantic'
import { useRoute } from 'vue-router'
import { useStore } from '~/store'
import { useI18n } from 'vue-i18n'
import { Menu, Settings } from 'lucide-vue-next'

import SemanticModal from '~/components/semantic/Modal.vue'
import UserModal from '~/components/common/UserModal.vue'
import UserMenu from '~/components/common/UserMenu.vue'

import useThemeList from '~/composables/useThemeList'
import useTheme from '~/composables/useTheme'

interface Events {
  (e: 'show:set-instance-modal'): void
}

interface Props {
  width: number
}

const emit = defineEmits<Events>()
const props = defineProps<Props>()

const store = useStore()
const { theme } = useTheme()
const themes = useThemeList()
const { t, locale: i18nLocale } = useI18n()

const route = useRoute()

const additionalNotifications = computed(() => store.getters['ui/additionalNotifications'])
const logoUrl = computed(() => store.state.auth.authenticated ? 'library.index' : 'index')

const labels = computed(() => ({
  mainMenu: t('components.Sidebar.label.main'),
  selectTrack: t('components.Sidebar.label.play'),
  pendingFollows: t('components.Sidebar.label.follows'),
  pendingReviewEdits: t('components.Sidebar.label.edits'),
  pendingReviewReports: t('components.Sidebar.label.reports'),
  language: t('components.Sidebar.label.language'),
  theme: t('components.Sidebar.label.theme'),
  addContent: t('components.Sidebar.label.add'),
  administration: t('components.Sidebar.label.administration')
}))

const ROUTE_MAPPINGS = {
  library: ['library.index', 'library.albums.browse', 'library.artists.browse', 'library.tracks.browse'],
  myContent: ['library.me', 'library.albums.me', 'library.artists.me', 'library.playlists.me'],
  myChannel: ['channels.me', 'channels.detail'],
  adminland: ['manage.library.edits', 'manage.moderation.reports.list', 'manage.users.users.list'],
  upload: ['content.index']
}

const moderationNotifications = computed(() =>
  store.state.ui.notifications.pendingReviewEdits
    + store.state.ui.notifications.pendingReviewReports
    + store.state.ui.notifications.pendingReviewRequests
)

const showLanguageModal = ref(false)
const locale = ref(i18nLocale.value)
watch(locale, (locale) => {
  setI18nLanguage(locale)
})

const isProduction = import.meta.env.PROD
const showUserModal = ref(false)
const showThemeModal = ref(false)

const el = useCurrentElement()
watchEffect(() => {
  if (store.state.auth.authenticated) {
    setupDropdown('.admin-dropdown', el.value)
  }
  
  setupDropdown('.user-dropdown', el.value, {
    action: 'click',
    direction: 'downward',
    transition: 'dropdown',
    on: 'click',
    // Adding these to modify the user menu for beta:
    closable: true,
    allowCategorySelection: false,
    selectOnKeydown: false,
    forceSelection: false,
    hideAdditions: true,
    match: 'none',
    // Add these new options to restrict menu items
    useLabels: false,
    maxSelections: 0,
    showOnFocus: false,
    apiSettings: false,
    saveRemoteData: false,
    useSearch: false,
    fullTextSearch: false
  })
})

onMounted(() => {
  document.getElementById('fake-sidebar')?.classList.add('loaded')
})

const shouldHideSidebar = computed(() => {
  const hiddenRoutes = ['', '/', '/create', '/auth']
  const shouldHide = hiddenRoutes.includes(route.path)
  document.getElementById('main')?.classList.toggle('no-sidebar', shouldHide)
  return shouldHide
})

// Add ref for tracking sidebar collapse state
const isSidebarCollapsed = ref(false)

// Add function to toggle sidebar
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  emit('update:collapsed', isSidebarCollapsed.value)
}

watch(() => props.width, (width) => {
  if (width < 1024 && !isSidebarCollapsed.value) {
    toggleSidebar()
  }
})
</script>

<template>
  <aside
    v-if="!shouldHideSidebar"
    :class="['ui', 'vertical', 'left', 'visible', 'wide', 'sidebar', 'component-sidebar', { collapsed: isSidebarCollapsed }]"
  >
    <header class="ui basic segment header-wrapper">
      <Menu class="menu-icon" @click="toggleSidebar" />
      <div class="spacer"></div>
      <nav class="top ui compact right aligned inverted text menu">
        <div class="right menu">
          <div
            v-if="$store.state.auth.availablePermissions['settings'] || $store.state.auth.availablePermissions['moderation']"
            class="item"
            :title="labels.administration"
          >
            <div class="item ui inline admin-dropdown dropdown">
              <Settings class="wrench icon" />
              <div
                v-if="moderationNotifications > 0"
                :class="['ui', 'accent', 'mini', 'bottom floating', 'circular', 'label']"
              >
                {{ moderationNotifications }}
              </div>
              <div class="menu">
                <h3 class="header">
                  {{ $t('components.Sidebar.header.administration') }}
                </h3>
                <div class="divider" />
                <router-link
                  v-if="$store.state.auth.availablePermissions['library']"
                  class="item"
                  :to="{name: 'manage.library.edits', query: {q: 'is_approved:null'}}"
                >
                  <div
                    v-if="$store.state.ui.notifications.pendingReviewEdits > 0"
                    :title="labels.pendingReviewEdits"
                    :class="['ui', 'circular', 'mini', 'right floated', 'accent', 'label']"
                  >
                    {{ $store.state.ui.notifications.pendingReviewEdits }}
                  </div>
                  {{ $t('components.Sidebar.link.library') }}
                </router-link>
                <router-link
                  v-if="$store.state.auth.availablePermissions['moderation']"
                  class="item"
                  :to="{name: 'manage.moderation.reports.list', query: {q: 'resolved:no'}}"
                >
                  <div
                    v-if="$store.state.ui.notifications.pendingReviewReports + $store.state.ui.notifications.pendingReviewRequests > 0"
                    :title="labels.pendingReviewReports"
                    :class="['ui', 'circular', 'mini', 'right floated', 'accent', 'label']"
                  >
                    {{ $store.state.ui.notifications.pendingReviewReports + $store.state.ui.notifications.pendingReviewRequests }}
                  </div>
                  {{ $t('components.Sidebar.link.moderation') }}
                </router-link>
                <router-link
                  v-if="$store.state.auth.availablePermissions['settings']"
                  class="item"
                  :to="{name: 'manage.users.users.list'}"
                >
                  {{ $t('components.Sidebar.link.users') }}
                </router-link>
                <router-link
                  v-if="$store.state.auth.availablePermissions['settings']"
                  class="item"
                  :to="{path: '/manage/settings'}"
                >
                  {{ $t('components.Sidebar.link.settings') }}
                </router-link>
              </div>
            </div>
          </div>
        </div>
        <template v-if="width > 768">
          <div class="item">
            <div class="ui dropdown user-dropdown">
              <div class="trigger">
                <img
                  v-if="$store.state.auth.authenticated && $store.state.auth.profile?.avatar && $store.state.auth.profile?.avatar.urls.medium_square_crop"
                  class="ui avatar image"
                  alt=""
                  :src="$store.getters['instance/absoluteUrl']($store.state.auth.profile?.avatar.urls.medium_square_crop)"
                >
                <actor-avatar
                  v-else-if="$store.state.auth.authenticated"
                  :actor="{preferred_username: $store.state.auth.username, full_username: $store.state.auth.username,}"
                />
                <i v-else class="cog icon" />
              </div>
              <div class="menu dropdown-menu">
                <user-menu v-bind="$attrs" :width="width" />
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <a
            href=""
            class="item"
            @click.prevent.exact="showUserModal = !showUserModal"
          >
            <img
              v-if="$store.state.auth.authenticated && $store.state.auth.profile?.avatar?.urls.medium_square_crop"
              class="ui avatar image"
              alt=""
              :src="$store.getters['instance/absoluteUrl']($store.state.auth.profile?.avatar.urls.medium_square_crop)"
            >
            <actor-avatar
              v-else-if="$store.state.auth.authenticated"
              :actor="{preferred_username: $store.state.auth.username, full_username: $store.state.auth.username,}"
            />
            <i
              v-else
              class="cog icon"
            />
            <div
              v-if="$store.state.ui.notifications.inbox + additionalNotifications > 0"
              :class="['ui', 'accent', 'mini', 'bottom floating', 'circular', 'label']"
            >
              {{ $store.state.ui.notifications.inbox + additionalNotifications }}
            </div>
          </a>
        </template>
        <user-modal
          v-model:show="showUserModal"
          @show-theme-modal-event="showThemeModal=true"
          @show-language-modal-event="showLanguageModal=true"
        />
        <semantic-modal
          ref="languageModal"
          v-model:show="showLanguageModal"
          :fullscreen="false"
        >
          <i
            role="button"
            class="left chevron back inside icon"
            @click.prevent.exact="showUserModal = !showUserModal"
          />
          <div class="header">
            <h3 class="title">
              {{ labels.language }}
            </h3>
          </div>
          <div class="content">
            <fieldset
              v-for="(language, key) in SUPPORTED_LOCALES"
              :key="key"
            >
              <input
                :id="`${key}`"
                v-model="locale"
                type="radio"
                name="language"
                :value="key"
              >
              <label :for="`${key}`">{{ language }}</label>
            </fieldset>
          </div>
        </semantic-modal>
        <semantic-modal
          ref="themeModal"
          v-model:show="showThemeModal"
          :fullscreen="false"
        >
          <i
            role="button"
            class="left chevron back inside icon"
            @click.prevent.exact="showUserModal = !showUserModal"
          />
          <div class="header">
            <h3 class="title">
              {{ labels.theme }}
            </h3>
          </div>
          <div class="content">
            <fieldset
              v-for="th in themes"
              :key="th.key"
            >
              <input
                :id="th.key"
                v-model="theme"
                type="radio"
                name="theme"
                :value="th.key"
              >
              <label :for="th.key">{{ th.name }}</label>
            </fieldset>
          </div>
        </semantic-modal>
        <div class="item collapse-button-wrapper">
          <button
            :class="['ui', 'basic', 'big', 'inverted icon', 'collapse', 'button']"
          >
            <i class="sidebar icon" />
          </button>
        </div>
      </nav>
    </header>
    <div
      v-if="!$store.state.auth.authenticated"
      class="ui basic signup segment"
    >
      <router-link
        class="ui fluid tiny primary button"
        :to="{name: 'login'}"
      >
        {{ $t('components.Sidebar.link.login') }}
      </router-link>
      <div class="ui small hidden divider" />
      <router-link
        class="ui fluid tiny button"
        :to="{path: '/signup'}"
      >
        {{ $t('components.Sidebar.link.createAccount') }}
      </router-link>
    </div>
    <nav
      class="secondary"
      role="navigation"
      aria-labelledby="navigation-label"
    >
      <h1
        id="navigation-label"
        class="visually-hidden"
      >
        {{ $t('components.Sidebar.header.main') }}
      </h1>
      <div class="ui small hidden divider" />
      <section
        :aria-label="labels.mainMenu"
        class="ui bottom attached active tab"
      >
        <nav
          class="ui vertical large fluid inverted menu"
          role="navigation"
          :aria-label="labels.mainMenu"
        >
          <!-- <router-link
            class="item"
            :to="{name: 'index'}"
          >
            {{ $t('components.Sidebar.link.library') }}
          </router-link> -->

          <router-link
            v-if="$store.state.auth.authenticated"
            class="item"
            :to="{ path: '/explore' }"
            @click.prevent="toggleSidebar"
          >
            {{ $t('components.Sidebar.header.explore') }}
          </router-link>

          <router-link
            v-if="$store.state.auth.authenticated && $store.state.auth.profile.is_artist"
            class="item"
            :to="{ path: '/mycontent' }"
          >
            {{ $t('components.Sidebar.link.myContent') }}
          </router-link>

          <router-link
            v-if="$store.state.auth.authenticated && $store.state.auth.profile.is_artist"
            class="item"
            :to="{name: 'channels.detail', params: {id: $store.state.auth.fullUsername}}"
          >
            {{ $t('components.Sidebar.link.myChannel') }}
          </router-link>

          <!--
          <router-link
            v-if="$store.state.auth.availablePermissions['settings']"
            class="item"
            :to="{ path: '/adminland' }"
          >
            {{ $t('components.Sidebar.link.adminland') }}
          </router-link> -->

          <router-link
            v-if="$store.state.auth.authenticated && $store.state.auth.profile.is_artist"
            class="ui primary button"
            :to="{ path: '/upload' }"
          >
            {{ $t('components.Sidebar.link.upload') }}
          </router-link> 
        </nav>
      </section>
    </nav>
  </aside>
</template>

<style>
/* Menu icon color */
.menu-icon {
  color: #1c8085 !important;
  position: absolute !important;
  top: 1rem !important;
  left: 1rem !important;
  cursor: pointer !important;
}

.sidebar {
  padding-bottom: 1rem;
}

/* Wrench icon color with more specific selector */
.ui.menu .item .wrench.icon,
.ui.admin-dropdown .wrench.icon,
.component-sidebar .wrench.icon {
  color: #373571 !important;
}

.ui.vertical.left.visible.wide.sidebar.component-sidebar,
.ui.vertical.left.visible.wide.sidebar.component-sidebar .header-wrapper {
  transition: all 0.3s ease !important;
}

/* Add collapsed state styles with transition */
.ui.vertical.left.visible.wide.sidebar.component-sidebar.collapsed {
  width: 60px !important;
  min-width: 60px !important;
  max-width: 60px !important;
  background-color: #e5f1f2 !important;
  box-shadow: none !important;
}

/* Adjust header when collapsed */
.ui.vertical.left.visible.wide.sidebar.component-sidebar.collapsed .header-wrapper {
  width: 60px !important;
  min-width: 60px !important;
  max-width: 60px !important;
  padding: 1rem 0 !important;
  display: flex !important;
  justify-content: center !important;
  background-color: #e5f1f2 !important;
}

/* Hide elements when collapsed */
.ui.vertical.left.visible.wide.sidebar.component-sidebar.collapsed .secondary,
.ui.vertical.left.visible.wide.sidebar.component-sidebar.collapsed .search-wrapper,
.ui.vertical.left.visible.wide.sidebar.component-sidebar.collapsed .signup,
.ui.vertical.left.visible.wide.sidebar.component-sidebar.collapsed .right.menu,
.ui.vertical.left.visible.wide.sidebar.component-sidebar.collapsed .spacer {
  display: none !important;
}

/* Keep menu icon visible when collapsed */
.ui.vertical.left.visible.wide.sidebar.component-sidebar.collapsed .menu-icon {
  display: block !important;
  position: relative !important;
  top: 0 !important;
  left: 0 !important;
}

/* Adjust main content margin */
#app > div > .main.pusher {
  transition: margin-left 0.3s ease !important;
}

#app > div > .main.pusher.no-sidebar {
  margin-left: 0px !important;
}

#app > div > .main.pusher.sidebar-collapsed:not(.small) {
  margin-left: 60px !important;
}

/* Apply color to navigation items only, excluding top icons */
.ui.vertical.menu .item,
.ui.vertical.menu .item:hover,
.secondary .component-sidebar .item,
.secondary .component-sidebar a {
  color: #1c8085 !important;
}

/* Keep top menu icons with their original color */
.top.menu .icon,
.top.menu .item {
  color: inherit !important;
}

.ui.vertical.menu {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  text-align: center !important;
}

.ui.vertical.menu .item {
  width: 144px !important;
  border-radius: 4px !important;
  justify-content: center !important;
  text-align: center !important;
}

.ui.vertical.menu .item.active,
.ui.menu .item.active {
  background: transparent !important;
  border-right: none !important;
}

.ui.vertical.inverted.menu .router-link-exact-active.active {
  color: #e7922f !important;
}

.ui.dropdown.user-dropdown {
  position: relative !important;
  
  .trigger {
    cursor: pointer;
    display: flex;
    align-items: center;
  }

  .dropdown-menu {
    position: absolute !important;
    top: 100% !important;
    right: 0 !important;
    left: auto !important;
    min-width: 200px !important;
    background: var(--sidebar-background) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 4px !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
    margin-top: 0.5rem !important;
    z-index: 1000 !important;
    
    .menu {
      position: static !important;
      border: none !important;
      box-shadow: none !important;
      background: transparent !important;
    }
    
    .item {
      color: var(--primary-color) !important;
      padding: 0.8rem 1rem !important;
      
      &:hover {
        background-color: rgba(0,0,0,0.05) !important;
      }
    }
  }
}
</style>
