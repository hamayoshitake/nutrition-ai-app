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

// Firebase設定（開発環境対応）
const getFirebaseConfig = () => {
  // 環境変数から設定を取得
  const config = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID
  };

  // 本番環境でのフォールバック設定
  if (process.env.NODE_ENV === 'production') {
    return {
      apiKey: config.apiKey || "production-api-key-required",
      authDomain: config.authDomain || "nutrition-ai-app-bdee9.firebaseapp.com",
      projectId: config.projectId || "nutrition-ai-app-bdee9",
      storageBucket: config.storageBucket || "nutrition-ai-app-bdee9.firebasestorage.app",
      messagingSenderId: config.messagingSenderId || "123456789012",
      appId: config.appId || "1:123456789012:web:abcdef1234567890abcdef"
    };
  }

  // 開発環境では環境変数が設定されていない場合はnullを返す
  return config.apiKey ? config : null;
};

// Firebase初期化
let app: any = null;
let auth: any = null;

// クライアントサイドでのみ初期化
if (typeof window !== 'undefined') {
  try {
    const config = getFirebaseConfig();
    
    // 設定が無効な場合は初期化をスキップ
    if (!config || !config.apiKey) {
      console.log('⚠️ Firebase 設定が不完全です。認証機能は無効になります。');
      console.log('📋 環境変数の設定が必要: NEXT_PUBLIC_FIREBASE_API_KEY など');
      console.log('🔍 現在の設定状況:', {
        hasConfig: !!config,
        apiKey: config?.apiKey ? '設定済み' : '未設定',
        authDomain: config?.authDomain || '未設定',
        projectId: config?.projectId || '未設定',
        nodeEnv: process.env.NODE_ENV
      });
      // auth は null のままにしておく
      return;
    }
    
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
    auth = null;
  }
}

// エクスポート
export { auth };
export default app;