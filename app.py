import pandas as pd
import streamlit as st
import os
import time
import io
import base64
import re
st.markdown(
    """
    <style>
    /* Sembunyikan tombol Manage App */
    button[kind="header"] {
        display: none !important;
    }
    .manage-app-button {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Sistem Manajemen Data Terintegrasi FK UNPAD",
    page_icon="🏥",
    layout="wide",
)

# ==========================================
# FUNGSI MEMBACA GAMBAR LOKAL (ANTI GAGAL)
# ==========================================
def get_image_base64(file_path):
    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except:
        return "https://upload.wikimedia.org/wikipedia/id/thumb/0/05/Makara_dari_Universitas_Padjadjaran.svg/800px-Makara_dari_Universitas_Padjadjaran.svg.png"

LOGO_SRC = get_image_base64("logo_unpad.png")

# ==========================================
# CSS KHUSUS (STICKY HEADER & DESAIN JUDUL)
# ==========================================
st.markdown(
    f"""
    <style>
    div[data-testid="stVerticalBlock"] > div:first-of-type {{
        position: sticky;
        top: 2.875rem; 
        z-index: 999;
        background-color: var(--background-color);
        padding-top: 10px;
        padding-bottom: 10px;
    }}
    .header-container {{
        display: flex;
        align-items: center;
        gap: 20px;
        border-bottom: 1.5px solid #d1d5db;
        padding-bottom: 15px;
        margin-bottom: 15px;
    }}
    .header-title {{
        font-size: 2.1rem;
        color: #2c3e50; 
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }}
    .block-container {{
        padding-top: 2rem !important;
    }}
    </style>
    <div class="header-container">
        <img src="{LOGO_SRC}" width="70" style="object-fit: contain;">
        <div class="header-title">Sistem Manajemen Data Terintegrasi FK UNPAD</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Konstanta Nama File Excel
EXCEL_DOSEN = "DATA DOSEN FK UNPAD_Pak Dede.xlsx"
EXCEL_STAFF = "DATA TENDIK FK UNPAD_Pak Dede.xlsx"

# Daftar Pilihan List Box untuk Prodi / Unit FK UNPAD
LIST_PRODI_UNIT = [
    "Pilih Prodi / Unit...",
    "Program Studi Sarjana Kedokteran",
    "Program Studi Profesi Dokter",
    "Program Studi PPDH (Dokter Hewan)",
    "Program Studi Magister (S2) Ilmu Kedokteran Dasar",
    "Program Studi Magister (S2) Kebidanan",
    "Program Studi Doktor (S3) Ilmu Kedokteran",
    "Departemen Anatomi",
    "Departemen Fisiologi",
    "Departemen Biokimia",
    "Departemen Farmakologi",
    "Departemen Patologi Anatomi",
    "Departemen Mikrobiologi",
    "Departemen Parasitologi",
    "Departemen Ilmu Penyakit Dalam",
    "Departemen Ilmu Bedah",
    "Departemen Ilmu Kesehatan Anak",
    "Departemen Obgin",
    "Departemen Neurologi",
    "Departemen Psikiatri",
    "Departemen Kardiologi",
    "Departemen Pulmonologi",
    "Departemen THT-KL",
    "Departemen Mata",
    "Departemen Kulit & Kelamin",
    "Departemen Anestesiologi",
    "Departemen Radiologi",
    "Departemen Ilmu Bedah Saraf",
    "Departemen Orthopaedi & Traumatologi",
    "Bagian Akademik & Kemahasiswaan",
    "Bagian Keuangan & Kepegawaian (SDM)",
    "Bagian Umum & Perlengkapan",
    "Dekanat / Pimpinan Fakultas"
]

# Daftar Pilihan List Box untuk User
LIST_USER = [
    "Pilih User / Pengaju...",
    "Asep Koswara",
    "Cheppy Agustiana",
    "Dede Nurdin",
    "Deviyanti",
    "Erwin Muftiwijaya",
    "Neneng Ratnasari Rosa",
    "Nita Widyastuti",
    "Yopi Taufik Limatranendra"
]

# ==========================================
# FUNGSI MEMUAT & MENYIMPAN DATA
# ==========================================
def load_data_dosen():
    if os.path.exists("Backup_Data_Dosen.csv"):
        try:
            df = pd.read_csv("Backup_Data_Dosen.csv", dtype=str)
            if len(df) > 0: return df.fillna("")
        except:
            pass
    try:
        df = pd.read_excel(EXCEL_DOSEN, sheet_name="2026", header=3, dtype=str)
        df = df.dropna(subset=["NAMA"])
        for col in ["NIP", "NIK", "HP"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '')
        return df.fillna("")
    except:
        return pd.DataFrame()

def load_data_staff():
    if os.path.exists("Backup_Data_Staff.csv"):
        try:
            df = pd.read_csv("Backup_Data_Staff.csv", dtype=str)
            if len(df) > 0: return df.fillna("")
        except:
            pass
    try:
        df_tendik = pd.read_excel(EXCEL_STAFF, sheet_name="2026", header=2, dtype=str)
        df_tendik = df_tendik.dropna(subset=["NAMA"])
        if "NIP" in df_tendik.columns:
            df_tendik["NIP"] = df_tendik["NIP"].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '')
            
        df_staff = pd.DataFrame()
        df_staff["No."] = range(1, len(df_tendik) + 1)
        df_staff["NIP"] = df_tendik["NIP"]
        df_staff["NAMA"] = df_tendik["NAMA"]
        df_staff["JABATAN"] = df_tendik.get("JABATAN FUNGSIONAL", "")
        df_staff["UNIT KERJA"] = "" 
        df_staff["STATUS PEGAWAI"] = df_tendik.get("STATUS", "")
        df_staff["JENIS KELAMIN"] = df_tendik.get("JENIS KELAMIN", "")
        df_staff["HP"] = df_tendik.get("HP", "")
        df_staff["Email"] = df_tendik.get("Email", "")
        return df_staff.fillna("")
    except:
        return pd.DataFrame(columns=["No.", "NIP", "NAMA", "JABATAN", "UNIT KERJA", "STATUS PEGAWAI", "JENIS KELAMIN", "HP", "Email"])

def load_data_sptjb():
    if os.path.exists("Backup_Data_SPTJB.csv"):
        try:
            df = pd.read_csv("Backup_Data_SPTJB.csv", dtype=str)
            if len(df) > 0: return df.fillna("")
        except:
            pass

    file_target = None
    if os.path.exists("INPUT SPTJB.xlsx"):
        file_target = "INPUT SPTJB.xlsx"
    elif os.path.exists("SPTJB 2026 VER.1.xlsx"):
        file_target = "SPTJB 2026 VER.1.xlsx"

    df_empty = pd.DataFrame(columns=["Tanggal", "No. SPTJB / SPTJM", "Perihal / Kegiatan", "Prodi / Unit", "Akun / Output", "Nominal (Rp)", "User (Nama)", "No. Invoice", "Link Dokumen"])

    if not file_target:
        return df_empty

    try:
        df_raw = pd.read_excel(file_target, sheet_name=0, header=None, dtype=str)
        idx_header = 0
        for i, row in df_raw.iterrows():
            row_str = " ".join(row.fillna("").astype(str)).upper()
            if "SPTJB" in row_str or "SPTJM" in row_str:
                idx_header = i
                break
                
        df_raw.columns = df_raw.iloc[idx_header].fillna("").astype(str).str.upper().str.strip()
        df_data = df_raw.iloc[idx_header+1:].reset_index(drop=True)
        
        def get_col(keywords):
            for col in df_data.columns:
                for kw in keywords:
                    if kw in col:
                        return col
            return None
            
        col_tgl = get_col(["TANGGAL"])
        col_sptjb = get_col(["SPTJB", "SPTJM"])
        col_perihal = get_col(["PERIHAL", "KEGIATAN"])
        col_prodi = get_col(["PRODI", "UNIT"])
        col_akun = get_col(["AKUN", "OUTPUT"])
        col_nominal = get_col(["ANGGARAN", "NOMINAL", "REALISASI"])
        col_user = get_col(["USER", "NAMA USER", "MENGAJUKAN"])
        col_invoice = get_col(["INVOICE", "FAKTUR"])
        col_link = get_col(["LINK", "DOKUMEN", "UPLOAD"])
        
        df_sptjb = pd.DataFrame()
        df_sptjb["Tanggal"] = df_data[col_tgl] if col_tgl else ""
        df_sptjb["No. SPTJB / SPTJM"] = df_data[col_sptjb] if col_sptjb else ""
        df_sptjb["Perihal / Kegiatan"] = df_data[col_perihal] if col_perihal else ""
        df_sptjb["Prodi / Unit"] = df_data[col_prodi] if col_prodi else ""
        df_sptjb["Akun / Output"] = df_data[col_akun] if col_akun else ""
        df_sptjb["Nominal (Rp)"] = df_data[col_nominal] if col_nominal else ""
        df_sptjb["User (Nama)"] = df_data[col_user] if col_user else ""
        df_sptjb["No. Invoice"] = df_data[col_invoice] if col_invoice else ""
        df_sptjb["Link Dokumen"] = df_data[col_link] if col_link else ""

        df_sptjb = df_sptjb.dropna(subset=["No. SPTJB / SPTJM"])
        df_sptjb = df_sptjb[df_sptjb["No. SPTJB / SPTJM"].astype(str).str.strip() != ""]
        df_sptjb = df_sptjb[df_sptjb["No. SPTJB / SPTJM"].astype(str).str.upper().str.strip() != "NO. SPTJB / SPTJM"]
        
        def clean_date_format(val):
            val_str = str(val).strip()
            if not val_str or val_str.lower() == 'nan':
                return ""
            if ' ' in val_str:
                val_str = val_str.split(' ')[0]
            parsed_date = pd.to_datetime(val_str, errors='coerce')
            if pd.notna(parsed_date):
                return parsed_date.strftime('%Y-%m-%d')
            return val_str

        df_sptjb["Tanggal"] = df_sptjb["Tanggal"].apply(clean_date_format)

        if not df_sptjb["Nominal (Rp)"].empty:
            df_sptjb["Nominal (Rp)"] = df_sptjb["Nominal (Rp)"].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '')

        df_sptjb = df_sptjb.fillna("").reset_index(drop=True)
        
        if len(df_sptjb) > 0:
            df_sptjb.to_csv("Backup_Data_SPTJB.csv", index=False)
            
        return df_sptjb
    except:
        return df_empty

def simpan_backup():
    st.session_state.df_dosen.to_csv("Backup_Data_Dosen.csv", index=False)
    st.session_state.df_staff.to_csv("Backup_Data_Staff.csv", index=False)
    st.session_state.df_sptjb.to_csv("Backup_Data_SPTJB.csv", index=False)

# Fungsi untuk menghasilkan nomor SPTJB otomatis berikutnya
def generate_next_sptjb_number(df):
    if df is None or len(df) == 0:
        return "1210/UN6.C/PK/KU/2026"
    
    # Ambil nilai nomor SPTJB terakhir dari baris terakhir dataframe
    last_val = str(df["No. SPTJB / SPTJM"].iloc[-1]).strip()
    
    # Cari angka di bagian depan string menggunakan regex
    match = re.match(r'^(\d+)(.*)$', last_val)
    if match:
        num_part = int(match.group(1))
        suffix_part = match.group(2) # misal "/UN6.C/PK/KU/2026"
        next_num = num_part + 1
        return f"{next_num}{suffix_part}"
    
    return "1210/UN6.C/PK/KU/2026"

# Inisialisasi Data
if "df_dosen" not in st.session_state:
    st.session_state.df_dosen = load_data_dosen()
if "df_staff" not in st.session_state:
    st.session_state.df_staff = load_data_staff()
if "df_sptjb" not in st.session_state:
    st.session_state.df_sptjb = load_data_sptjb()

# ==========================================
# SIDEBAR & NAVIGASI
# ==========================================
kategori_data = st.sidebar.radio(
    "👥 Pilih Kategori Data:",
    ["👨‍⚕️ Data Dosen", "👨‍💼 Data Staff", "📄 Nomor SPTJB"]
)

st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Pilih Menu Navigasi",
    ["📋 Lihat & Cari Data", "➕ Tambah Data Baru", "✏️ Edit Data", "🗑️ Hapus Data", "📥 Unduh / Simpan ke Excel"],
)
st.sidebar.markdown("---")
st.sidebar.info(f"Anda sedang berada di mode **{kategori_data}**")

if kategori_data == "👨‍⚕️ Data Dosen":
    df_aktif = st.session_state.df_dosen
    kategori_nama = "Dosen"
elif kategori_data == "👨‍💼 Data Staff":
    df_aktif = st.session_state.df_staff
    kategori_nama = "Staff"
else:
    if len(st.session_state.df_sptjb) == 0:
        st.session_state.df_sptjb = load_data_sptjb()
    df_aktif = st.session_state.df_sptjb
    kategori_nama = "SPTJB"

def clean_val(val):
    if pd.isna(val) or str(val).lower() == 'nan': return ""
    val_str = str(val)
    if val_str.endswith('.0'): val_str = val_str[:-2]
    return val_str

# ==========================================
# MENU 1: LIHAT & CARI DATA
# ==========================================
if menu == "📋 Lihat & Cari Data":
    st.subheader(f"🔍 Pencarian & Filter Data {kategori_nama}")
    
    if kategori_nama == "SPTJB" and len(df_aktif) == 0:
        if not os.path.exists("INPUT SPTJB.xlsx") and not os.path.exists("SPTJB 2026 VER.1.xlsx"):
            st.error("❌ GAGAL MEMUAT DATA: File Excel tidak ditemukan!")

    st.metric(f"Total Data {kategori_nama} Tercatat", len(df_aktif))
    st.markdown("---")

    if kategori_nama == "SPTJB":
        keyword = st.text_input("Cari SPTJB (berdasarkan Nomor, Perihal, Nama, atau Prodi):", placeholder="Ketik di sini...")
        filtered_df = df_aktif.copy()
        if keyword:
            filtered_df = filtered_df[
                filtered_df["No. SPTJB / SPTJM"].astype(str).str.contains(keyword, case=False, na=False) |
                filtered_df["Perihal / Kegiatan"].astype(str).str.contains(keyword, case=False, na=False) |
                filtered_df["Prodi / Unit"].astype(str).str.contains(keyword, case=False, na=False) |
                filtered_df["User (Nama)"].astype(str).str.contains(keyword, case=False, na=False)
            ]
        
        st.markdown(f"**Menampilkan {len(filtered_df)} data:**")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=500,
            hide_index=True,
            column_config={
                "Link Dokumen": st.column_config.LinkColumn(
                    "Link Dokumen",
                    help="Klik untuk membuka tautan dokumen",
                    display_text="🔗 Buka Dokumen"
                )
            }
        )
    else:
        keyword = st.text_input(f"Cari {kategori_nama} (berdasarkan Nama atau NIP):", placeholder="Ketik di sini...")
        filtered_df = df_aktif.copy()
        if keyword:
            filtered_df = filtered_df[
                filtered_df["NAMA"].astype(str).str.contains(keyword, case=False, na=False) |
                filtered_df["NIP"].astype(str).str.contains(keyword, case=False, na=False)
            ]

        st.markdown(f"**Menampilkan {len(filtered_df)} data:**")
        st.dataframe(filtered_df, use_container_width=True, height=500, hide_index=True)

# ==========================================
# MENU 2: TAMBAH DATA
# ==========================================
elif menu == "➕ Tambah Data Baru":
    st.subheader(f"➕ Form Penambahan Data {kategori_nama}")
    
    # Hitung nomor otomatis jika kategori SPTJB
    auto_sptjb_num = generate_next_sptjb_number(st.session_state.df_sptjb) if kategori_nama == "SPTJB" else ""

    with st.form("form_tambah"):
        col1, col2 = st.columns(2)
        if kategori_nama == "Dosen":
            with col1:
                nip = st.text_input("NIP")
                nik = st.text_input("NIK")
                nama = st.text_input("Nama Lengkap & Gelar*")
                departemen = st.text_input("Departemen")
                instansi = st.selectbox("Instansi Induk", ["Kemenkes", "Kemendiktisainstek", "Lainnya"])
                status_aktif = st.selectbox("Status Keaktifan", ["Aktif", "Tidak Aktif", "Tugas Belajar"])
            with col2:
                jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-Laki", "Perempuan"])
                tmp_lahir = st.text_input("Tempat Lahir")
                tgl_lahir = st.text_input("Tanggal Lahir (Format: YYYY-MM-DD)")
                alamat = st.text_area("Alamat Rumah")
                email = st.text_input("Email")
                hp = st.text_input("Nomor HP")
        elif kategori_nama == "Staff":
            with col1:
                nip = st.text_input("NIP / NIK / ID Staff")
                nama = st.text_input("Nama Lengkap*")
                jabatan = st.text_input("Jabatan (Contoh: Admin, Teknisi, dll)")
                unit_kerja = st.text_input("Unit Kerja / Bagian")
            with col2:
                status_pegawai = st.selectbox("Status Pegawai", ["PNS", "Non PNS", "Honorer", "Lainnya"])
                jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-Laki", "Perempuan"])
                hp = st.text_input("Nomor HP")
                email = st.text_input("Email")
        elif kategori_nama == "SPTJB":
            with col1:
                tanggal = st.date_input("Tanggal")
                # Nomor SPTJB otomatis (disabled agar tidak bisa diubah sembarangan, tapi tetap tampil jelas)
                no_sptjb = st.text_input("No. SPTJB / SPTJM (Otomatis)", value=auto_sptjb_num, disabled=True)
                perihal = st.text_area("Perihal / Kegiatan")
                prodi = st.selectbox("Prodi / Unit", LIST_PRODI_UNIT)
            with col2:
                akun = st.text_input("Akun / Output")
                nominal = st.text_input("Nominal (Rp)")
                nama_user = st.selectbox("User (Nama Yang Mengajukan)", LIST_USER)
                invoice = st.text_input("No. Invoice")
                link_dokumen = st.text_input("Link Dokumen (URL / Link web)")
                
        submit_button = st.form_submit_button(f"💾 Simpan Data {kategori_nama}", use_container_width=True)
        if submit_button:
            if kategori_nama in ["Dosen", "Staff"] and not nama:
                st.warning("⚠️ Nama Lengkap wajib diisi!")
            elif kategori_nama == "SPTJB" and prodi == LIST_PRODI_UNIT[0]:
                st.warning("⚠️ Silakan pilih Prodi / Unit terlebih dahulu!")
            elif kategori_nama == "SPTJB" and nama_user == LIST_USER[0]:
                st.warning("⚠️ Silakan pilih User / Nama Pengaju terlebih dahulu!")
            else:
                if kategori_nama == "Dosen":
                    new_data = {"No.": len(df_aktif)+1, "NIP": str(nip), "NIK": str(nik), "NAMA": nama, "DEPARTEMEN": departemen, "INSTANSI INDUK": instansi, "STATUS AKTIF/TIDAK AKTIF": status_aktif, "JENIS KELAMIN": jenis_kelamin, "Tempat Lahir": tmp_lahir, "Tanggal Lahir": tgl_lahir, "USIA": "-", "Alamat Rumah": alamat, "Email": email, "HP": str(hp)}
                    st.session_state.df_dosen = pd.concat([st.session_state.df_dosen, pd.DataFrame([new_data])], ignore_index=True)
                elif kategori_nama == "Staff":
                    new_data = {"No.": len(df_aktif)+1, "NIP": str(nip), "NAMA": nama, "JABATAN": jabatan, "UNIT KERJA": unit_kerja, "STATUS PEGAWAI": status_pegawai, "JENIS KELAMIN": jenis_kelamin, "HP": str(hp), "Email": email}
                    st.session_state.df_staff = pd.concat([st.session_state.df_staff, pd.DataFrame([new_data])], ignore_index=True)
                elif kategori_nama == "SPTJB":
                    new_data = {"Tanggal": str(tanggal), "No. SPTJB / SPTJM": auto_sptjb_num, "Perihal / Kegiatan": perihal, "Prodi / Unit": prodi, "Akun / Output": akun, "Nominal (Rp)": nominal, "User (Nama)": nama_user, "No. Invoice": invoice, "Link Dokumen": link_dokumen}
                    st.session_state.df_sptjb = pd.concat([st.session_state.df_sptjb, pd.DataFrame([new_data])], ignore_index=True)
                simpan_backup()
                msg = auto_sptjb_num if kategori_nama == "SPTJB" else nama
                st.success(f"🎉 Data {kategori_nama} dengan nomor **{msg}** berhasil ditambahkan dan tersimpan!")
                time.sleep(1.5)
                st.rerun()
                
# ==========================================
# MENU 3: EDIT DATA
# ==========================================
elif menu == "✏️ Edit Data":
    st.subheader(f"✏️ Edit Data {kategori_nama}")
    if len(df_aktif) == 0:
        st.info(f"Belum ada data {kategori_nama} untuk diedit.")
    else:
        if kategori_nama == "SPTJB":
            pilihan = df_aktif["No. SPTJB / SPTJM"].dropna().tolist()
            to_edit = st.selectbox("Pilih Nomor SPTJB yang ingin diedit:", pilihan)
            old_data = df_aktif[df_aktif["No. SPTJB / SPTJM"] == to_edit].iloc[0]
            idx = df_aktif[df_aktif["No. SPTJB / SPTJM"] == to_edit].index[0]
        else:
            pilihan = df_aktif["NAMA"].dropna().tolist()
            to_edit = st.selectbox(f"Pilih Nama {kategori_nama} yang ingin diedit:", pilihan)
            old_data = df_aktif[df_aktif["NAMA"] == to_edit].iloc[0]
            idx = df_aktif[df_aktif["NAMA"] == to_edit].index[0]
        
        with st.form("form_edit"):
            col1, col2 = st.columns(2)
            if kategori_nama == "Dosen":
                with col1:
                    nip = st.text_input("NIP", value=clean_val(old_data.get("NIP")))
                    nama = st.text_input("Nama Lengkap*", value=clean_val(old_data.get("NAMA")))
                    departemen = st.text_input("Departemen", value=clean_val(old_data.get("DEPARTEMEN")))
                with col2:
                    email = st.text_input("Email", value=clean_val(old_data.get("Email")))
                    hp = st.text_input("Nomor HP", value=clean_val(old_data.get("HP")))
            elif kategori_nama == "Staff":
                with col1:
                    nip = st.text_input("NIP / ID Staff", value=clean_val(old_data.get("NIP")))
                    nama = st.text_input("Nama Lengkap*", value=clean_val(old_data.get("NAMA")))
                    jabatan = st.text_input("Jabatan", value=clean_val(old_data.get("JABATAN")))
                    unit_kerja = st.text_input("Unit Kerja", value=clean_val(old_data.get("UNIT KERJA")))
                with col2:
                    status_opts = ["PNS", "Non PNS", "Honorer", "Lainnya"]
                    curr_status = clean_val(old_data.get("STATUS PEGAWAI"))
                    idx_status = status_opts.index(curr_status) if curr_status in status_opts else 0
                    status_pegawai = st.selectbox("Status Pegawai", status_opts, index=idx_status)
                    jk_opts = ["Laki-Laki", "Perempuan"]
                    curr_jk = clean_val(old_data.get("JENIS KELAMIN"))
                    idx_jk = jk_opts.index(curr_jk) if curr_jk in jk_opts else 0
                    jenis_kelamin = st.selectbox("Jenis Kelamin", jk_opts, index=idx_jk)
                    hp = st.text_input("Nomor HP", value=clean_val(old_data.get("HP")))
                    email = st.text_input("Email", value=clean_val(old_data.get("Email")))
            elif kategori_nama == "SPTJB":
                with col1:
                    tanggal = st.text_input("Tanggal (YYYY-MM-DD)", value=clean_val(old_data.get("Tanggal")))
                    no_sptjb_edit = st.text_input("No. SPTJB / SPTJM", value=clean_val(old_data.get("No. SPTJB / SPTJM")))
                    perihal = st.text_area("Perihal / Kegiatan", value=clean_val(old_data.get("Perihal / Kegiatan")))
                    
                    curr_prodi = clean_val(old_data.get("Prodi / Unit"))
                    idx_prodi = LIST_PRODI_UNIT.index(curr_prodi) if curr_prodi in LIST_PRODI_UNIT else 0
                    prodi = st.selectbox("Prodi / Unit", LIST_PRODI_UNIT, index=idx_prodi)
                with col2:
                    akun = st.text_input("Akun / Output", value=clean_val(old_data.get("Akun / Output")))
                    nominal = st.text_input("Nominal (Rp)", value=clean_val(old_data.get("Nominal (Rp)")))
                    
                    curr_user = clean_val(old_data.get("User (Nama)"))
                    idx_user = LIST_USER.index(curr_user) if curr_user in LIST_USER else 0
                    nama_user = st.selectbox("User (Nama Yang Mengajukan)", LIST_USER, index=idx_user)
                    
                    invoice = st.text_input("No. Invoice", value=clean_val(old_data.get("No. Invoice")))
                    link_dokumen = st.text_input("Link Dokumen", value=clean_val(old_data.get("Link Dokumen")))

            submit_edit = st.form_submit_button("🔄 Perbarui Data", use_container_width=True)
            if submit_edit:
                if kategori_nama in ["Dosen", "Staff"] and not nama:
                    st.warning("⚠️ Nama Lengkap wajib diisi!")
                else:
                    if kategori_nama == "Dosen":
                        st.session_state.df_dosen.at[idx, "NIP"], st.session_state.df_dosen.at[idx, "NAMA"] = str(nip), nama
                        st.session_state.df_dosen.at[idx, "DEPARTEMEN"], st.session_state.df_dosen.at[idx, "Email"], st.session_state.df_dosen.at[idx, "HP"] = departemen, email, str(hp)
                    elif kategori_nama == "Staff":
                        st.session_state.df_staff.at[idx, "NIP"], st.session_state.df_staff.at[idx, "NAMA"] = str(nip), nama
                        st.session_state.df_staff.at[idx, "JABATAN"], st.session_state.df_staff.at[idx, "UNIT KERJA"] = jabatan, unit_kerja
                        st.session_state.df_staff.at[idx, "STATUS PEGAWAI"], st.session_state.df_staff.at[idx, "JENIS KELAMIN"], st.session_state.df_staff.at[idx, "HP"], st.session_state.df_staff.at[idx, "Email"] = status_pegawai, jenis_kelamin, str(hp), email
                    elif kategori_nama == "SPTJB":
                        st.session_state.df_sptjb.at[idx, "Tanggal"] = str(tanggal)
                        st.session_state.df_sptjb.at[idx, "No. SPTJB / SPTJM"], st.session_state.df_sptjb.at[idx, "Perihal / Kegiatan"] = no_sptjb_edit, perihal
                        st.session_state.df_sptjb.at[idx, "Prodi / Unit"], st.session_state.df_sptjb.at[idx, "Akun / Output"] = prodi, akun
                        st.session_state.df_sptjb.at[idx, "Nominal (Rp)"] = nominal
                        st.session_state.df_sptjb.at[idx, "User (Nama)"], st.session_state.df_sptjb.at[idx, "No. Invoice"], st.session_state.df_sptjb.at[idx, "Link Dokumen"] = nama_user, invoice, link_dokumen
                    simpan_backup()
                    msg = no_sptjb_edit if kategori_nama == "SPTJB" else nama
                    st.success(f"✅ Data {kategori_nama} **{msg}** berhasil diperbarui!")
                    time.sleep(1.5)
                    st.rerun()

# ==========================================
# MENU 4: HAPUS DATA
# ==========================================
elif menu == "🗑️ Hapus Data":
    st.subheader(f"🗑️ Penghapusan Data {kategori_nama}")
    if len(df_aktif) == 0:
        st.info(f"Tidak ada data {kategori_nama} untuk dihapus.")
    else:
        if kategori_nama == "SPTJB":
            pilihan = df_aktif["No. SPTJB / SPTJM"].dropna().tolist()
            to_delete = st.selectbox("Pilih Nomor SPTJB yang ingin dihapus:", pilihan)
        else:
            pilihan = df_aktif["NAMA"].dropna().tolist()
            to_delete = st.selectbox(f"Pilih Nama {kategori_nama} yang akan dihapus:", pilihan)

        if st.button("🗑️ Hapus Data", type="primary"):
            if kategori_nama == "Dosen":
                st.session_state.df_dosen = st.session_state.df_dosen[st.session_state.df_dosen["NAMA"] != to_delete].reset_index(drop=True)
            elif kategori_nama == "Staff":
                st.session_state.df_staff = st.session_state.df_staff[st.session_state.df_staff["NAMA"] != to_delete].reset_index(drop=True)
            elif kategori_nama == "SPTJB":
                st.session_state.df_sptjb = st.session_state.df_sptjb[st.session_state.df_sptjb["No. SPTJB / SPTJM"] != to_delete].reset_index(drop=True)
            simpan_backup()
            st.success(f"✅ Data {kategori_nama} **{to_delete}** berhasil dihapus!")
            time.sleep(1.5)
            st.rerun()

# ==========================================
# MENU 5: UNDUH / SIMPAN KE EXCEL
# ==========================================
elif menu == "📥 Unduh / Simpan ke Excel":
    st.subheader(f"📥 Unduh Excel: Data {kategori_nama}")
    if len(df_aktif) == 0:
        st.warning(f"Data {kategori_nama} masih kosong.")
    else:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_aktif.to_excel(writer, index=False, sheet_name=f'Data_{kategori_nama}')
        st.download_button(
            label=f"💾 Download File Excel Data {kategori_nama} Sekarang",
            data=buffer.getvalue(),
            file_name=f"Data_{kategori_nama}_Terbaru.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
