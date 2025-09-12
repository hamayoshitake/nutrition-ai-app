import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createUserWithEmailAndPassword } from 'firebase/auth'
import RegisterPage from '@/app/register/page'
import { AuthProvider } from '../contexts/AuthContext'

// Firebase Auth のモック
jest.mock('firebase/auth')
const mockCreateUserWithEmailAndPassword = createUserWithEmailAndPassword as jest.MockedFunction<typeof createUserWithEmailAndPassword>

// Next.js router のモック
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

// fetch のモック
global.fetch = jest.fn()

// AuthProvider でラップするヘルパー関数
const renderWithAuth = (component: React.ReactElement) => {
  return render(
    <AuthProvider>
      {component}
    </AuthProvider>
  )
}

describe('RegisterPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // fetch のデフォルトモック
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ success: true }),
    })
  })

  test('登録フォームが正しく表示される', () => {
    renderWithAuth(<RegisterPage />)
    
    expect(screen.getByText('MY BODY COACH')).toBeInTheDocument()
    expect(screen.getByText('新しいアカウントを作成してください')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('メールアドレス')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('パスワード（6文字以上）')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('パスワード確認')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'アカウント作成' })).toBeInTheDocument()
    expect(screen.getByText('既にアカウントをお持ちの方はこちら')).toBeInTheDocument()
  })

  test('有効な情報でユーザー登録が成功する', async () => {
    const user = userEvent.setup()
    
    // Firebase Auth のモック設定
    const mockUser = {
      uid: 'test-uid',
      email: 'test@example.com',
      displayName: null,
      getIdToken: jest.fn().mockResolvedValue('mock-token'),
    }
    mockCreateUserWithEmailAndPassword.mockResolvedValue({
      user: mockUser,
    } as any)

    renderWithAuth(<RegisterPage />)

    // フォーム入力
    await user.type(screen.getByPlaceholderText('メールアドレス'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('パスワード（6文字以上）'), 'password123')
    await user.type(screen.getByPlaceholderText('パスワード確認'), 'password123')

    // 登録ボタンクリック
    await user.click(screen.getByRole('button', { name: 'アカウント作成' }))

    // Firebase Auth が呼ばれることを確認
    await waitFor(() => {
      expect(mockCreateUserWithEmailAndPassword).toHaveBeenCalledWith(
        expect.anything(),
        'test@example.com',
        'password123'
      )
    })

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

    // ページ遷移が発生することを確認
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/')
    })
  })

  test('パスワードが一致しない場合エラーが表示される', async () => {
    const user = userEvent.setup()
    
    renderWithAuth(<RegisterPage />)

    // フォーム入力（パスワード不一致）
    await user.type(screen.getByPlaceholderText('メールアドレス'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('パスワード（6文字以上）'), 'password123')
    await user.type(screen.getByPlaceholderText('パスワード確認'), 'password456')

    // 登録ボタンクリック
    await user.click(screen.getByRole('button', { name: 'アカウント作成' }))

    // エラーメッセージが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText('パスワードが一致しません。')).toBeInTheDocument()
    })

    // Firebase Auth が呼ばれないことを確認
    expect(mockCreateUserWithEmailAndPassword).not.toHaveBeenCalled()
  })

  test('パスワードが6文字未満の場合エラーが表示される', async () => {
    const user = userEvent.setup()
    
    renderWithAuth(<RegisterPage />)

    // フォーム入力（短いパスワード）
    await user.type(screen.getByPlaceholderText('メールアドレス'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('パスワード（6文字以上）'), '12345')
    await user.type(screen.getByPlaceholderText('パスワード確認'), '12345')

    // 登録ボタンクリック
    await user.click(screen.getByRole('button', { name: 'アカウント作成' }))

    // エラーメッセージが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText('パスワードは6文字以上で入力してください。')).toBeInTheDocument()
    })

    // Firebase Auth が呼ばれないことを確認
    expect(mockCreateUserWithEmailAndPassword).not.toHaveBeenCalled()
  })

  test('Firebase Auth でエラーが発生した場合エラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    
    // Firebase Auth のエラーモック
    mockCreateUserWithEmailAndPassword.mockRejectedValue(new Error('Firebase Auth Error'))

    renderWithAuth(<RegisterPage />)

    // フォーム入力
    await user.type(screen.getByPlaceholderText('メールアドレス'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('パスワード（6文字以上）'), 'password123')
    await user.type(screen.getByPlaceholderText('パスワード確認'), 'password123')

    // 登録ボタンクリック
    await user.click(screen.getByRole('button', { name: 'アカウント作成' }))

    // エラーメッセージが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText('登録に失敗しました。メールアドレスが既に使用されている可能性があります。')).toBeInTheDocument()
    })
  })

  test('ローディング中はボタンが無効化される', async () => {
    const user = userEvent.setup()
    
    // Firebase Auth を遅延させる
    mockCreateUserWithEmailAndPassword.mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 1000))
    )

    renderWithAuth(<RegisterPage />)

    // フォーム入力
    await user.type(screen.getByPlaceholderText('メールアドレス'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('パスワード（6文字以上）'), 'password123')
    await user.type(screen.getByPlaceholderText('パスワード確認'), 'password123')

    // 登録ボタンクリック
    await user.click(screen.getByRole('button', { name: 'アカウント作成' }))

    // ローディング状態の確認
    await waitFor(() => {
      expect(screen.getByRole('button', { name: '登録中...' })).toBeDisabled()
    })
  })

  test('バックエンドAPIエラーでもユーザー登録は完了する', async () => {
    const user = userEvent.setup()
    
    // Firebase Auth は成功
    const mockUser = {
      uid: 'test-uid',
      email: 'test@example.com',
      displayName: null,
      getIdToken: jest.fn().mockResolvedValue('mock-token'),
    }
    mockCreateUserWithEmailAndPassword.mockResolvedValue({
      user: mockUser,
    } as any)

    // バックエンドAPI は失敗
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 500,
    })

    renderWithAuth(<RegisterPage />)

    // フォーム入力
    await user.type(screen.getByPlaceholderText('メールアドレス'), 'test@example.com')
    await user.type(screen.getByPlaceholderText('パスワード（6文字以上）'), 'password123')
    await user.type(screen.getByPlaceholderText('パスワード確認'), 'password123')

    // 登録ボタンクリック
    await user.click(screen.getByRole('button', { name: 'アカウント作成' }))

    // Firebase Auth が呼ばれることを確認
    await waitFor(() => {
      expect(mockCreateUserWithEmailAndPassword).toHaveBeenCalled()
    })

    // ページ遷移は発生する（Firebase Auth は成功したため）
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/')
    })
  })
}) 