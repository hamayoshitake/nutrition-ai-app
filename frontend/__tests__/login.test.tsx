import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { signInWithEmailAndPassword } from 'firebase/auth'
import LoginPage from '../app/login/page'
import { AuthProvider } from '../contexts/AuthContext'

// Firebase Auth のモック
jest.mock('firebase/auth')
const mockSignInWithEmailAndPassword = signInWithEmailAndPassword as jest.MockedFunction<typeof signInWithEmailAndPassword>

// Next.js router のモック
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

// AuthProvider でラップするヘルパー関数
const renderWithAuth = (component: React.ReactElement) => {
  return render(
    <AuthProvider>
      {component}
    </AuthProvider>
  )
}

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('ログインフォームが正しく表示される', () => {
    renderWithAuth(<LoginPage />)
    
    expect(screen.getByText('MY BODY COACH')).toBeInTheDocument()
    expect(screen.getByText('アカウントにログインしてください')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('メールアドレス')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('パスワード')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'ログイン' })).toBeInTheDocument()
    expect(screen.getByText('アカウントをお持ちでない方はこちら')).toBeInTheDocument()
  })

  test('有効な情報でログインが成功する', async () => {
    const user = userEvent.setup()
    
    // Firebase Auth のモック設定
    const mockUser = {
      uid: 'test-uid',
      email: 'test@example.com',
    }
    mockSignInWithEmailAndPassword.mockResolvedValue({
      user: mockUser,
    } as any)

    renderWithAuth(<LoginPage />)

    // フォーム入力
    await user.type(screen.getByPlaceholderText('メールアドレス'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('パスワード'), 'password123')

    // ログインボタンクリック
    await user.click(screen.getByRole('button', { name: 'ログイン' }))

    // Firebase Auth が呼ばれることを確認
    await waitFor(() => {
      expect(mockSignInWithEmailAndPassword).toHaveBeenCalledWith(
        expect.anything(),
        'test@example.com',
        'password123'
      )
    })

    // ページ遷移が発生することを確認
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/')
    })
  })

  test('Firebase Auth でエラーが発生した場合エラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    
    // Firebase Auth のエラーモック
    mockSignInWithEmailAndPassword.mockRejectedValue(new Error('Firebase Auth Error'))

    renderWithAuth(<LoginPage />)

    // フォーム入力
    await user.type(screen.getByPlaceholderText('メールアドレス'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('パスワード'), 'wrongpassword')

    // ログインボタンクリック
    await user.click(screen.getByRole('button', { name: 'ログイン' }))

    // エラーメッセージが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText('ログインに失敗しました。メールアドレスとパスワードを確認してください。')).toBeInTheDocument()
    })

    // ページ遷移が発生しないことを確認
    expect(mockPush).not.toHaveBeenCalled()
  })

  test('ローディング中はボタンが無効化される', async () => {
    const user = userEvent.setup()
    
    // Firebase Auth を遅延させる
    mockSignInWithEmailAndPassword.mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 1000))
    )

    renderWithAuth(<LoginPage />)

    // フォーム入力
    await user.type(screen.getByPlaceholderText('メールアドレス'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('パスワード'), 'password123')

    // ログインボタンクリック
    await user.click(screen.getByRole('button', { name: 'ログイン' }))

    // ローディング状態の確認
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'ログイン中...' })).toBeDisabled()
    })
  })

  test('必須フィールドが空の場合はフォーム送信されない', async () => {
    const user = userEvent.setup()
    
    renderWithAuth(<LoginPage />)

    // メールアドレスのみ入力
    await user.type(screen.getByPlaceholderText('メールアドレス'), 'test@example.com')

    // ログインボタンクリック
    await user.click(screen.getByRole('button', { name: 'ログイン' }))

    // Firebase Auth が呼ばれないことを確認
    expect(mockSignInWithEmailAndPassword).not.toHaveBeenCalled()
  })

  test('登録ページへのリンクが機能する', () => {
    renderWithAuth(<LoginPage />)
    
    const registerLink = screen.getByText('アカウントをお持ちでない方はこちら')
    expect(registerLink).toBeInTheDocument()
    expect(registerLink.closest('a')).toHaveAttribute('href', '/register')
  })
}) 