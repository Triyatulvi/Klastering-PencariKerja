import os
import joblib
from flask import Flask, Response, render_template, request
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import io
import base64
from database import get_db_connection

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/')
def dashboard():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM tbll_pencarikerja", conn)

    if df.empty:
        return "⚠️ Data kosong, cek database!"

    tahun_dipilih = request.args.get("tahun")
    daftar_tahun = df['Tahun'].dropna().unique()
    daftar_tahun.sort()

    if tahun_dipilih and tahun_dipilih.isdigit():
        df = df[df['Tahun'] == int(tahun_dipilih)]

    cursor = conn.cursor(dictionary=True)

    # MAPPING
    pendidikan_map = {
        0: "Diploma I", 1: "Diploma II", 2: "Diploma III", 3: "Diploma IV",
        4: "SD / MI / Sederajat", 5: "SLTA / MA", 6: "SLTP / MTS / Sederajat",
        7: "SMK / MAK", 8: "Strata 1", 9: "Strata 2", 10: "Tidak Memiliki Ijazah"
    }
    pengalaman_map = {
        0: "Tidak Ada", 1: "Information Technology (IT)", 2: "Lain - lain",
        3: "Operator dan Perakit Mesin", 4: "Pejabat Lembaga Legislatif, Pejabat Tinggi dan Manajer", 5: "Pekerja Kasar, Tenaga Kebersihan", 6: "Pariwisata dan Perhotelan",
        7: "Perbankan / Keuangan", 8: "Teknisi dan Asisten Tenaga Proffesional",9: "Tenaga Pengolahan dan Kerajinan",10: "Tenaga Profesional",11: "Tenaga Tata Usaha",12: "Tenaga Usaha Jasa dan Tenaga Penjualan di Toko dan Pasar",
        13: "Tenaga Usaha Pertanian dan Peternakan",14: "Akunting",15: "Arsitektur",16: "Kesehatan",
        17: "Manager",18: "Marketing",19: "Pendidikan",20: "Teknik",
    }
    sertifikat_map = {
    0:"Lainnya" ,1:  "Tidak Ada"
}

    prodi_map = {
        0: "Administrasi", 1: "Administrasi Niaga", 2: "Administrasi Perkantoran", 3: "Administrasi Rumah Sakit",
        4: "Agribisnis", 5: "Agroteknologi", 6: "Akutansi", 7: "Analis Kesehatan", 8: "Animasi", 9: "Arsitektur",
        10: "Bahasa Inggris", 11: "Bahasa dan Sastra Indonesia", 12: "Bimbingan dan Konseling", 13: "Biologi",
        14: "Bioteknologi", 15: "Desain Grafis", 16: "Desain Interior", 17: "Desain Komunikasi Visual",
        18: "Desain Produk", 19: "Ekonomi Islam", 20: "Ekonomi Pembangunan", 21: "Farmasi", 22: "Fisika",
        23: "Fisioterapi", 24: "Gizi", 25: "Hubungan Internasional", 26: "Hukum Ekonomi Syariah",
        27: "Hukum Keluarga (Ahwal Syakhshiyah)", 28: "Hukum Tata Negara", 29: "IPA", 30: "IPS",
        31: "Ilmu Administrasi", 32: "Ilmu Administrasi Negara", 33: "Ilmu Administrasi Niaga",
        34: "Ilmu Administrasi Publik", 35: "Ilmu Ekonomi", 36: "Ilmu Filsafat", 37: "Ilmu Hukum",
        38: "Ilmu Keperawatan", 39: "Ilmu Kesehatan Masyarakat", 40: "Ilmu Kesejahteraan Sosial",
        41: "Ilmu Komunikasi", 42: "Ilmu Manajemen", 43: "Ilmu Perpustakaan", 44: "Ilmu Politik",
        45: "Ilmu Sejarah", 46: "Ilmu Teknik Sipil", 47: "Kebidanan", 48: "Kecantikan Rambut", 49: "Kenotariatan",
        50: "Kepariwisataan", 51: "Keperawatan", 52: "Kesekretariatan", 53: "Ketatalaksanaan Pelayaran Niaga dan Kepelabuhan",
        54: "Keuangan dan Perbankan", 55: "Kewirausahaan", 56: "Kimia", 57: "Komputer Grafis dan Cetak",
        58: "Komputer Multimedia", 59: "Komputer Akutansi", 60: "Konstruksi Batu dan Beton", 61: "Listrik",
        62: "Manajemen", 63: "Manajemen Informatika", 64: "Manajemen Pariwisata", 65: "Manajemen Pemasaran",
        66: "Manajemen Pemerintah", 67: "Manajemen Pendidikan", 68: "Manajemen Perhotelan",
        69: "Manajemen Perpajakan", 70: "Manajemen Perusahaan", 71: "Manajemen Zakat dan Wakaf", 72: "Matematika",
        73: "Nautika", 74: "PSKGJ Bimbingan dan Konseling", 75: "PSKGJ Pendidikan Bahasa Inggris",
        76: "PSKGJ Pendidikan Guru Sekolah Dasar(PGSD)", 77: "PSKGJ Pendidikan Kesejahteraan Keluarga",
        78: "PSKGJ Pendidikan Matematika", 79: "PSKGJ Pendidikan Pancasila dan Kewarganegaraan", 80: "Patiseri",
        81: "Pendidikan Agama Islam", 82: "Pendidikan Bahasa Dan Sastra Indonesia", 83: "Pendidikan Bahasa Inggris",
        84: "Pendidikan Bahasa Mandarin", 85: "Pendidikan Biologi", 86: "Pendidikan Dokter", 87: "Pendidikan Dokter Gigi",
        88: "Pendidikan Dokter Hewan", 89: "Pendidikan Ekonomi", 90: "Pendidikan Fisika",
        91: "Pendidikan Guru Madrasah Ibtidaiyah", 92: "Pendidikan Guru Pendidikan Anak Usia Dini",
        93: "Pendidikan Guru Sekolah Dasar", 94: "Pendidikan Islam", 95: "Pendidikan Kepelatihan Olahraga",
        96: "Pendidikan Khusus", 97: "Pendidikan Kimia", 98: "Pendidikan Matematika", 99: "Pendidikan Olahraga",
        100: "Pendidikan Pancasila Dan Kewarganegaraan", 101: "Pendidikan Sejarah",
        102: "Pendidikan Seni Drama, Tari dan Musik", 103: "Pendidikan Seni Rupa", 104: "Pendidikan Sosiologi",
        105: "Perbandingan Agama", 106: "Perbankan Syariah", 107: "Perencanaan Wilayah Dan Kota",
        108: "Perhotelan", 109: "Perikanan", 110: "Perpajakan", 111: "Perpustakaan dan Arsip",
        112: "Profesi Akuntan", 113: "Profesi Dokter", 114: "Profesi Ners", 115: "Psikologi",
        116: "Rekam Medik dan Informasi Kesehatan", 117: "Sastra Inggris", 118: "Sastra Jepang",
        119: "Sastra Jerman", 120: "Sastra Prancis", 121: "Seni Karawitan", 122: "Seni Musik",
        123: "Seni Tari", 124: "Seni Teater", 125: "Sistem Informasi", 126: "Sistem Komputer",
        127: "Sosial Ekonomi Pertanian", 128: "Sosiologi", 129: "Statistika", 130: "Tata Boga",
        131: "Tata Busana", 132: "Teknik Elektro", 133: "Teknik Elektronika", 134: "Teknik Industri",
        135: "Teknik Informatika", 136: "Teknik Kelautan", 137: "Teknik Kendaraan Ringan", 138: "Teknik Kimia",
        139: "Teknik Komputer", 140: "Teknik Lingkungan", 141: "Teknik Listrik Industri", 142: "Teknik Manufaktur",
        143: "Teknik Mesin", 144: "Teknik Mesin Kapal", 145: "Teknik Otomotif", 146: "Teknik Perkapalan",
        147: "Teknik Pertanian", 148: "Teknik Sipil", 149: "Teknik Sistem Perkapalan",
        150: "Teknik Telekomunikasi", 151: "Teknika", 152: "Teknologi Industri Pertanian",
        153: "Teknologi Informasi", 154: "Teknologi Pangan", 155: "Teknologi Pendidikan",
        156: "Televisi dan Film", 157: "Umum"
    }
    status_map = {
        0:"Belum Menikah", 1:"Duda",2:"Janda", 3:"Menikah"
    }
    disabilitas_map = {
        0: "Non-Disabilitas", 1: "Disabilitas"
    }


    # TINGKAT PENDIDIKAN
    cursor.execute(f"""
        SELECT tingkat_pendidikan AS pendidikan, COUNT(*) AS total
        FROM tabel_pencarikerja
        {f"WHERE Tahun = {tahun_dipilih}" if tahun_dipilih else ""}
        GROUP BY tingkat_pendidikan
        ORDER BY pendidikan
    """)
    pendidikan_data = cursor.fetchall()
    pendidikan = [pendidikan_map.get(row['pendidikan'], "Lainnya") for row in pendidikan_data]
    pencarikerja_counts = [row['total'] for row in pendidikan_data]

    # DISTRIBUSI USIA
    cursor.execute(f"""
        SELECT Usia AS usia, COUNT(*) AS total
        FROM tabel_pencarikerja
        {f"WHERE Tahun = {tahun_dipilih}" if tahun_dipilih else ""}
        GROUP BY Usia
        ORDER BY usia
    """)
    usia_data = cursor.fetchall()
    usia_labels = [str(row['usia']) for row in usia_data]
    usia_counts = [row['total'] for row in usia_data]

    # PENGALAMAN KERJA (BIDANG)
    cursor.execute(f"""
        SELECT `Pengalaman Kerja` AS pengalaman, COUNT(*) AS total
        FROM tabel_pencarikerja
        {f"WHERE Tahun = {tahun_dipilih}" if tahun_dipilih else ""}
        GROUP BY `Pengalaman Kerja`
        ORDER BY pengalaman
    """)
    pengalaman_data = cursor.fetchall()
    pengalaman_labels = [pengalaman_map.get(row['pengalaman'], "Lainnya") for row in pengalaman_data]
    pengalaman_counts = [row['total'] for row in pengalaman_data]

    # SERTIFIKAT
    cursor.execute(f"""
        SELECT `Sertifikat` AS sertifikat, COUNT(*) AS total
        FROM tabel_pencarikerja
        {f"WHERE Tahun = {tahun_dipilih}" if tahun_dipilih else ""}
        GROUP BY `Sertifikat`
        ORDER BY sertifikat
    """)
    sertifikat_data = cursor.fetchall()
    sertifikat_labels = [sertifikat_map.get(row['sertifikat'], "Lainnya") for row in sertifikat_data]
    sertifikat_counts = [row['total'] for row in sertifikat_data]

     # 10 Nama Prodi Terbanyak
    cursor.execute(f"""
        SELECT nama_prodi, COUNT(*) AS total
        FROM tabel_pencarikerja
        {f"WHERE Tahun = {tahun_dipilih}" if tahun_dipilih else ""}
        GROUP BY nama_prodi
        ORDER BY total DESC
        LIMIT 10
    """)
    prodi_data = cursor.fetchall()
    prodi_labels = [prodi_map.get(row['nama_prodi'], "Lainnya") for row in prodi_data]
    prodi_counts = [row['total'] for row in prodi_data]

        # STATUS PERNIKAHAN
    cursor.execute(f"""
        SELECT status_pernikahan, COUNT(*) AS total
        FROM tabel_pencarikerja
        {f"WHERE Tahun = {tahun_dipilih}" if tahun_dipilih else ""}
        GROUP BY status_pernikahan
        ORDER BY status_pernikahan
    """)
    status_data = cursor.fetchall()
    status_labels = [status_map.get(row['status_pernikahan'] ,"Lainnya")for row in status_data]
    status_counts = [row['total'] for row in status_data]

     # DISABILITAS
    cursor.execute(f"""
        SELECT disabilitas, COUNT(*) AS total
        FROM tabel_pencarikerja
        {f"WHERE Tahun = {tahun_dipilih}" if tahun_dipilih else ""}
        GROUP BY disabilitas
    """)
    disabilitas_data = cursor.fetchall()
    disabilitas_labels = [disabilitas_map.get(row['disabilitas']) for row in disabilitas_data]
    disabilitas_counts = [row['total'] for row in disabilitas_data]

     # JUMLAH ANAK
    cursor.execute(f"""
        SELECT jumlah_anak, COUNT(*) AS total
        FROM tabel_pencarikerja
        {f"WHERE Tahun = {tahun_dipilih}" if tahun_dipilih else ""}
        GROUP BY jumlah_anak
        ORDER BY jumlah_anak
    """)
    anak_data = cursor.fetchall()
    anak_labels = [str(row['jumlah_anak']) for row in anak_data]
    anak_counts = [row['total'] for row in anak_data]

    

    cursor.close()
    conn.close()

    total_pengalaman = df[df['Pengalaman Kerja'] > 0].shape[0]
    total_tanpa_pengalaman = df[df['Pengalaman Kerja'] == 0].shape[0]
    rata_rata_usia = round(df['Usia'].mean(), 1) if not df.empty else 0
    

    return render_template(
        "index.html",
        total_pencari=len(df),
        total_pengalaman=total_pengalaman,
        total_tanpa_pengalaman=total_tanpa_pengalaman,
        rata_rata_usia=rata_rata_usia,
        pendidikan=pendidikan,
        pencarikerja_counts=pencarikerja_counts,
        usia_labels=usia_labels,
        usia_counts=usia_counts,
        pengalaman_labels=pengalaman_labels,
        pengalaman_counts=pengalaman_counts,
        sertifikat_labels=sertifikat_labels,
        sertifikat_counts=sertifikat_counts,
        daftar_tahun=daftar_tahun,
        tahun_dipilih=int(tahun_dipilih) if tahun_dipilih and tahun_dipilih.isdigit() else "",
        prodi_labels=prodi_labels,
        prodi_counts=prodi_counts,
        status_labels=status_labels,
        status_counts=status_counts,
        disabilitas_labels=disabilitas_labels,
        disabilitas_counts=disabilitas_counts,
        anak_labels=anak_labels,
        anak_counts=anak_counts,
    )

# Fungsi klasifikasi sertifikat menjadi biner
def klasifikasi_sertifikat_biner(isi):
    kategori_dict = {
        'Kompetensi': 0, 'PKL/Prakerin': 0, 'Softskill': 0, 'Bahasa Internasional': 0,
        'Audit/Akuntansi': 0, 'Manajemen/Perpajakan/Administrasi': 0,
        'Profesi': 0, 'Teknologi': 0, 'Teknik': 0, 'Kesehatan': 0, 'Hukum': 0,
        'Food and Beverage': 0, 'Lainnya': 0
    }

    if pd.isna(isi) or str(isi).strip().lower() in ["", "tidak ada", "tdk ada", "ga ada", "gak ada", "kosong"]:
        return kategori_dict

    isi = str(isi).lower()
    cocok = False

    if any(x in isi for x in ['kompetensi', 'lsp', 'bnsp']):
        kategori_dict['Kompetensi'] = 1; cocok = True
    if any(x in isi for x in ['pkl', 'prakerin', 'magang', 'praktek kerja lapangan', 'praktik kerja', 'msib', 'internship']):
        kategori_dict['PKL/Prakerin'] = 1; cocok = True
    if any(x in isi for x in ['softskill', 'soft skill', 'komunikasi', 'pengembangan pribadi', 'public speaking', 'kepemimpinan', 'seminar', 'leadership', 'suspelatnas', 'lkmm']):
        kategori_dict['Softskill'] = 1; cocok = True
    if any(x in isi for x in ['bahasa inggris', 'toefl', 'ielts', 'toeic', 'english', 'jlpt n3', 'mandarin', 'arabic', 'delf b1', 'elpt']):
        kategori_dict['Bahasa Internasional'] = 1; cocok = True
    if any(x in isi for x in ['audit', 'akuntansi', 'accounting']):
        kategori_dict['Audit/Akuntansi'] = 1; cocok = True
    if any(x in isi for x in ['hrd', 'iso', 'brevet', 'administrasi perkantoran', 'admin', 'pajak', 'saham', 'sumber daya manusia', 'business', 'perbankan', 'sekretaris', 'chro', 'export', 'ekspor', 'pemasaran', 'bisnis', 'human capital staff', 'manager']):
        kategori_dict['Manajemen/Perpajakan/Administrasi'] = 1; cocok = True
    if any(x in isi for x in ['profesi', 'pkpa', 'kerja']):
        kategori_dict['Profesi'] = 1; cocok = True
    if any(x in isi for x in ['data analyst', 'microsoft', 'digital', 'oracle', 'komputer', 'it', 'data', 'visual basic', 'cisco', 'python', 'sap', 'quality assurance', 'start up', 'word', 'excel', 'backend']):
        kategori_dict['Teknologi'] = 1; cocok = True
    if any(x in isi for x in ['teknik', 'teknisi', 'konstruksi', 'welding', 'k3', 'plc', 'autocad', 'forklift', 'quality control', 'cswa', 'machinery', 'supply chain', 'mekanik', 'electronic', 'otomotif']):
        kategori_dict['Teknik'] = 1; cocok = True
    if any(x in isi for x in ['bidan', 'persalinan', 'surat tanda registrasi', 'ekg', 'ppgd', 'health', 'gizi']):
        kategori_dict['Kesehatan'] = 1; cocok = True
    if any(x in isi for x in ['legal', 'contract drafting']):
        kategori_dict['Hukum'] = 1; cocok = True
    if any(x in isi for x in ['food', 'starbucks', 'coffee', 'haccp']):
        kategori_dict['Food and Beverage'] = 1; cocok = True

    if not cocok:
        kategori_dict['Lainnya'] = 1

    return kategori_dict

# Fungsi preprocessing data
def preprocess_data(df):
    df_cleaned = df.copy()

    # Isi nilai kosong
    kolom_mode = ['status_pernikahan', 'nama_prodi']
    for col in kolom_mode:
        if col in df_cleaned.columns:
            df_cleaned[col].fillna(df_cleaned[col].mode()[0], inplace=True)

    # Ganti '{}' menjadi "tidak ada"
    for col in ['Pengalaman Kerja', 'Sertifikat']:
        if col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].replace("{}", "tidak ada")

    # Konversi sertifikat ke dalam bentuk biner kategori
    if 'Sertifikat' in df_cleaned.columns:
        sertifikat_dummies = df_cleaned['Sertifikat'].apply(klasifikasi_sertifikat_biner).apply(pd.Series)
        df_cleaned = pd.concat([df_cleaned, sertifikat_dummies], axis=1)
        df_cleaned.drop(['Sertifikat'], axis=1, inplace=True)

    # Drop kolom yang tidak diperlukan
    for col in ['Tanggal', 'Tahun', 'nama', 'no']:
        if col in df_cleaned.columns:
            df_cleaned.drop([col], axis=1, inplace=True)

    # Rename kolom
    if 'nama_pendidikan' in df_cleaned.columns:
        df_cleaned.rename(columns={'nama_pendidikan': 'tingkat_pendidikan'}, inplace=True)

    # Encode kolom kategorik
    categorical_cols = ['tingkat_pendidikan', 'Pengalaman Kerja', 'nama_prodi', 'disabilitas', 'status_pernikahan']
    label_encoder = LabelEncoder()
    for col in categorical_cols:
        if col in df_cleaned.columns:
            df_cleaned[col] = label_encoder.fit_transform(df_cleaned[col])

    return df_cleaned

@app.route('/hasil_klastering', methods=['GET', 'POST'])
def hasil_klastering():
    global uploaded_df, output_df

    error = None
    step = request.form.get('step', 'upload')
    sil_score = None
    dbi_score = None
    image_base64 = None
    cluster_insights = []

    

    if request.method == 'POST' and request.form.get('uploaded_df') == 'true':
        if 'output_df' in globals():
            output = io.StringIO()
            output_df.to_csv(output, index=False)
            output.seek(0)
            return Response(
                output,
                mimetype="text/csv",
                headers={"Content-Disposition": "attachment;filename=hasil_klastering.csv"}
            )
        else:
            return "Data tidak tersedia untuk diunduh.", 400

    if request.method == 'POST':
        if step == 'upload':
            file = request.files.get('file')
            if not file or not file.filename.endswith('.csv'):
                error = "Harap upload file CSV yang valid."
                return render_template('hasil_klastering.html', step='upload', error=error)
            try:
                uploaded_df = pd.read_csv(file)
                uploaded_df.columns = [col.strip() for col in uploaded_df.columns]
                # Gunakan fungsi cleaning dan preprocessing
                df_cleaned = preprocess_data(uploaded_df.copy())

                for col in df_cleaned.columns:
                    if df_cleaned[col].dtype == 'object':
                        df_cleaned[col] = df_cleaned[col].astype('category').cat.codes

                # Standarisasi dan load PCA serta model
                scaler = StandardScaler()
                df_scaled = scaler.fit_transform(df_cleaned)

                pca = joblib.load('pca_model.pkl')
                df_pca = pca.transform(df_scaled)

                kmeans = joblib.load('klastering.pkl')
                cluster_labels = kmeans.predict(df_pca)

                output_df = uploaded_df.copy()
                output_df['Cluster'] = cluster_labels
                cluster_counts = output_df['Cluster'].value_counts().sort_index().to_dict()

                # Visualisasi dengan PCA dan menambahkan legenda
                plt.figure(figsize=(8, 6))
                scatter = plt.scatter(df_pca[:, 0], df_pca[:, 1], c=cluster_labels, cmap='Set1')
                plt.xlabel("PCA 1")
                plt.ylabel("PCA 2")
                plt.title("Visualisasi Klaster dengan PCA")

                # Menambahkan legenda
                handles, labels = scatter.legend_elements()
                plt.legend(handles, labels, title="Klaster", loc="best")

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                buf.close()
                plt.close()

                # Rekomendasi untuk setiap klaster berdasarkan analisis
                rekomendasi_klaster = {
                    0: "Klaster ini menunjukkan pencari kerja junior dan tidak berpengalaman. Karena klaster ini didominasi oleh pencari kerja muda, belum menikah, belum mempunyai tanggungan keluarga serta masih rendah dalam aspek kompetensi proffesional maupun softskill. Direkomendasikan untuk mengikuti pelatihan dasar untuk pencari kerja pemula,  pelatihan keterampilan kerja, pelatihan vokasional intensif, serta program pengembangan pribadi untuk membangun kepercayaan diri dan kesiapan kerja awal.",
                    1: "Klaster ini menunjukkan pencari kerja junior namun berpengalaman. Karena klaster ini didominasi oleh pencari kerja yang mempunyai kompetensi tinggi, usia matang, mempunyai banyak sertifikat dan pengalaman kerja.Direkomendasikan untuk pencari kerja yang siap kerja adalah dengan mengikuti pelatihan profesional bersertifikat dan pendampingan uji kompetensi untuk memperkuat posisi dalam pencarian kerja.",
                    2: "Klaster ini menunjukkan peluang kerja senior dan cukup berpengalaman. Karena klaster ini didominasi oleh pencari kerja yang mempunyai kompetensi proffesional yang cukup, mempunyai beberapa pengalaman kerja dan telah menikah atau mempunyai tanggungan keluarga. Direkomendasikan untuk mengikuti pelatihan penguatan soft skill seperti komunikasi, kepemimpinan dan manajemen kerja tim.",
                    3: "Klaster ini menunjukkan pencari kerja senior dan tidak berpengalaman. Karena klaster ini didominasi oleh kelompok pencari kerja yang cenderung lebih tua, mempunyai tanggungan keluarga namun kurang dalam kompetensi profesional. Direkomendasikan untuk mengikuti pelatihan dasar untuk pencari kerja switch career yang mempunyai banyak pengalaman namun perlu re-skilling karena sertifikat atau usia tidak relevan.",
                    4: "Klaster ini menunjukkan pencari kerja junior namun cukup berpengalaman. Karena klaster ini didominasi oleh kelompok pencari kerja yang mempunyai cukup pengalaman kerja dan sertifikat,mempunyai usia yang lebih muda dan belum mempunyai tanggungan keluarga. Direkomendasikan untuk mengikuti pelatihan tambahan bagi pencari kerja yang cukup siap kerja agar dapat meningkatkan skill dalam mendapatkan pekerjaan.",
                    5: "Klaster ini menunjukkan pencari  kerja senior dan berpengalaman. Karena klaster ini didominasi oleh pencari kerja yang berpengalaman, mempunyai banyak kompetensi, namun dari kelompok usia yang lebih tua dan mempunyai tanggungan keluarga. Direkomendasikan untuk pencari kerja yang lebih senior mengikuti program magang industri serta pelatihan lanjutan untuk meningkatkan keterampilan teknis dan soft skill kepemimpinan.",
                }

                # Menghapus insight sebelumnya dan menambahkan rekomendasi
                cluster_insights.clear()
                for cluster_id in range(6):
                    if cluster_id in rekomendasi_klaster:
                        cluster_insights.append(
                            f"\U0001F9ED Rekomendasi untuk Klaster {cluster_id}: {rekomendasi_klaster[cluster_id]}"
                        )

                return render_template(
                    'hasil_klastering.html',
                    step='result',
                    cluster_insights=cluster_insights,
                    image_base64=image_base64,
                    sil_score=sil_score,
                    dbi_score=dbi_score,
                    cluster_counts=cluster_counts,
                    tables=[output_df.to_html(classes='table table-striped', index=False)],
                    uploaded_df=output_df
                )

            except Exception as e:
                error = f"Terjadi kesalahan saat memproses file: {e}"
                return render_template('hasil_klastering.html', step='upload', error=error)

    return render_template('hasil_klastering.html', step='upload', error=error)

if __name__ == '__main__':
    app.run(debug=True)