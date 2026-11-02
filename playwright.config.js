const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './generated/tests',
  testMatch: '**/*.spec.js',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: [['list'], ['html', {
    outputFolder: 'generated/reports/playwright-report',
    open: 'never'
  }]],
  outputDir: 'generated/test-results',
  use: {
    baseURL: process.env.BASE_URL || undefined,
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
    actionTimeout: 15000,
    navigationTimeout: 30000
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }]
});
