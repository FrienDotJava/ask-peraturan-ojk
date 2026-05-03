export default function SourceCard({ source, title, page }: { source: string; title: string; page: number }) {
  const filename = source.split("/").pop() ?? source

  return (
    <div className="flex items-center gap-2 bg-blue-50 border border-blue-100 rounded-lg px-3 py-2 text-xs text-blue-700">
      <svg className="w-3 h-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <div className="flex flex-col">
        <span className="truncate">{filename}</span>
        <span className="font-bold">{title}</span>
        <span className="shrink-0 text-blue-400">{page != 0 ? "Halaman " + (page) : "Internet"}</span>
      </div>
    </div>
  )
}