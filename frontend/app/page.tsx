import Link from "next/link"

export default function Home() {
  return (
    <main className="min-h-screen bg-linear-to-br from-blue-50 to-white flex flex-col items-center justify-center px-4 text-center">
      <div className="max-w-2xl">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">AskPeraturan</h1>
        <p className="text-lg text-gray-600 mb-8">
          Tanya tentang peraturan Otoritas Jasa Keuangan (OJK). 
          Dijawab dengan AI berbasis dokumen resmi pemerintah.
        </p>
        <Link
          href="/chat"
          className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-full transition-colors"
        >
          Mulai Tanya →
        </Link>
        <div className="mt-12 grid grid-cols-3 gap-6 text-left">
          {[
            { icon: "📄", title: "Berbasis Dokumen Resmi", desc: "Jawaban dari dokumen resmi POJK" },
            { icon: "🔍", title: "Hybrid Search", desc: "Gabungan pencarian semantik dan keyword untuk hasil terbaik" },
            { icon: "📌", title: "Sumber Transparan", desc: "Setiap jawaban disertai referensi dokumen dan nomor halaman" },
          ].map((f) => (
            <div key={f.title} className="bg-white rounded-xl p-4 border border-gray-200 shadow-sm">
              <div className="text-2xl mb-2">{f.icon}</div>
              <h3 className="font-semibold text-gray-900 text-sm mb-1">{f.title}</h3>
              <p className="text-xs text-gray-500">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}