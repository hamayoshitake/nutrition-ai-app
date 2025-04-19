import { test, expect } from '@playwright/test';

// Next.js devサーバーが http://localhost:3000 で起動している前提

test.describe('チャット入力UI', () => {
  test('入力欄と送信ボタンが表示されている', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await expect(page.getByTestId('chat-input')).toBeVisible();
    await expect(page.getByTestId('send-button')).toBeVisible();
  });

  test('入力→送信でチャットバブルに反映される', async ({ page }) => {
    await page.goto('http://localhost:3000');
    const input = page.getByTestId('chat-input');
    const send = page.getByTestId('send-button');
    await input.fill('りんご 100g');
    await send.click();
    await expect(page.getByTestId('chat-bubble').filter({ hasText: 'りんご 100g' })).toBeVisible();
  });
}); 