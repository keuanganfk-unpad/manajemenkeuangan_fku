import pandas as pd
import streamlit as st
import os
import time
import io
import base64

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Dashboard Sistem Informasi RENCANG FK UNPAD",
    page_icon="🏥",
    layout="wide",
)

# ==========================================
# DATABASE USER ID & PASSWORD
# ==========================================
DATABASE_USER = {
    "adminfk": {"password": "admin2026", "nama": "Administrator FK Unpad", "role": "admin"},
    "asep": {"password": "asep123", "nama": "Asep Koswara", "role": "user"},
    "cheppy": {"password": "cheppy123", "nama": "Cheppy Agustiana", "role": "user"},
    "dede": {"password": "dede123", "nama": "Dede Nurdin", "role": "user"},
    "deviyanti": {"password": "devi123", "nama": "Deviyanti", "role": "user"},
    "erwin": {"password": "erwin123", "nama": "Erwin Muftiwijaya", "role": "user"},
    "neneng": {"password": "neneng123", "nama": "Neneng Ratnasari Rosa", "role": "user"},
    "nita": {"password": "nita123", "nama": "Nita Widyastuti", "role": "user"},
    "yopi": {"password": "yopi123", "nama": "Yopi Taufik Limatranendra", "role": "user"},
    "verifikator": {"password": "verif2026", "nama": "Tim Verifikator SPTJB", "role": "verifikator"}
}

# ==========================================
# INISIALISASI SESSION STATE & QUERY PARAMS
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "current_role" not in st.session_state:
    st.session_state.current_role = ""

query_params = st.query_params
if "user" in query_params and not st.session_state.logged_in:
    u_id = query_params["user"]
    if u_id in DATABASE_USER:
        st.session_state.logged_in = True
        st.session_state.current_user = DATABASE_USER[u_id]["nama"]
        st.session_state.current_role = DATABASE_USER[u_id]["role"]

# ==========================================
# HALAMAN LOGIN
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    
    with col_l2:
        st.markdown(
            """
            <div style="text-align: center; padding: 25px; border: 1px solid #d1d5db; border-radius: 12px; background-color: #f9fafb; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <h2>🔐 Login Rencang<br>FK Unpad</h2>
                <p style="color: gray;">Silakan masukkan User ID dan Password Anda</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        with st.form("form_login"):
            input_user_id = st.text_input("User ID", placeholder="Ketik User ID...").strip().lower()
            input_password = st.text_input("Password", type="password", placeholder="Ketik Password...")
            submit_login = st.form_submit_button("🚀 Masuk Aplikasi", use_container_width=True)
            
            if submit_login:
                if input_user_id in DATABASE_USER and DATABASE_USER[input_user_id]["password"] == input_password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = DATABASE_USER[input_user_id]["nama"]
                    st.session_state.current_role = DATABASE_USER[input_user_id]["role"]
                    st.query_params["user"] = input_user_id
                    st.success(f"Login berhasil! Selamat datang, {DATABASE_USER[input_user_id]['nama']}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ User ID atau Password salah! Periksa kembali data Anda.")
    
    st.stop()

# ==========================================
# LINK GOOGLE SHEETS
# ==========================================
URL_ASLI_SPTJB = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSm7LCABdy45Kmaid-V2eab1MA9so7Os7Nt01FeQlIaAcHxNksu6PrfgJQaVQPWWAPNxhvwdrSXoaOq/pub?gid=87462462&single=true&output=csv"
URL_ASLI_VERIFIKATOR = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSm7LCABdy45Kmaid-V2eab1MA9so7Os7Nt01FeQlIaAcHxNksu6PrfgJQaVQPWWAPNxhvwdrSXoaOq/pub?gid=848950239&single=true&output=csv"

def convert_sheets_url(url):
    if not url or "MASUKKAN_" in url:
        return ""
    if "export?format=csv" in url:
        return url
    if "/edit" in url:
        base_url = url.split("/edit")[0]
        if "gid=" in url:
            gid = url.split("gid=")[1].split("&")[0]
            return f"{base_url}/export?format=csv&gid={gid}"
        return f"{base_url}/export?format=csv"
    return url

URL_SPTJB = convert_sheets_url(URL_ASLI_SPTJB)
URL_VERIF = convert_sheets_url(URL_ASLI_VERIFIKATOR)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def make_unique_columns(cols):
    seen = {}
    new_cols = []
    for col in cols:
        col_str = str(col).strip()
        if not col_str or col_str.lower() == 'nan':
            col_str = "Kolom"
        if col_str in seen:
            seen[col_str] += 1
            new_cols.append(f"{col_str}_{seen[col_str]}")
        else:
            seen[col_str] = 0
            new_cols.append(col_str)
    return new_cols

def get_image_base64(file_path):
    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except:
        return "https://upload.wikimedia.org/wikipedia/id/thumb/0/05/Makara_dari_Universitas_Padjadjaran.svg/800px-Makara_dari_Universitas_Padjadjaran.svg.png"

LOGO_SRC = get_image_base64("logo_unpad.png")

# ==========================================
# CSS KHUSUS
# ==========================================
st.markdown(
    f"""
    <style>
    .block-container {{
        padding-top: 1.5rem !important;
    }}
    .header-container {{
        display: flex;
        align-items: center;
        gap: 20px;
        border-bottom: 1.5px solid #d1d5db;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }}
    .header-title {{
        font-size: 2rem;
        color: #2c3e50; 
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }}
    .header-subtitle {{
        font-size: 1rem;
        color: #6b7280;
        margin-top: 2px;
        font-weight: 500;
    }}
    .stTable div {{
        max-height: 500px;
        overflow-y: auto;
    }}
    .stTable table {{
        position: relative;
    }}
    .stTable th {{
        position: sticky !important;
        top: 0 !important;
        background-color: #f1f5f9 !important;
        color: #1e3a8a !important;
        z-index: 999 !important;
        box-shadow: inset 0 -1px 0 #cbd5e1;
    }}
    </style>
    <div class="header-container">
        <img src="{LOGO_SRC}" width="65" style="object-fit: contain;">
        <div>
            <div class="header-title">Sistem Informasi RENCANG</div>
            <div class="header-subtitle">Perencanaan dan Keuangan FK Unpad</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# LOAD DATA
# ==========================================
EXCEL_DOSEN = "DATA DOSEN FK UNPAD_Pak Dede.xlsx"
EXCEL_STAFF = "DATA TENDIK FK UNPAD_Pak Dede.xlsx"

def load_data_dosen():
    if os.path.exists("Backup_Data_Dosen.csv"):
        try:
            df = pd.read_csv("Backup_Data_Dosen.csv", dtype=str)
            if len(df) > 0:
                df.columns = make_unique_columns(df.columns)
                return df.astype(str).fillna("")
        except:
            pass
    try:
        df = pd.read_excel(EXCEL_DOSEN, sheet_name="2026", header=3, dtype=str)
        df = df.dropna(subset=["NAMA"])
        for col in ["NIP", "NIK", "HP"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '')
        df.columns = make_unique_columns(df.columns)
        return df.astype(str).fillna("")
    except:
        return pd.DataFrame()

def load_data_staff():
    if os.path.exists("Backup_Data_Staff.csv"):
        try:
            df = pd.read_csv("Backup_Data_Staff.csv", dtype=str)
            if len(df) > 0:
                df.columns = make_unique_columns(df.columns)
                return df.astype(str).fillna("")
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
        df_staff.columns = make_unique_columns(df_staff.columns)
        return df_staff.astype(str).fillna("")
    except:
        return pd.DataFrame()

def load_data_sptjb():
    if not URL_SPTJB:
        return pd.DataFrame()
    try:
        df = pd.read_csv(URL_SPTJB, header=8, dtype=str)
        df.columns = make_unique_columns(df.columns)
        target_indices = [2, 4, 6, 9, 10, 18, 19, 84, 86, 87]
        valid_indices = [i for i in target_indices if i < len(df.columns)]
        if valid_indices:
            df = df.iloc[:, valid_indices]

        df.columns = make_unique_columns(df.columns)
        df = df.dropna(how='all')
        return df.astype(str).fillna("")
    except Exception as e:
        return pd.DataFrame()

def load_data_verifikator():
    if not URL_VERIF:
        return pd.DataFrame()
    try:
        df_raw = pd.read_csv(URL_VERIF, header=None, dtype=str)
        target_indices_verif = [3, 5, 12, 77, 78]
        valid_indices = [i for i in target_indices_verif if i < len(df_raw.columns)]
        if not valid_indices:
            return pd.DataFrame()
            
        df = df_raw.iloc[9:, valid_indices].copy()
        headers = [str(df_raw.iloc[8, i]).strip() if pd.notna(df_raw.iloc[8, i]) else f"Kolom_{i}" for i in valid_indices]
        df.columns = make_unique_columns(headers)
        df = df.dropna(how='all').reset_index(drop=True)
        df.insert(0, "No.", range(1, len(df) + 1))
        return df.astype(str).fillna("")
    except Exception as e:
        return pd.DataFrame()

def simpan_backup():
    st.session_state.df_dosen.to_csv("Backup_Data_Dosen.csv", index=False)
    st.session_state.df_staff.to_csv("Backup_Data_Staff.csv", index=False)

if "df_dosen" not in st.session_state:
    st.session_state.df_dosen = load_data_dosen()
if "df_staff" not in st.session_state:
    st.session_state.df_staff = load_data_staff()
if "df_sptjb" not in st.session_state:
    st.session_state.df_sptjb = load_data_sptjb()
if "df_verif_sptjb" not in st.session_state:
    st.session_state.df_verif_sptjb = load_data_verifikator()

def clean_val(val):
    if pd.isna(val) or str(val).lower() == 'nan': return ""
    val_str = str(val)
    if val_str.endswith('.0'): val_str = val_str[:-2]
    return val_str

# ==========================================
# SIDEBAR TERKECIL (HANYA LOGOUT & INFO USER)
# ==========================================
with st.sidebar:
    st.success(f"👤 Login: **{st.session_state.current_user}**")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.current_role = ""
        st.query_params.clear()
        st.rerun()

# ==========================================
# PILIHAN MENU KATEGORI & AKSI DALAM SATU HALAMAN
# ==========================================
st.markdown("### 📌 **Panel Navigasi & Modul Kerja**")

col_kat, col_aks = st.columns([1.2, 2.5])

with col_kat:
    if st.session_state.current_role == "verifikator":
        kategori_pilihan = st.selectbox(
            "📂 Pilih Kategori Data:",
            ["✔️ Verifikasi SPTJB"]
        )
    else:
        kategori_pilihan = st.selectbox(
            "📂 Pilih Kategori Data:",
            ["👨‍⚕️ Data Dosen", "👨‍💼 Data Staff", "📄 Nomor SPTJB"]
        )

with col_aks:
    if kategori_pilihan == "📄 Nomor SPTJB" or st.session_state.current_role == "verifikator":
        aksi_pilihan = st.radio(
            "⚡ Pilih Aksi Operasi:",
            ["📋 Lihat & Cari Data"],
            horizontal=True
        )
    else:
        aksi_pilihan = st.radio(
            "⚡ Pilih Aksi Operasi:",
            ["📋 Lihat & Cari Data", "➕ Tambah Data", "✏️ Edit Data", "🗑️ Hapus Data", "📥 Unduh Excel"],
            horizontal=True
        )

# Penentuan dataframe aktif berdasarkan pilihan
if "Dosen" in kategori_pilihan:
    df_aktif = st.session_state.df_dosen
    kategori_nama = "Dosen"
elif "Staff" in kategori_pilihan:
    df_aktif = st.session_state.df_staff
    kategori_nama = "Staff"
elif "Verifikasi" in kategori_pilihan:
    df_aktif = st.session_state.df_verif_sptjb
    kategori_nama = "Verifikasi SPTJB"
else:
    df_aktif = st.session_state.df_sptjb
    kategori_nama = "SPTJB"

st.markdown("---")

# ==========================================
# EKSEKUSI AKSI BERDASARKAN SELEKSI
# ==========================================
if aksi_pilihan == "📋 Lihat & Cari Data":
    st.subheader(f"🔍 Daftar Data: {kategori_nama}")
    st.caption(f"Total Tercatat: {len(df_aktif)} Data")
    
    if len(df_aktif) > 0:
        keyword = st.text_input("Cari data (kata kunci):", placeholder="Ketik kata kunci untuk memfilter...")
        filtered_df = df_aktif.copy()
        if keyword:
            mask = filtered_df.apply(lambda row: row.astype(str).str.contains(keyword, case=False, na=False).any(), axis=1)
            filtered_df = filtered_df[mask]
        
        st.markdown(f"**Menampilkan {len(filtered_df)} data:**")
        st.table(filtered_df.astype(str))
    else:
        st.info("Data belum tersedia atau kosong.")

elif aksi_pilihan == "➕ Tambah Data":
    st.subheader(f"➕ Form Penambahan Data {kategori_nama}")
    
    with st.form("form_tambah_inline"):
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
                tgl_lahir = st.text_input("Tanggal Lahir (YYYY-MM-DD)")
                alamat = st.text_area("Alamat Rumah")
                email = st.text_input("Email")
                hp = st.text_input("Nomor HP")
        elif kategori_nama == "Staff":
            with col1:
                nip = st.text_input("NIP / ID Staff")
                nama = st.text_input("Nama Lengkap*")
                jabatan = st.text_input("Jabatan")
                unit_kerja = st.text_input("Unit Kerja")
            with col2:
                status_pegawai = st.selectbox("Status Pegawai", ["PNS", "Non PNS", "Honorer", "Lainnya"])
                jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-Laki", "Perempuan"])
                hp = st.text_input("Nomor HP")
                email = st.text_input("Email")
                
        submit_button = st.form_submit_button(f"💾 Simpan Data Baru", use_container_width=True)
        if submit_button:
            if not locals().get("nama", ""):
                st.warning("⚠️ Nama Lengkap wajib diisi!")
            else:
                if kategori_nama == "Dosen":
                    new_data = {"No.": len(df_aktif)+1, "NIP": str(nip), "NIK": str(nik), "NAMA": nama, "DEPARTEMEN": departemen, "INSTANSI INDUK": instansi, "STATUS AKTIF/TIDAK AKTIF": status_aktif, "JENIS KELAMIN": jenis_kelamin, "Tempat Lahir": tmp_lahir, "Tanggal Lahir": tgl_lahir, "USIA": "-", "Alamat Rumah": alamat, "Email": email, "HP": str(hp)}
                    st.session_state.df_dosen = pd.concat([st.session_state.df_dosen, pd.DataFrame([new_data])], ignore_index=True)
                    simpan_backup()
                elif kategori_nama == "Staff":
                    new_data = {"No.": len(df_aktif)+1, "NIP": str(nip), "NAMA": nama, "JABATAN": jabatan, "UNIT KERJA": unit_kerja, "STATUS PEGAWAI": status_pegawai, "JENIS KELAMIN": jenis_kelamin, "HP": str(hp), "Email": email}
                    st.session_state.df_staff = pd.concat([st.session_state.df_staff, pd.DataFrame([new_data])], ignore_index=True)
                    simpan_backup()
                
                st.success(f"🎉 Data {kategori_nama} berhasil ditambahkan!")
                time.sleep(1)
                st.rerun()

elif aksi_pilihan == "✏️ Edit Data":
    st.subheader(f"✏️ Perbarui Data {kategori_nama}")
    if len(df_aktif) == 0:
        st.info(f"Belum ada data {kategori_nama} untuk diedit.")
    else:
        identitas_kolom = "NAMA" if "NAMA" in df_aktif.columns else df_aktif.columns[1]
        pilihan = df_aktif[identitas_kolom].dropna().tolist() if identitas_kolom in df_aktif.columns else []
        
        if not pilihan:
            st.warning("Kolom identitas tidak ditemukan pada data.")
        else:
            to_edit = st.selectbox(f"Pilih nama data {kategori_nama}:", pilihan)
            old_data = df_aktif[df_aktif[identitas_kolom] == to_edit].iloc[0]
            idx = df_aktif[df_aktif[identitas_kolom] == to_edit].index[0]
            
            with st.form("form_edit_inline"):
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

                submit_edit = st.form_submit_button("🔄 Perbarui Data", use_container_width=True)
                if submit_edit:
                    if not locals().get("nama", ""):
                        st.warning("⚠️ Nama Lengkap wajib diisi!")
                    else:
                        if kategori_nama == "Dosen":
                            st.session_state.df_dosen.at[idx, "NIP"], st.session_state.df_dosen.at[idx, "NAMA"] = str(nip), nama
                            st.session_state.df_dosen.at[idx, "DEPARTEMEN"], st.session_state.df_dosen.at[idx, "Email"], st.session_state.df_dosen.at[idx, "HP"] = departemen, email, str(hp)
                            simpan_backup()
                        elif kategori_nama == "Staff":
                            st.session_state.df_staff.at[idx, "NIP"], st.session_state.df_staff.at[idx, "NAMA"] = str(nip), nama
                            st.session_state.df_staff.at[idx, "JABATAN"], st.session_state.df_staff.at[idx, "UNIT KERJA"] = jabatan, unit_kerja
                            st.session_state.df_staff.at[idx, "STATUS PEGAWAI"], st.session_state.df_staff.at[idx, "JENIS KELAMIN"], st.session_state.df_staff.at[idx, "HP"], st.session_state.df_staff.at[idx, "Email"] = status_pegawai, jenis_kelamin, str(hp), email
                            simpan_backup()
                        
                        st.success(f"✅ Data {kategori_nama} berhasil diperbarui!")
                        time.sleep(1)
                        st.rerun()

elif aksi_pilihan == "🗑️ Hapus Data":
    st.subheader(f"🗑️ Hapus Data {kategori_nama}")
    if len(df_aktif) == 0:
        st.info(f"Tidak ada data {kategori_nama} untuk dihapus.")
    else:
        identitas_kolom = "NAMA" if "NAMA" in df_aktif.columns else df_aktif.columns[1]
        pilihan = df_aktif[identitas_kolom].dropna().tolist() if identitas_kolom in df_aktif.columns else []
        
        if not pilihan:
            st.warning("Kolom identitas tidak ditemukan pada data.")
        else:
            to_delete = st.selectbox(f"Pilih nama data {kategori_nama} yang ingin dihapus:", pilihan)

            if st.button("🗑️ Konfirmasi Hapus Data", type="primary"):
                if kategori_nama == "Dosen":
                    st.session_state.df_dosen = st.session_state.df_dosen[st.session_state.df_dosen["NAMA"] != to_delete].reset_index(drop=True)
                    simpan_backup()
                elif kategori_nama == "Staff":
                    st.session_state.df_staff = st.session_state.df_staff[st.session_state.df_staff["NAMA"] != to_delete].reset_index(drop=True)
                    simpan_backup()
                
                st.success(f"✅ Data {kategori_nama} **{to_delete}** berhasil dihapus!")
                time.sleep(1)
                st.rerun()

elif aksi_pilihan == "📥 Unduh Excel":
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
