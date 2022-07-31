import type { InitModule } from '~/types'
import type { Router } from 'vue-router'
import type { App } from 'vue'

const COOKIE = 'allow-tracing'

const initSentry = async (app: App, router: Router) => {
  const [{ BrowserTracing }, Sentry] = await Promise.all([
    import('@sentry/tracing'),
    import('@sentry/vue')
  ])

  Sentry.init({
    app,
    dsn: import.meta.env.VUE_SENTRY_DSN,
    logErrors: true,
    trackComponents: true,
    integrations: [
      new BrowserTracing({
        routingInstrumentation: Sentry.vueRouterInstrumentation(router)
      })
    ],
    // Set tracesSampleRate to 1.0 to capture 100%
    // of transactions for performance monitoring.
    // We recommend adjusting this value in production
    tracesSampleRate: 1.0
  })
}

export const install: InitModule = async ({ app, router, store }) => {
  if (import.meta.env.VUE_SENTRY_DSN) {
    const [{ useCookies }, { gettext: { $pgettext } }] = await Promise.all([
      import('@vueuse/integrations/useCookies'),
      import('~/init/locale')
    ])

    const { get, set } = useCookies()

    const allowed = get(COOKIE)

    if (allowed === 'yes') {
      return initSentry(app, router)
    }

    if (allowed === undefined) {
      const { hostname, origin } = new URL(import.meta.env.VUE_SENTRY_DSN)
      return store.commit('ui/addMessage', {
        content: hostname === 'am.funkwhale.audio'
          ? $pgettext(
            'App/Message/Paragraph',
            'To enhance the quality of our services, we would like to collect information about crashes during your session.<br><sub>The stack traces will be shared to <a href="%{origin}">Funkwhale\'s official Glitchtip instance</a> in order to help us understand how and when the errors occur.</sub>',
            { hostname, origin }
          )
          : $pgettext(
            'App/Message/Paragraph',
            'To enhance the quality of our services, we would like to collect information about crashes during your session.<br><sub>The stack traces will be shared to <a href="%{origin}">%{hostname}</a> in order to help us understand how and when the errors occur.</sub>',
            { hostname, origin }
          ),
        date: new Date(),
        key: 'allowSentryTracing',
        displayTime: 0,
        classActions: 'bottom attached opaque',
        actions: [
          {
            text: $pgettext('App/Message/Paragraph', 'Allow'),
            class: 'primary',
            click: () => {
              set(COOKIE, 'yes')
              return initSentry(app, router)
            }
          },
          {
            text: $pgettext('App/Message/Paragraph', 'Deny'),
            class: 'basic',
            click: () => set(COOKIE, 'no')
          }
        ]
      })
    }
  }
}
