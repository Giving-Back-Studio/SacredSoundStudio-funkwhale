import { defineConfig } from 'cypress'

export default defineConfig({
  chromeWebSecurity: false,
  e2e: {
    baseUrl: 'https://demo.funkwhale.audio'
  }
})
