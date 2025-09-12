/**
 * Firebase クライアント設定ファイル
 * 
 * 主な仕様:
 * - セキュアな環境変数ベースの設定
 * - SSR対応のクライアントサイドのみ初期化
 * - 開発環境でのエミュレータ接続
 * - 同期的な初期化でエラーハンドリング改善
 * 
 * 制限事項:
 * - 環境変数が不完全な場合は初期化をスキップ
 * - サーバーサイドでの Firebase 初期化は行わない
 */

import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';

// Firebase設定
const getFirebaseConfig = () => ({
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID
});

// Firebase初期化
let app: any = null;
let auth: any = null;

// クライアントサイドでのみ初期化
if (typeof window !== 'undefined') {
  try {
    const config = getFirebaseConfig();
    
    // 必須の設定項目をチェック
    if (config.apiKey && config.authDomain && config.projectId) {
      // Firebase初期化
      app = initializeApp(config);
      auth = getAuth(app);
      
      // 開発環境でのみエミュレーター接続
      // 本番環境では絶対にエミュレーターに接続しない
      if (process.env.NODE_ENV === 'development' && process.env.NEXT_PUBLIC_USE_EMULATOR === 'true') {
        try {
          connectAuthEmulator(auth, 'http://localhost:9099');
          console.log('🔧 Firebase Auth Emulator connected');
        } catch (error) {
          console.log('Auth emulator already connected or not available');
        }
      }
      
      console.log('✅ Firebase 初期化完了');
    } else {
      console.warn('⚠️ Firebase 設定が不完全です:', {
        hasApiKey: !!config.apiKey,
        hasAuthDomain: !!config.authDomain,
        hasProjectId: !!config.projectId
      });
    }
  } catch (error) {
    console.error('❌ Firebase initialization error:', error);
  }
}

// エクスポート
export { auth };
export default app;