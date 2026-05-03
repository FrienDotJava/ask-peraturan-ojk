
export interface Source {
  source: string
  title: string
  page?: number
}

export interface QueryResponse {
  answer: string
  sources: Source[]
}


export async function askQuestion(question: string): Promise<QueryResponse> {
  const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
  const res = await fetch(`${API_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  })
  if (!res.ok) throw new Error("Failed to fetch answer")
  return res.json()
}

// Streaming
export async function askQuestionStream(
  question: string,
  onToken: (token: string) => void,
  onSources: (sources: Source[]) => void,
  onDone: () => void,
  onError: (err: string) => void
) {
  const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
  const res = await fetch(`${API_URL}/api/query/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  })

  if (!res.ok || !res.body) {
    onError("Gagal terhubung ke server.")
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split("\n")
    buffer = lines.pop() ?? ""

    let currentEvent = ""
    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7).trim()
      } else if (line.startsWith("data: ")) {
        const data = line.slice(6).trim()
        if (currentEvent === "sources") {
          onSources(JSON.parse(data))
        } else if (currentEvent === "token") {
          onToken(JSON.parse(data))
        } else if (currentEvent === "done") {
          onDone()
        }
      }
    }
  }
}