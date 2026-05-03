"use client"

import { useState, KeyboardEvent } from "react"

interface Props {
  onSubmit: (question: string) => void
  isLoading: boolean
}

const EXAMPLE_QUESTIONS = [
  "Apa syarat fintech terdaftar OJK?",
  "Bagaimana cara klaim BPJS rawat inap?",
  "Tarif pajak UMKM berapa persen?",
]

export default function QueryInput({ onSubmit, isLoading }: Props) {
  const [value, setValue] = useState("")

  function handleSubmit() {
    if (!value.trim()) return
    onSubmit(value)
    setValue("")
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="space-y-2">
      {/* Example questions */}
      <div className="flex flex-wrap gap-2">
        {EXAMPLE_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => onSubmit(q)}
            className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-full px-3 py-1 transition-colors"
            disabled={isLoading}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input area */}
      <div className="flex gap-2 items-end bg-white border border-gray-300 rounded-2xl px-4 py-3 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Tanyakan tentang peraturan Indonesia..."
          rows={1}
          className="flex-1 resize-none outline-none text-sm text-gray-800 placeholder-gray-400 bg-transparent"
          disabled={isLoading}
        />
        <button
          onClick={handleSubmit}
          disabled={isLoading || !value.trim()}
          className="shrink-0 w-8 h-8 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-200 text-white rounded-full flex items-center justify-center transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  )
}