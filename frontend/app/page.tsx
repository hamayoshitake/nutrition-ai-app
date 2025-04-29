"use client"

import { useState, useRef, useEffect } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Mic, Send } from "lucide-react"

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello Vincent, thank you for calling Provide! 😊",
      isUser: true,
      timestamp: "10:20 Am",
    },
    {
      id: "2",
      content: "Perfect, I am really glad to hear that! 😊",
      isUser: false,
      timestamp: "10:30 Am",
    },
    {
      id: "3",
      content: "I am really sorry to hear that. Is there anything I can do to help you? 😊",
      isUser: true,
      timestamp: "10:36 Am",
    },
    {
      id: "4",
      content: "That is a good! 😃",
      isUser: false,
      timestamp: "10:39 Am",
    },
    {
      id: "5",
      content: "I'm not sure, but let me find...",
      isUser: true,
      timestamp: "10:40 Am",
    },
  ])

  const [inputValue, setInputValue] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSendMessage = () => {
    if (inputValue.trim() === "") return

    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    }

    setMessages([...messages, newMessage])
    setInputValue("")

    // Simulate a response after a short delay
    setTimeout(() => {
      const responseMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Thanks for your message!",
        isUser: false,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      }
      setMessages((prev) => [...prev, responseMessage])
    }, 1000)
  }

  return (
    <div className="flex flex-col h-screen max-w-md mx-auto bg-gray-50">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}>
            {!message.isUser && (
              <Avatar className="h-8 w-8 mr-2 mt-1">
                <AvatarImage src="/placeholder.svg?height=32&width=32" />
                <AvatarFallback>VN</AvatarFallback>
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
            placeholder="Type something..."
            className="flex-1 border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
          />

          <Button
            size="icon"
            className="rounded-full h-8 w-8 bg-[#ffd465] hover:bg-[#ffc935]"
            onClick={handleSendMessage}
            disabled={inputValue.trim() === ""}
          >
            <Send className="h-4 w-4 text-gray-800" />
          </Button>
        </div>
      </div>
    </div>
  )
}
