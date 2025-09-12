// API設定
export const config = {
  // 環境判定
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production',
  
  // 環境変数から取得
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
  
  // APIベースURL（本番環境用のデフォルト値を設定）
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 
    (process.env.NODE_ENV === 'production' 
      ? 'https://us-central1-nutrition-ai-app-bdee9.cloudfunctions.net'
      : 'http://127.0.0.1:5005/nutrition-ai-app-bdee9/us-central1'),
  
  // エンドポイント
  endpoints: {
    agent: '/agent',
    createUserProfile: '/createUserProfile',
    helloWorld: '/helloWorld'
  },
  
  // 完全なAPIエンドポイントを取得する関数
  getApiUrl: (endpoint: string) => {
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 
      (process.env.NODE_ENV === 'production' 
        ? 'https://us-central1-nutrition-ai-app-bdee9.cloudfunctions.net'
        : 'http://127.0.0.1:5005/nutrition-ai-app-bdee9/us-central1')
    return `${baseUrl}${endpoint}`
  }
}

// デバッグ用ログ（開発環境のみ）
if (config.isDevelopment) {
  console.log('🔧 API Configuration:', {
    environment: config.environment,
    apiBaseUrl: config.apiBaseUrl,
    agentUrl: config.getApiUrl(config.endpoints.agent)
  })
} 