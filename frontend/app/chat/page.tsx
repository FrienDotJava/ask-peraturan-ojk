"use client"

import { useState, useRef, useEffect } from "react"
import { askQuestion, QueryResponse } from "@/lib/api"
import MessageBubble from "@/components/MessageBubble"
import QueryInput from "@/components/QueryInput"

interface Message {
  role: "user" | "assistant"
  content: string
  sources?: QueryResponse["sources"]
  loading?: boolean
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Halo! Saya AskPeraturan. Tanyakan apapun tentang peraturan mengenai OJK.",
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  async function handleSubmit(question: string) {
    if (!question.trim() || isLoading) return

    // Add user message
    setMessages(prev => [...prev, { role: "user", content: question }])
    
    // Add loading placeholder
    setMessages(prev => [...prev, { role: "assistant", content: "", loading: true }])
    setIsLoading(true)

    try {
      const result = await askQuestion(question)
      
      // Replace loading placeholder with real answer
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: "assistant", content: result.answer, sources: result.sources }
      ])
    } catch {
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: "assistant", content: "Terjadi kesalahan. Coba lagi." }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-bold">
          AP
        </div>
        <div>
          <h1 className="font-semibold text-gray-900">AskPeraturan</h1>
          <p className="text-xs text-gray-500">Asisten hukum & regulasi Indonesia</p>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 max-w-3xl mx-auto w-full">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t bg-white px-4 py-4">
        <div className="max-w-3xl mx-auto">
          <QueryInput onSubmit={handleSubmit} isLoading={isLoading} />
          <p className="text-xs text-center text-gray-400 mt-2">
            Jawaban berdasarkan dokumen peraturan resmi. Bukan pengganti konsultasi hukum.
          </p>
        </div>
      </div>
    </div>
  )
}