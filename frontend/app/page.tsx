"use client"

import { useState, useRef, useEffect } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "../components/ui/avatar"
import { Button } from "../components/ui/button"
import { Mic, Send, LogOut } from "lucide-react"
import ProtectedRoute from "../components/ProtectedRoute"
import { useAuth } from "../contexts/AuthContext"
import { config } from "../lib/config"

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: string
}

function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isComposing, setIsComposing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { user, logout, getValidToken } = useAuth()

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      const scrollHeight = textareaRef.current.scrollHeight
      const maxHeight = 5 * 20 // 5行分の高さ (line-height: 20px)
      const minHeight = 20 // 1行分の高さ
      
      if (inputValue.trim() === '') {
        // 入力がない場合は1行の高さを維持
        textareaRef.current.style.height = minHeight + 'px'
      } else {
        // 入力がある場合は内容に応じてリサイズ
        textareaRef.current.style.height = Math.min(Math.max(scrollHeight, minHeight), maxHeight) + 'px'
      }
    }
  }, [inputValue])

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('ログアウトエラー:', error)
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    // ユーザーメッセージを追加
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    }
    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    // agentsChat エンドポイントへリクエスト
    try {
      console.log('🔧 DEBUG: チャットメッセージ送信開始');
      console.log('🔧 DEBUG: inputValue:', inputValue);
      
      // 新しいgetValidToken関数を使用
      const idToken = await getValidToken()
      console.log('🔧 DEBUG: idToken取得:', idToken ? '成功' : '失敗');
      
      if (!idToken) {
        throw new Error('認証トークンの取得に失敗しました')
      }
      
      const apiUrl = config.getApiUrl(config.endpoints.agent);
      console.log('🔧 DEBUG: API URL:', apiUrl);
      console.log('🔧 DEBUG: config.endpoints.agent:', config.endpoints.agent);
      console.log('🔧 DEBUG: config.apiBaseUrl:', config.apiBaseUrl);
      console.log('🔧 DEBUG: Environment:', process.env.NODE_ENV);
      console.log('🔧 DEBUG: NEXT_PUBLIC_API_BASE_URL:', process.env.NEXT_PUBLIC_API_BASE_URL);
      
      const requestBody = { prompt: inputValue };
      console.log('🔧 DEBUG: Request body:', requestBody);
      
      const requestOptions = {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${idToken}`
        },
        // credentials: "include", // 一時的にコメントアウト
        body: JSON.stringify(requestBody),
      };
      console.log('🔧 DEBUG: Request options:', requestOptions);
      
      console.log('🔧 DEBUG: fetchリクエスト送信中...');
      const res = await fetch(apiUrl, requestOptions);
      console.log('🔧 DEBUG: fetchレスポンス受信:', res.status, res.statusText);
      const data = await res.json()
      console.log('🔧 DEBUG: レスポンスデータ:', data);
      
      // レスポンスステータスに応じて表示するメッセージを選択
      const messageText = res.ok
        ? data.message
        : data.error || "エラーが発生しました"
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: messageText,
        isUser: false,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      }
      setMessages((prev) => [...prev, botMessage])
    } catch (error) {
      console.error("agentsChat error:", error)
      // エラー時もメッセージとして表示
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "エラーが発生しました。しばらく待ってからもう一度お試しください。",
        isUser: false,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      // ローディング終了
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && !isComposing) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-md mx-auto bg-gray-50">
      {/* Header with logout */}
      <div className="flex justify-between items-center p-4 bg-white border-b">
        <h1 className="text-lg font-semibold">MY BODY COACH</h1>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">{user?.email}</span>
          <Button variant="ghost" size="sm" onClick={handleLogout}>
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}>
            {!message.isUser && (
              <Avatar className="h-8 w-8 mr-2 mt-1">
                <AvatarImage src="/placeholder.svg?height=32&width=32" />
                <AvatarFallback>BC</AvatarFallback>
              </Avatar>
            )}

            <div className="max-w-[75%]">
              <div
                className={`p-3 rounded-2xl whitespace-pre-wrap ${
                  message.isUser ? "bg-[#a8e1dc] text-gray-800" : "bg-white border border-gray-200"
                }`}
              >
                {message.content}
              </div>
              <div className="text-xs text-gray-500 mt-1 px-1">{message.timestamp}</div>
            </div>
          </div>
        ))}
        
        {/* ローディングインジケータ */}
        {isLoading && (
          <div className="flex justify-start">
            <Avatar className="h-8 w-8 mr-2 mt-1">
              <AvatarImage src="/placeholder.svg?height=32&width=32" />
              <AvatarFallback>BC</AvatarFallback>
            </Avatar>
            <div className="max-w-[75%]">
              <div className="p-3 rounded-2xl bg-white border border-gray-200">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0s" }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 pb-6 border-t">
        <div className="flex items-center bg-white rounded-2xl border overflow-hidden">
          <Button variant="ghost" size="icon" className="rounded-full h-10 w-10 ml-1">
            <Mic className="h-5 w-5 text-gray-500" />
          </Button>

          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onCompositionStart={() => setIsComposing(true)}
            onCompositionEnd={() => setIsComposing(false)}
            onKeyDown={handleKeyDown}
            placeholder="メッセージを入力してください"
            className="flex-1 border-0 focus:outline-none focus:ring-0 resize-none overflow-y-auto px-3 text-sm bg-transparent"
            rows={1}
            style={{ 
              lineHeight: '20px',
              height: '20px',
              minHeight: '20px',
              maxHeight: '100px',
              wordWrap: 'break-word',
              overflowWrap: 'break-word'
            }}
          />

          <Button
            size="icon"
            className="rounded-full h-8 w-8 bg-[#ffd465] hover:bg-[#ffc935] mr-2"
            onClick={handleSendMessage}
            disabled={inputValue.trim() === "" || isLoading}
          >
            <Send className="h-4 w-4 text-gray-800" />
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function Page() {
  return (
    <ProtectedRoute>
      <ChatPage />
    </ProtectedRoute>
  )
}
