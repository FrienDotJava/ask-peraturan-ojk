import SourceCard from "./SourceCard"
import ReactMarkdown from "react-markdown"

interface Message {
  role: "user" | "assistant"
  content: string
  sources?: { source: string; title: string; page?: number }[]
  loading?: boolean
  streaming?: boolean
}

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user"

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] ${isUser ? "order-2" : "order-1"}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? "bg-blue-600 text-white rounded-br-sm"
              : "bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm"
          }`}
        >
          {message.loading ? (
            <div className="flex gap-1 items-center h-5">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
            </div>
          ) : isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-ol:my-1 prose-li:my-0">
              <ReactMarkdown>{message.content}</ReactMarkdown>
              {message.streaming && (
                <span className="inline-block w-0.5 h-4 bg-gray-500 ml-0.5 animate-pulse" />
              )}
            </div>
          )}
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 space-y-1">
            <p className="text-xs text-gray-400 px-1">Sumber dokumen:</p>
            {message.sources.map((src, i) => (
              <SourceCard key={i} source={src.source} title={src.title} page={src.page ?? 0} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}