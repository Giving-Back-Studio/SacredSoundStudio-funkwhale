import type { RouteRecordRaw } from 'vue-router'
import artistRoutes from './artists'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('~/views/Home.vue'),
    meta: {
      requiresAuth: false,
      title: 'Home'
    }
  },
  ...artistRoutes
]

export default routes
