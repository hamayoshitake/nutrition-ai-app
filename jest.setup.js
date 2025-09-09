import '@testing-library/jest-dom'

// Firebase モックの設定
const mockAuth = {
  currentUser: null,
}

const mockSignInWithEmailAndPassword = jest.fn()
const mockCreateUserWithEmailAndPassword = jest.fn()
const mockSignOut = jest.fn()
const mockOnAuthStateChanged = jest.fn()

jest.mock('firebase/auth', () => ({
  getAuth: jest.fn(() => mockAuth),
  signInWithEmailAndPassword: mockSignInWithEmailAndPassword,
  createUserWithEmailAndPassword: mockCreateUserWithEmailAndPassword,
  signOut: mockSignOut,
  onAuthStateChanged: mockOnAuthStateChanged,
  connectAuthEmulator: jest.fn(),
}))

jest.mock('firebase/app', () => ({
  initializeApp: jest.fn(),
}))

// Next.js router モック
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
  }),
  usePathname: () => '/',
}))

// グローバルにモック関数を公開
global.mockSignInWithEmailAndPassword = mockSignInWithEmailAndPassword
global.mockCreateUserWithEmailAndPassword = mockCreateUserWithEmailAndPassword
global.mockSignOut = mockSignOut
global.mockOnAuthStateChanged = mockOnAuthStateChanged

// 環境変数のモック
process.env.NEXT_PUBLIC_FIREBASE_API_KEY = 'test-api-key'
process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN = 'test-domain.firebaseapp.com'
process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID = 'test-project'
process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET = 'test-bucket'
process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID = '123456789'
process.env.NEXT_PUBLIC_FIREBASE_APP_ID = 'test-app-id'
process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID = 'test-measurement-id' 