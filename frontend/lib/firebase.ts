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
  // Vercel環境変数の詳細確認ログ
  console.log('🔍 === Vercel環境変数確認 ===');
  console.log('📍 NODE_ENV:', process.env.NODE_ENV);
  console.log('📍 VERCEL:', process.env.VERCEL);
  console.log('📍 VERCEL_ENV:', process.env.VERCEL_ENV);
  console.log('📍 Firebase環境変数:');
  console.log('  - API_KEY:', process.env.NEXT_PUBLIC_FIREBASE_API_KEY ? '✅ 設定済み' : '❌ 未設定');
  console.log('  - AUTH_DOMAIN:', process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN ? '✅ 設定済み' : '❌ 未設定');
  console.log('  - PROJECT_ID:', process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID ? '✅ 設定済み' : '❌ 未設定');
  console.log('  - STORAGE_BUCKET:', process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET ? '✅ 設定済み' : '❌ 未設定');
  console.log('  - MESSAGING_SENDER_ID:', process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID ? '✅ 設定済み' : '❌ 未設定');
  console.log('  - APP_ID:', process.env.NEXT_PUBLIC_FIREBASE_APP_ID ? '✅ 設定済み' : '❌ 未設定');
  console.log('📍 実際の値（最初の10文字のみ表示）:');
  console.log('  - API_KEY:', process.env.NEXT_PUBLIC_FIREBASE_API_KEY?.substring(0, 10) + '...');
  console.log('  - AUTH_DOMAIN:', process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN);
  console.log('  - PROJECT_ID:', process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID);
  console.log('================================');

  // 本番環境の場合のデフォルト設定
  const defaultConfig = {
    apiKey: "AIzaSyDYOlD2g8X8eFWZhbp3tG3kXX8lJE-1234", // ダミー値、実際の値はVercelで設定
    authDomain: "nutrition-ai-app-bdee9.firebaseapp.com",
    projectId: "nutrition-ai-app-bdee9",
    storageBucket: "nutrition-ai-app-bdee9.firebasestorage.app",
    messagingSenderId: "123456789012",
    appId: "1:123456789012:web:abcdef1234567890abcdef"
  };

  const config = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || defaultConfig.apiKey,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || defaultConfig.authDomain,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || defaultConfig.projectId,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || defaultConfig.storageBucket,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || defaultConfig.messagingSenderId,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || defaultConfig.appId
  };

  console.log('🔧 最終的なFirebase設定:', {
    apiKey: config.apiKey?.substring(0, 10) + '...',
    authDomain: config.authDomain,
    projectId: config.projectId,
    storageBucket: config.storageBucket,
    messagingSenderId: config.messagingSenderId,
    appId: config.appId?.substring(0, 20) + '...'
  });

  return config;
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
    } else {
    
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
    }
  } catch (error) {
    console.error('❌ Firebase initialization error:', error);
    // エラーが発生してもauth は null のままにしておく
    auth = null;
  }
}

// エクスポート
export { auth };
export default app;