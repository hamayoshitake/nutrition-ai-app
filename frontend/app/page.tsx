"use client"

import { useState, useRef, useEffect } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Mic, Send, LogOut } from "lucide-react"
import ProtectedRoute from "@/components/ProtectedRoute"
import { useAuth } from "@/contexts/AuthContext"
import { config } from "@/lib/config"

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
  const { user, logout, getValidToken } = useAuth()

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

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
      // 新しいgetValidToken関数を使用
      const idToken = await getValidToken()
      
      if (!idToken) {
        throw new Error('認証トークンの取得に失敗しました')
      }
      
      const res = await fetch(
        config.getApiUrl(config.endpoints.agent),
        {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${idToken}`
          },
          credentials: "include",
          body: JSON.stringify({ prompt: inputValue }),
        }
      )
      const data = await res.json()
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
                className={`p-3 rounded-2xl ${
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
      <div className="p-4 border-t">
        <div className="flex items-center bg-white rounded-full border overflow-hidden pr-2">
          <Button variant="ghost" size="icon" className="rounded-full h-10 w-10">
            <Mic className="h-5 w-5 text-gray-500" />
          </Button>

          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onCompositionStart={() => setIsComposing(true)}
            onCompositionEnd={() => setIsComposing(false)}
            placeholder="メッセージを入力してください"
            className="flex-1 border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !isComposing) {
                handleSendMessage()
              }
            }}
          />

          <Button
            size="icon"
            className="rounded-full h-8 w-8 bg-[#ffd465] hover:bg-[#ffc935]"
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
