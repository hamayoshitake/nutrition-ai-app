'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { 
  User, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut, 
  onAuthStateChanged 
} from 'firebase/auth';
import { auth } from '../lib/firebase';
import { config } from '../lib/config';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  getValidToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // サーバーサイドレンダリング対応
  const isClient = typeof window !== 'undefined';

  // トークンの自動更新機能（30分間隔）
  const getValidToken = useCallback(async (): Promise<string | null> => {
    if (!user) return null;
    
    try {
      // 強制的に新しいトークンを取得（30分の有効期限）
      const token = await user.getIdToken(true);
      return token;
    } catch (error) {
      console.error('トークン取得エラー:', error);
      return null;
    }
  }, [user]);

  // 25分間隔でトークンを自動更新
  useEffect(() => {
    if (!user) return;

    const tokenRefreshInterval = setInterval(async () => {
      try {
        await user.getIdToken(true);
        console.log('✅ トークンを自動更新しました');
      } catch (error) {
        console.error('❌ トークン自動更新エラー:', error);
      }
    }, 25 * 60 * 1000); // 25分間隔

    return () => clearInterval(tokenRefreshInterval);
  }, [user]);

  useEffect(() => {
    // クライアントサイドでのみ認証状態を監視
    if (!isClient || !auth) {
      setLoading(false);
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    return unsubscribe;
  }, [isClient]);

  const signIn = async (email: string, password: string) => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (error: any) {
      // エラーメッセージを日本語で処理
      const errorCode = error.code;
      let errorMessage = '';
      
      switch (errorCode) {
        case 'auth/user-not-found':
          errorMessage = 'このメールアドレスは登録されていません。';
          break;
        case 'auth/wrong-password':
          errorMessage = 'パスワードが間違っています。';
          break;
        case 'auth/invalid-email':
          errorMessage = 'メールアドレスの形式が正しくありません。';
          break;
        case 'auth/user-disabled':
          errorMessage = 'このアカウントは無効化されています。';
          break;
        default:
          errorMessage = 'ログインに失敗しました。';
      }
      
      console.error('ログインエラー:', errorCode, errorMessage);
      throw new Error(errorMessage);
    }
  };

  const signUp = async (email: string, password: string) => {
    try {
      // Firebase Authenticationでユーザー作成
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // バックエンドにユーザープロフィールを作成
      try {
        const idToken = await user.getIdToken();
        const response = await fetch(config.getApiUrl(config.endpoints.createUserProfile), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${idToken}`
          },
          body: JSON.stringify({
            email: user.email,
            name: user.displayName || null
          })
        });
        
        if (!response.ok) {
          console.error('ユーザープロフィール作成に失敗しました');
        }
      } catch (error) {
        console.error('ユーザープロフィール作成エラー:', error);
      }
    } catch (error: any) {
      // Firebase Authentication エラーの処理
      const errorCode = error.code;
      let errorMessage = '';
      
      switch (errorCode) {
        case 'auth/email-already-in-use':
          errorMessage = 'このメールアドレスは既に使用されています。';
          break;
        case 'auth/invalid-email':
          errorMessage = 'メールアドレスの形式が正しくありません。';
          break;
        case 'auth/weak-password':
          errorMessage = 'パスワードが弱すぎます。6文字以上で設定してください。';
          break;
        default:
          errorMessage = 'ユーザー登録に失敗しました。';
      }
      
      console.error('ユーザー登録エラー:', errorCode, errorMessage);
      throw new Error(errorMessage);
    }
  };

  const logout = async () => {
    await signOut(auth);
  };

  const value = {
    user,
    loading,
    signIn,
    signUp,
    logout,
    getValidToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};