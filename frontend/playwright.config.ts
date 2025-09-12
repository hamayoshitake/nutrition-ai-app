/**
 * Playwright 設定ファイル
 * 
 * 主な仕様:
 * - ローカル開発環境でのE2Eテスト実行
 * - ヘッドレスモードでの実行
 * - レポート生成とスクリーンショット保存
 * 
 * 制限事項:
 * - Chromeブラウザのみでテスト実行
 * - ローカルサーバー起動が前提
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});