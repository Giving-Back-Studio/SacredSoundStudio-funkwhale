import type { RouteRecordRaw } from 'vue-router'

import settings from './settings'
import library from './library'
import content from './content'
import manage from './manage'
import store from '~/store'
import auth from './auth'
import user from './user'
import { requireLoggedIn } from '~/router/guards'

const routeToIndex = (to: any, from: any, next: any) => {
  if (store.state.auth.authenticated) {
    if (store.state.auth.profile?.is_artist) return next('/mycontent')
    return next('/explore')
  }
  return next()
}

export default [
  {
    path: '/',
    name: 'index',
    component: () => import('~/components/Home.vue'),
    beforeEnter: routeToIndex
  },
  {
    path: '/create',
    name: 'artistLandingPage',
    component: () => import('~/components/ArtistLandingPage.vue'),
    beforeEnter: routeToIndex
  },
  {
    path: '/auth',
    name: 'auth',
    component: () => import('~/components/auth/AuthForm.vue')
  },
  {
    path: '/explore',
    name: 'explore',
    component: () => import('~/views/content/AllContent.vue')
  },
  {
    path: '/index.html',
    redirect: to => {
      const { hash, query } = to
      return { name: 'index', hash, query }
    }
  },
  {
    path: '/front',
    name: 'front',
    redirect: to => {
      const { hash, query } = to
      return { name: 'index', hash, query }
    }
  },

  {
    path: '/about',
    name: 'about',
    component: () => import('~/components/About.vue')
  },
  {
    // TODO (wvffle): Make it a child of /about to have the active style on the sidebar link
    path: '/about/pod',
    name: 'about-pod',
    component: () => import('~/components/AboutPod.vue')
  },
  {
    path: '/notifications',
    name: 'notifications',
    component: () => import('~/views/Notifications.vue')
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('~/views/Search.vue')
  },
  ...auth,
  ...settings,
  ...user,
  {
    path: '/favorites',
    name: 'favorites',
    component: () => import('~/components/favorites/List.vue'),
    props: route => ({
      defaultOrdering: route.query.ordering,
      defaultPage: route.query.page ? +route.query.page : undefined
    }),
    beforeEnter: requireLoggedIn()
  },
  ...content,
  {
    path: '/mycontent',
    name: 'content.me',
    component: () => import('~/views/content/MyContent.vue'),
    beforeEnter: requireLoggedIn(),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/mychannel',
    name: 'channels.me',
    component: () => import('~/views/channels/MyChannel.vue'),
    beforeEnter: requireLoggedIn(),
    meta: {
      requiresAuth: true
    }
  },
  ...manage,
  ...library,
  {
    path: '/channels/:id',
    props: true,
    component: () => import('~/views/channels/DetailBase.vue'),
    children: [
      {
        path: '',
        name: 'channels.detail',
        component: () => import('~/views/channels/DetailOverview.vue')
      },
      {
        path: 'episodes',
        name: 'channels.detail.episodes',
        component: () => import('~/views/channels/DetailEpisodes.vue')
      }
    ]
  },
  {
    path: '/subscriptions',
    name: 'subscriptions',
    component: () => import('~/views/channels/SubscriptionsList.vue'),
    props: route => ({ defaultQuery: route.query.q })
  },
  {
    path: '/:pathMatch(.*)*',
    name: '404',
    component: () => import('~/components/PageNotFound.vue')
  }
] as RouteRecordRaw[]
