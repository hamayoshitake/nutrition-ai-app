/**
 * ログイン機能のE2Eテスト
 * 
 * 主な仕様:
 * - ログインページの表示確認
 * - フォーム入力とエラーハンドリング
 * - 認証フローのテスト
 * 
 * 制限事項:
 * - エミュレータ環境でのテスト
 * - テストユーザーでの実行
 */

import { test, expect } from '@playwright/test';

test.describe('ログイン機能', () => {
  test.beforeEach(async ({ page }) => {
    // ローカル開発サーバーにアクセス
    await page.goto('http://localhost:3000/login');
  });

  test('ログインページが正しく表示される', async ({ page }) => {
    // ページタイトルの確認
    await expect(page).toHaveTitle(/MY BODY COACH/);
    
    // ログインフォームの要素が存在することを確認
    await expect(page.locator('text=Welcome Back')).toBeVisible();
    await expect(page.locator('text=Log in to your account')).toBeVisible();
    
    // フォーム要素の確認
    await expect(page.locator('label:has-text("Email")')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('label:has-text("Password")')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button:has-text("ログイン")')).toBeVisible();
  });

  test('空の値でログインを試行するとエラーが表示される', async ({ page }) => {
    // ログインボタンをクリック
    await page.locator('button:has-text("ログイン")').click();
    
    // バリデーションエラーメッセージの確認
    await expect(page.locator('text=メールアドレスを入力してください')).toBeVisible();
    await expect(page.locator('text=パスワードを入力してください')).toBeVisible();
  });

  test('無効なメールアドレスでログインを試行するとエラーが表示される', async ({ page }) => {
    // 無効なメールアドレスを入力
    await page.locator('input[type="email"]').fill('invalid-email');
    await page.locator('input[type="password"]').fill('password');
    
    // ログインボタンをクリック
    await page.locator('button:has-text("ログイン")').click();
    
    // 一般的なエラーメッセージの確認
    await expect(page.locator('text=ログインに失敗しました。メールアドレスとパスワードを確認してください。')).toBeVisible();
  });

  test('存在しないユーザーでログインを試行するとエラーが表示される', async ({ page }) => {
    // 存在しないユーザー情報を入力
    await page.locator('input[type="email"]').fill('nonexistent@example.com');
    await page.locator('input[type="password"]').fill('wrongpassword');
    
    // ログインボタンをクリック
    await page.locator('button:has-text("ログイン")').click();
    
    // 一般的なエラーメッセージの確認
    await expect(page.locator('text=ログインに失敗しました。メールアドレスとパスワードを確認してください。')).toBeVisible();
  });

  test('有効なユーザーでログインが成功する', async ({ page }) => {
    // テストユーザーでログイン
    await page.locator('input[type="email"]').fill('test-1@gmail.com');
    await page.locator('input[type="password"]').fill('pass2025');
    
    // ログインボタンをクリック
    await page.locator('button:has-text("ログイン")').click();
    
    // ログイン成功後のリダイレクト確認
    await expect(page).toHaveURL('http://localhost:3000/');
    
    // チャット画面の要素確認
    await expect(page.locator('text=MY BODY COACH')).toBeVisible();
    await expect(page.locator('button:has-text("ログアウト")')).toBeVisible();
  });

  test('登録ページへのリンクが機能する', async ({ page }) => {
    // 登録ページへのリンクをクリック（実際のテキストに合わせて修正）
    await page.locator('a:has-text("Sign up")').click();
    
    // 登録ページに遷移することを確認
    await expect(page).toHaveURL('http://localhost:3000/register');
  });
});
