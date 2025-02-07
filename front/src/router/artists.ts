import type { RouteRecordRaw } from 'vue-router'
import ArtistProfile from '~/views/artists/ArtistProfile.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/artists/:id',
    name: 'artists.profile',
    component: ArtistProfile,
    props: true,
    meta: {
      requiresAuth: false,
      title: (route: any) => `Artist - ${route.params.id}`
    }
  }
]

export default routes
