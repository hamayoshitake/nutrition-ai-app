import { render, screen, waitFor, act } from '@testing-library/react'
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged 
} from 'firebase/auth'
import { AuthProvider, useAuth } from '../contexts/AuthContext'

// Firebase Auth のモック
jest.mock('firebase/auth')
const mockSignInWithEmailAndPassword = signInWithEmailAndPassword as jest.MockedFunction<typeof signInWithEmailAndPassword>
const mockCreateUserWithEmailAndPassword = createUserWithEmailAndPassword as jest.MockedFunction<typeof createUserWithEmailAndPassword>
const mockSignOut = signOut as jest.MockedFunction<typeof signOut>
const mockOnAuthStateChanged = onAuthStateChanged as jest.MockedFunction<typeof onAuthStateChanged>

// fetch のモック
global.fetch = jest.fn()

// テスト用コンポーネント
const TestComponent = () => {
  const { user, loading, signIn, signUp, logout, getValidToken } = useAuth()
  
  return (
    <div>
      <div data-testid="loading">{loading ? 'loading' : 'not-loading'}</div>
      <div data-testid="user">{user ? user.email : 'no-user'}</div>
      <button onClick={() => signIn('test@example.com', 'password123')}>
        Sign In
      </button>
      <button onClick={() => signUp('test@example.com', 'password123')}>
        Sign Up
      </button>
      <button onClick={logout}>Logout</button>
      <button onClick={async () => {
        const token = await getValidToken()
        console.log('Token:', token)
      }}>
        Get Token
      </button>
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // fetch のデフォルトモック
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ success: true }),
    })
  })

  test('初期状態ではローディング中でユーザーはnull', () => {
    // onAuthStateChanged のモック（初期状態）
    mockOnAuthStateChanged.mockImplementation((auth, callback) => {
      // 初期状態では何もしない
      return jest.fn() // unsubscribe function
    })

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    expect(screen.getByTestId('loading')).toHaveTextContent('loading')
    expect(screen.getByTestId('user')).toHaveTextContent('no-user')
  })

  test('ユーザーがログインしている場合、ユーザー情報が表示される', async () => {
    const mockUser = {
      uid: 'test-uid',
      email: 'test@example.com',
      getIdToken: jest.fn().mockResolvedValue('mock-token'),
    }

    // onAuthStateChanged のモック（ログイン済み）
    mockOnAuthStateChanged.mockImplementation((auth, callback) => {
      // すぐにコールバックを呼び出す
      setTimeout(() => callback(mockUser as any), 0)
      return jest.fn() // unsubscribe function
    })

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('not-loading')
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com')
    })
  })

  test('signIn が正常に動作する', async () => {
    const mockUser = {
      uid: 'test-uid',
      email: 'test@example.com',
    }

    mockSignInWithEmailAndPassword.mockResolvedValue({
      user: mockUser,
    } as any)

    mockOnAuthStateChanged.mockImplementation((auth, callback) => {
      return jest.fn()
    })

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    const signInButton = screen.getByText('Sign In')
    
    await act(async () => {
      signInButton.click()
    })

    expect(mockSignInWithEmailAndPassword).toHaveBeenCalledWith(
      expect.anything(),
      'test@example.com',
      'password123'
    )
  })

  test('signUp が正常に動作し、バックエンドAPIが呼ばれる', async () => {
    const mockUser = {
      uid: 'test-uid',
      email: 'test@example.com',
      displayName: null,
      getIdToken: jest.fn().mockResolvedValue('mock-token'),
    }

    mockCreateUserWithEmailAndPassword.mockResolvedValue({
      user: mockUser,
    } as any)

    mockOnAuthStateChanged.mockImplementation((auth, callback) => {
      return jest.fn()
    })

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    const signUpButton = screen.getByText('Sign Up')
    
    await act(async () => {
      signUpButton.click()
    })

    expect(mockCreateUserWithEmailAndPassword).toHaveBeenCalledWith(
      expect.anything(),
      'test@example.com',
      'password123'
    )

    // バックエンドAPIが呼ばれることを確認
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:5001/nutrition-ai-app-bdee9/us-central1/createUserProfile',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-token',
          },
          body: JSON.stringify({
            email: 'test@example.com',
            name: null,
          }),
        })
      )
    })
  })

  test('logout が正常に動作する', async () => {
    mockSignOut.mockResolvedValue()

    mockOnAuthStateChanged.mockImplementation((auth, callback) => {
      return jest.fn()
    })

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    const logoutButton = screen.getByText('Logout')
    
    await act(async () => {
      logoutButton.click()
    })

    expect(mockSignOut).toHaveBeenCalled()
  })

  test('getValidToken がトークンを返す', async () => {
    const mockUser = {
      uid: 'test-uid',
      email: 'test@example.com',
      getIdToken: jest.fn().mockResolvedValue('valid-token'),
    }

    mockOnAuthStateChanged.mockImplementation((auth, callback) => {
      setTimeout(() => callback(mockUser as any), 0)
      return jest.fn()
    })

    const consoleSpy = jest.spyOn(console, 'log').mockImplementation()

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com')
    })

    const getTokenButton = screen.getByText('Get Token')
    
    await act(async () => {
      getTokenButton.click()
    })

    await waitFor(() => {
      expect(mockUser.getIdToken).toHaveBeenCalledWith(true)
    })

    consoleSpy.mockRestore()
  })

  test('ユーザーがいない場合、getValidToken は null を返す', async () => {
    mockOnAuthStateChanged.mockImplementation((auth, callback) => {
      setTimeout(() => callback(null), 0)
      return jest.fn()
    })

    const consoleSpy = jest.spyOn(console, 'log').mockImplementation()

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('no-user')
    })

    const getTokenButton = screen.getByText('Get Token')
    
    await act(async () => {
      getTokenButton.click()
    })

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Token:', null)
    })

    consoleSpy.mockRestore()
  })
}) 