const { defineConfig } = require('@playwright/test')

module.exports = defineConfig({
  testDir: './tests',
  timeout: 90000,
  retries: 0,
  reporter: 'list',
  use: {
    headless: true,
    viewport: { width: 1280, height: 900 },
    ignoreHTTPSErrors: true,
  },
})
