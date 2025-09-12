import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';

// Firebase設定（本番用のデフォルト値を含む）
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyDummy-Key-For-Build-Process",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "nutrition-ai-app-bdee9.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "nutrition-ai-app-bdee9",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "nutrition-ai-app-bdee9.firebasestorage.app",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "123456789",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:123456789:web:dummy",
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID || "G-DUMMY"
};

// サーバーサイドでの初期化チェック
let app;
let auth;

try {
  // Firebase初期化
  app = initializeApp(firebaseConfig);
  
  // Authentication初期化（クライアントサイドのみ）
  if (typeof window !== 'undefined') {
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
  }
} catch (error) {
  console.warn('Firebase initialization error:', error);
  // ビルド時エラーを防ぐ
}

// エクスポート（安全な方法）
export { auth };
export default app; 