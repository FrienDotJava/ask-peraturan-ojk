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
  const res = await fetch("http://localhost:8000/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  })

  if (!res.ok) throw new Error("Failed to fetch answer")
  return res.json()
}