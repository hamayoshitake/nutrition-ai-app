/**
 * Firebase クライアント設定ファイル
 * 
 * 主な仕様:
 * - 本番環境でのフォールバック設定
 * - 開発環境でのエミュレータ接続
 * - エラーハンドリングの改善
 * 
 * 制限事項:
 * - 開発環境のみエミュレータ接続
 */

import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';

// Firebase設定（本番環境用のフォールバック付き）
const getFirebaseConfig = () => {
  // 本番環境の場合のデフォルト設定
  const defaultConfig = {
    apiKey: "AIzaSyDYOlD2g8X8eFWZhbp3tG3kXX8lJE-1234", // ダミー値、実際の値はVercelで設定
    authDomain: "nutrition-ai-app-bdee9.firebaseapp.com",
    projectId: "nutrition-ai-app-bdee9",
    storageBucket: "nutrition-ai-app-bdee9.firebasestorage.app",
    messagingSenderId: "123456789012",
    appId: "1:123456789012:web:abcdef1234567890abcdef"
  };

  return {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || defaultConfig.apiKey,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || defaultConfig.authDomain,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || defaultConfig.projectId,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || defaultConfig.storageBucket,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || defaultConfig.messagingSenderId,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || defaultConfig.appId
  };
};

// Firebase初期化
let app: any = null;
let auth: any = null;

// クライアントサイドでのみ初期化
if (typeof window !== 'undefined') {
  try {
    const config = getFirebaseConfig();
    
    console.log('🔧 Firebase 初期化開始');
    console.log('📍 環境:', process.env.NODE_ENV);
    
    app = initializeApp(config);
    auth = getAuth(app);
    
    // 開発環境のみエミュレーター接続
    if (process.env.NODE_ENV === 'development' && process.env.NEXT_PUBLIC_USE_EMULATOR === 'true') {
      try {
        connectAuthEmulator(auth, 'http://localhost:9099');
        console.log('✅ Auth エミュレータに接続しました');
      } catch (error) {
        console.log('⚠️ Auth emulator already connected:', error);
      }
    }
    
    console.log('✅ Firebase 初期化完了');
  } catch (error) {
    console.error('❌ Firebase initialization error:', error);
    // エラーが発生してもauth は null のままにしておく
  }
}

// エクスポート
export { auth };
export default app;