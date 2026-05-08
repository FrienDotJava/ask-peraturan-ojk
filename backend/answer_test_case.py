from setup_agent import get_agent
import json
import time

test_cases = [
    {
        "question": "Apa yang dimaksud dengan Penjaminan menurut peraturan OJK?",
        "ground_truth": "Penjaminan adalah kegiatan pemberian jaminan atas pemenuhan kewajiban finansial Terjamin."
    },
    {
        "question": "Berapa jumlah modal mendirikan Perusahaan Penjaminan lingkup nasional?",
        "ground_truth": "Jumlah modal disetor atau setoran pokok dan sertifikat modal Perusahaan Penjaminan ditetapkan paling sedikit Rp100.000.000.000,00 (seratus miliar rupiah) untuk lingkup nasional."
    },
    {
        "question": "Berapa batas kepemilikan asing maksimum secara langsung maupun tidak langsung pada Lembaga Penjaminan berbentuk badan hukum Perseroan Terbatas?",
        "ground_truth": "Total kepemilikan asing pada Lembaga Penjaminan berbentuk badan hukum Perseroan Terbatas baik secara langsung maupun tidak langsung paling banyak sebesar 49% (empat puluh sembilan per seratus) dari modal disetor."
    },
    {
        "question": "Berapa modal kerja minimum yang harus disisihkan oleh Perusahaan Penjaminan untuk pembentukan Unit Usaha Syariah?",
        "ground_truth": "Modal kerja yang harus disisihkan untuk pembentukan Unit Usaha Syariah dari Perusahaan Penjaminan adalah sebesar Rp10.000.000.000,00 (sepuluh miliar rupiah)."
    },
    {
        "question": "Apa pengertian dari Usaha Produktif berdasarkan ketentuan POJK Penyelenggaraan Usaha Lembaga Penjaminan?",
        "ground_truth": "Usaha Produktif adalah kegiatan untuk menghasilkan barang dan/atau jasa yang memberikan nilai tambah dan meningkatkan pendapatan bagi Terjamin."
    },
    {
        "question": "Berapa rasio likuiditas paling sedikit yang wajib dijaga oleh Lembaga Penjaminan?",
        "ground_truth": "Rasio likuiditas Lembaga Penjaminan ditetapkan paling sedikit 150% (seratus lima puluh per seratus)."
    },
    {
        "question": "Berapa komisi maksimal yang dapat diberikan kepada agen penjamin dari Imbal Jasa Penjaminan (IJP)?",
        "ground_truth": "Klausula pemberian komisi kepada agen Penjamin paling tinggi sebesar 20% (dua puluh per seratus) dari IJP."
    },
    {
        "question": "Berapa persentase minimum cadangan umum dari laba bersih yang wajib dimiliki Lembaga Penjaminan pada tiap akhir periode laporan tahunan?",
        "ground_truth": "Lembaga Penjaminan wajib memiliki cadangan umum paling sedikit 25% (dua puluh lima per seratus) dari laba bersih atau selisih hasil usaha pada tiap akhir periode laporan tahunan."
    },
    {
        "question": "Apa tujuan dilakukannya Pemeriksaan terhadap Lembaga Penjaminan oleh Otoritas Jasa Keuangan?",
        "ground_truth": "Pemeriksaan bertujuan untuk memperoleh keyakinan mengenai kondisi Lembaga Penjaminan yang sebenarnya, meneliti kesesuaian kondisi dengan peraturan perundang-undangan dan praktik yang sehat, serta memastikan bahwa Lembaga Penjaminan telah melakukan upaya pemenuhan kewajiban kepada Penerima Jaminan."
    },
    {
        "question": "Berapa kali sekurang-kurangnya pemeriksaan berkala dilakukan terhadap Lembaga Penjaminan dalam satu tahun?",
        "ground_truth": "Pelaksanaan Pemeriksaan terhadap setiap Lembaga Penjaminan secara berkala dilakukan paling sedikit 1 (satu) kali dalam 1 (satu) tahun."
    },
    {
        "question": "Bagaimana tahap Pemeriksaan Lembaga Penjaminan yang dilakukan oleh OJK?",
        "ground_truth": "Pemeriksaan berkala meliputi pemeriksaan atas substansi laporan berkala dan kepatuhan terhadap peraturan perundang-undangan di bidang lembaga penjaminan."
    },
    {
        "question": "Berapa batas nominal terendah Pinjaman atau Pembiayaan yang wajib dilayani oleh Lembaga Keuangan Mikro (LKM)?",
        "ground_truth": "Batas Pinjaman atau Pembiayaan terendah yang dilayani oleh LKM adalah sebesar Rp50.000,- (lima puluh ribu Rupiah)."
    },
    {
        "question": "Berapa batas maksimum pemberian Pinjaman atau Pembiayaan Lembaga Keuangan Mikro (LKM) untuk nasabah kelompok?",
        "ground_truth": "Batas maksimum pemberian Pinjaman atau Pembiayaan untuk nasabah kelompok ditetapkan paling tinggi 10% (sepuluh persen) dari modal LKM."
    },
    {
        "question": "Dari mana saja sumber pendanaan Lembaga Keuangan Mikro (LKM) dapat berasal?",
        "ground_truth": "Sumber pendanaan LKM hanya dapat berasal dari: ekuitas, Simpanan, pinjaman, dan/atau hibah."
    },
    {
        "question": "Berapa nilai minimum layanan pembukaan Simpanan yang tidak boleh ditolak oleh Lembaga Keuangan Mikro (LKM)?",
        "ground_truth": "Batas nilai minimum untuk layanan pembukaan Simpanan ditetapkan sebesar Rp5.000,- (lima ribu Rupiah)."
    },
    {
        "question": "Bagaimana pengelompokkan penilaian kualitas Pinjaman atau Pembiayaan di Lembaga Keuangan Mikro (LKM)?",
        "ground_truth": "Penilaian kualitas Pinjaman atau Pembiayaan ditetapkan menjadi 3 (tiga) kelompok yaitu: lancar, diragukan, dan macet."
    },
    {
        "question": "Berapa persentase penyisihan penghapusan Pinjaman atau Pembiayaan yang wajib dibentuk LKM untuk kredit dengan kualitas diragukan?",
        "ground_truth": "LKM wajib membentuk penyisihan penghapusan Pinjaman atau Pembiayaan paling kurang 50% (lima puluh persen) dari Pinjaman atau Pembiayaan dengan kualitas diragukan."
    },
    {
        "question": "Apa saja bentuk badan hukum yang diizinkan untuk menyelenggarakan Usaha Pergadaian?",
        "ground_truth": "Bentuk badan hukum Perusahaan Pergadaian adalah perseroan terbatas atau koperasi."
    },
    {
        "question": "Berapa Modal Disetor paling sedikit untuk mendirikan Perusahaan Pergadaian lingkup wilayah usaha kabupaten/kota?",
        "ground_truth": "Jumlah Modal Disetor Perusahaan Pergadaian untuk lingkup wilayah usaha kabupaten/kota ditetapkan paling sedikit Rp500.000.000,00 (lima ratus juta rupiah)."
    },
    {
        "question": "Berapa bulan batas jangka waktu paling lama untuk pinjaman dengan jaminan berdasarkan hukum Gadai?",
        "ground_truth": "Jangka waktu pinjaman kepada Nasabah dengan jaminan berdasarkan hukum Gadai paling lama 4 (empat) bulan."
    },
    {
        "question": "Berapa batas maksimum total pemberian pinjaman dana kepada setiap Penerima Pinjaman dalam Layanan Pinjam Meminjam Uang Berbasis Teknologi Informasi (Fintech)?",
        "ground_truth": "Batas maksimum total pemberian pinjaman dana kepada setiap Penerima Pinjaman ditetapkan sebesar Rp2.000.000.000,00 (dua miliar rupiah)."
    },
    {
        "question": "Berapa maksimal kepemilikan saham oleh warga negara asing atau badan hukum asing pada penyelenggara Fintech P2P Lending?",
        "ground_truth": "Kepemilikan saham Penyelenggara oleh warga negara asing dan/atau badan hukum asing, baik secara langsung maupun tidak langsung paling banyak 85% (delapan puluh lima persen)."
    },
    {
        "question": "Apa syarat nilai transaksi tunai yang mewajibkan Penyedia Jasa Keuangan untuk melakukan prosedur Uji Tuntas Nasabah (Customer Due Diligence)?",
        "ground_truth": "Prosedur CDD wajib dilakukan saat terdapat transaksi keuangan dengan mata uang rupiah dan/atau mata uang asing yang nilainya paling sedikit atau setara dengan Rp100.000.000,00 (seratus juta rupiah)."
    },
    {
        "question": "Apa pengertian Walk in Customer (WIC) dalam Peraturan Penerapan Program Anti Pencucian Uang di Sektor Jasa Keuangan?",
        "ground_truth": "Walk in Customer (WIC) adalah pihak yang menggunakan jasa PJK di Sektor Perbankan atau Pasar Modal namun tidak memiliki rekening pada PJK tersebut, tidak termasuk pihak yang mendapat perintah atau penugasan dari Nasabah untuk transaksi kepentingan Nasabah."
    },
    {
        "question": "Siapa pihak yang berwenang untuk melakukan penyidikan tindak pidana di Sektor Jasa Keuangan berdasarkan POJK No.22/POJK.01/2015?",
        "ground_truth": "Otoritas Jasa Keuangan berwenang melakukan penyidikan, yang pelaksanaannya dilakukan oleh Penyidik OJK yang terdiri atas Pejabat Penyidik Kepolisian Negara Republik Indonesia dan/atau Pejabat Pegawai Negeri Sipil yang diberi wewenang khusus sebagai Penyidik."
    }
]

agent = get_agent()

questions = []
answers = []
contexts = []
ground_truths = []

for case in test_cases:
    retries = 3
    while retries > 0:
        try:
            print(f"Running: {case['question']}")
            result = agent.invoke({"question": case["question"], "is_evaluate": True})

            questions.append(case["question"])
            answers.append(result["answer"])
            contexts.append([doc.page_content for doc in result["retrieved_docs"]])
            ground_truths.append(case["ground_truth"])

            print(f"\tAnswer: {result['answer']}")
            break
        except Exception as e:
            if "429" in e:
                print("Rate limit hit, sleeping longer...")
                time.sleep(60)
                retries -= 1
            else:
                raise e

    time.sleep(40)

data = {
    "user_input": questions,
    "response": answers,
    "retrieved_contexts": contexts,
    "reference": ground_truths
}
with open('test_cases.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)