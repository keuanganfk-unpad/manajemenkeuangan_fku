import pandas as pd
import streamlit as st
import os
import time
import io
import base64
import re

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
# INISIALISASI SESSION STATE & URL QUERY (ANTI LOGOUT SAAT REFRESH)
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
# HALAMAN LOGIN (USER ID & PASSWORD)
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
# LINK GOOGLE SHEETS TERPISAH
# ==========================================
URL_ASLI_SPTJB = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSm7LCABdy45Kmaid-V2eab1MA9so7Os7Nt01FeQlIaAcHxNksu6PrfgJQaVQPWWAPNxhvwdrSXoaOq/pub?gid=87462462&single=true&output=csv"
URL_ASLI_VERIFIKATOR = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSm7LCABdy45Kmaid-V2eab1MA9so7Os7Nt01FeQlIaAcHxNksu6PrfgJQaVQPWWAPNxhvwdrSXoaOq/pub?gid=848950239&single=true&output=csv"
URL_ASLI_KLINIK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTrAOfYGQUPB9ntgIfSOjPv4dGAea5ZCCsJXqSqwITRLWJ1NNvk9LvUcX58gOKTXA/pub?gid=772898747&single=true&output=csv"
URL_ASLI_TOR_MHS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQrAM-wUQzQPuYlrO0IRhrCy8JsE-ijQ16XE2ZMnlKGjuOdQ2rlK9hNgtf1dYp8Li9CjXJq7WGfI49I/pub?gid=291854399&single=true&output=csv"

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
URL_KLINIK = convert_sheets_url(URL_ASLI_KLINIK)
URL_TOR_MHS = convert_sheets_url(URL_ASLI_TOR_MHS)

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
# CSS KHUSUS
# ==========================================
st.markdown(
    f"""
    <style>
    .block-container {{
        padding-top: 2.5rem !important;
    }}
    .header-container {{
        display: flex;
        align-items: center;
        gap: 20px;
        border-bottom: 1.5px solid #d1d5db;
        padding-bottom: 15px;
        margin-bottom: 20px;
        margin-top: 10px;
    }}
    .header-text {{
        display: flex;
        flex-direction: column;
    }}
    .header-title {{
        font-size: 2.1rem;
        color: #2c3e50; 
        font-weight: 700;
        margin: 0;
        line-height: 1.3;
    }}
    .header-subtitle {{
        font-size: 1.1rem;
        color: #6b7280;
        margin-top: 4px;
        font-weight: 500;
    }}
    .sticky-wrapper {{
        position: sticky;
        top: 0rem;
        z-index: 998;
        background-color: var(--background-color);
        padding-top: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }}
    </style>
    <div class="header-container">
        <img src="{LOGO_SRC}" width="70" style="object-fit: contain;">
        <div class="header-text">
            <div class="header-title">Sistem Informasi RENCANG</div>
            <div class="header-subtitle">Perencanaan dan Keuangan FK Unpad</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

EXCEL_DOSEN = "DATA DOSEN FK UNPAD_Pak Dede.xlsx"
EXCEL_STAFF = "DATA TENDIK FK UNPAD_Pak Dede.xlsx"

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

def load_data_klinik():
    if os.path.exists("Backup_Data_Klinik.csv"):
        try:
            df = pd.read_csv("Backup_Data_Klinik.csv", dtype=str)
            if len(df) > 0: 
                df.columns = df.columns.str.strip()
                return df.fillna("")
        except:
            pass
    if not URL_KLINIK:
        return pd.DataFrame(columns=["No.", "Nama Klinik", "Kode Klinik", "Penanggung Jawab", "Lokasi / Alamat", "Nomor Telepon", "Keterangan"])
    try:
        df = pd.read_csv(URL_KLINIK, dtype=str)
        df.columns = df.columns.str.strip()
        if len(df.columns) > 4:
            df = df.iloc[:, 4:]
            df.columns = df.columns.str.strip()
        df = df.dropna(how='all').reset_index(drop=True)
        if "No." not in df.columns:
            df.insert(0, "No.", range(1, len(df) + 1))
        return df.fillna("")
    except Exception as e:
        st.error(f"Gagal memuat Google Sheets Data Klinik: {e}")
        return pd.DataFrame(columns=["No.", "Nama Klinik", "Kode Klinik", "Penanggung Jawab", "Lokasi / Alamat", "Nomor Telepon", "Keterangan"])

def load_data_tor_mhs():
    if os.path.exists("Backup_Data_TOR_Mhs.csv"):
        try:
            df = pd.read_csv("Backup_Data_TOR_Mhs.csv", dtype=str)
            if len(df) > 0: 
                df.columns = df.columns.str.strip()
                cols = pd.Series(df.columns)
                for dup in cols[cols.duplicated()].unique(): 
                    cols[cols == dup] = [dup + f"_{i}" if i != 0 else dup for i in range(sum(cols == dup))]
                df.columns = cols
                return df.fillna("")
        except:
            pass
    if not URL_TOR_MHS:
        return pd.DataFrame()
    try:
        df_raw = pd.read_csv(URL_TOR_MHS, header=None, dtype=str)
        target_indices = [4, 6, 9, 10, 13, 18, 19, 84, 85, 86, 87, 91] # E, G, J, K, N, S, T, CG, CH, CI, CJ, CN
        valid_indices = [i for i in target_indices if i < len(df_raw.columns)]
        
        if not valid_indices:
            return pd.DataFrame()
            
        df = df_raw.iloc[8:, valid_indices].copy()
        
        headers = []
        for i in valid_indices:
            h_val = str(df_raw.iloc[8, i]).strip() if pd.notna(df_raw.iloc[8, i]) else f"Kolom_{i}"
            headers.append(h_val)
        df.columns = headers
        
        # Mencegah error duplikasi nama kolom secara otomatis
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique(): 
            cols[cols == dup] = [dup + f"_{i}" if i != 0 else dup for i in range(sum(cols == dup))]
        df.columns = cols
        
        df = df.dropna(how='all').reset_index(drop=True)
        return df.fillna("")
    except Exception as e:
        st.error(f"Gagal memuat Google Sheets TOR Mahasiswa: {e}")
        return pd.DataFrame()

def load_data_sptjb():
    if not URL_SPTJB:
        return pd.DataFrame()
    try:
        df = pd.read_csv(URL_SPTJB, header=8, dtype=str)
        df.columns = df.columns.str.strip()
        
        target_indices = [2, 4, 6, 9, 10, 18, 19, 84, 86, 87]
        valid_indices = [i for i in target_indices if i < len(df.columns)]
        if valid_indices:
            df = df.iloc[:, valid_indices]

        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique(): 
            cols[cols == dup] = [dup + f"_{i}" if i != 0 else dup for i in range(sum(cols == dup))]
        df.columns = cols

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

        for col in df.columns:
            if "tanggal" in col.lower():
                df[col] = df[col].apply(clean_date_format)
            if "nominal" in col.lower():
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).replace('nan', '')

        df = df.dropna(how='all')
        return df.fillna("")
    except Exception as e:
        st.error(f"Gagal memuat Google Sheets SPTJB: {e}")
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
        
        headers = []
        for i in valid_indices:
            h_val = str(df_raw.iloc[8, i]).strip() if pd.notna(df_raw.iloc[8, i]) else f"Kolom_{i}"
            headers.append(h_val)
        df.columns = headers

        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique(): 
            cols[cols == dup] = [dup + f"_{i}" if i != 0 else dup for i in range(sum(cols == dup))]
        df.columns = cols

        df = df.dropna(how='all').reset_index(drop=True)
        df.insert(0, "No.", range(1, len(df) + 1))

        target_col_idx = -1
        for idx, col_name in enumerate(df.columns):
            if any(k in col_name.lower() for k in ["siat", "perencanaan", "proses", "link", "url"]):
                target_col_idx = idx
                break
        
        if target_col_idx != -1:
            df.insert(target_col_idx + 1, "Checklist", False)
        else:
            df["Checklist"] = False

        return df.fillna("")
    except Exception as e:
        st.error(f"Gagal memuat data Verifikator Bu Wadek: {e}")
        return pd.DataFrame()

def simpan_backup():
    st.session_state.df_dosen.to_csv("Backup_Data_Dosen.csv", index=False)
    st.session_state.df_staff.to_csv("Backup_Data_Staff.csv", index=False)
    st.session_state.df_klinik.to_csv("Backup_Data_Klinik.csv", index=False)
    st.session_state.df_tor_mhs.to_csv("Backup_Data_TOR_Mhs.csv", index=False)

if "df_dosen" not in st.session_state:
    st.session_state.df_dosen = load_data_dosen()
if "df_staff" not in st.session_state:
    st.session_state.df_staff = load_data_staff()
if "df_klinik" not in st.session_state:
    st.session_state.df_klinik = load_data_klinik()
if "df_tor_mhs" not in st.session_state:
    st.session_state.df_tor_mhs = load_data_tor_mhs()
if "df_sptjb" not in st.session_state:
    st.session_state.df_sptjb = load_data_sptjb()
if "df_verif_sptjb" not in st.session_state:
    st.session_state.df_verif_sptjb = load_data_verifikator()

# ==========================================
# SIDEBAR & NAVIGASI
# ==========================================
st.sidebar.success(f"👤 Login as: **{st.session_state.current_user}**")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.current_role = ""
    st.query_params.clear()
    st.rerun()

st.sidebar.markdown("---")

if st.session_state.current_role == "verifikator":
    kategori_data = "✔️ Verifikator SPTJB"
    st.sidebar.radio("👥 Pilih Kategori Data:", [kategori_data])
    st.sidebar.markdown("---")
    menu = st.sidebar.selectbox("Pilih Menu Navigasi", [
        "🏠 Home / Beranda",
        "🔍 Verifikasi & Cek Dokumen SPTJB"
    ])
    st.sidebar.markdown("---")
    st.sidebar.info("Anda berada di **Mode Verifikator Khusus**")
    
    df_aktif = st.session_state.df_verif_sptjb
    kategori_nama = "Verifikasi SPTJB"

else:
    kategori_data = st.sidebar.radio(
        "👥 Pilih Kategori Data:",
        ["👨‍⚕️ Data Dosen", "👨‍💼 Data Staff", "🏥 Data Klinik", "🎓 TOR Mahasiswa", "📄 Nomor SPTJB"]
    )
    st.sidebar.markdown("---")

    if kategori_data == "📄 Nomor SPTJB":
        menu = st.sidebar.selectbox("Pilih Menu Navigasi", ["🏠 Home / Beranda", "📋 Lihat & Cari Data"])
    else:
        menu = st.sidebar.selectbox(
            "Pilih Menu Navigasi",
            ["🏠 Home / Beranda", "📋 Lihat & Cari Data", "➕ Tambah Data Baru", "✏️ Edit Data", "🗑️ Hapus Data", "📥 Unduh / Simpan ke Excel"],
        )

    st.sidebar.markdown("---")
    st.sidebar.info(f"Anda sedang berada di mode **{kategori_data}**")

    if kategori_data == "👨‍⚕️ Data Dosen":
        df_aktif = st.session_state.df_dosen
        kategori_nama = "Dosen"
    elif kategori_data == "👨‍💼 Data Staff":
        df_aktif = st.session_state.df_staff
        kategori_nama = "Staff"
    elif kategori_data == "🏥 Data Klinik":
        df_aktif = st.session_state.df_klinik
        kategori_nama = "Klinik"
    elif kategori_data == "🎓 TOR Mahasiswa":
        df_aktif = st.session_state.df_tor_mhs
        kategori_nama = "TOR Mahasiswa"
    else:
        df_aktif = st.session_state.df_sptjb
        kategori_nama = "SPTJB"

def clean_val(val):
    if pd.isna(val) or str(val).lower() == 'nan': return ""
    val_str = str(val)
    if val_str.endswith('.0'): val_str = val_str[:-2]
    return val_str

# ==========================================
# KONTEN UTAMA APLIKASI (DASHBOARD HOME)
# ==========================================
if menu == "🏠 Home / Beranda":
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 35px; border-radius: 12px; color: white; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <h1 style="margin: 0; font-size: 2.3rem;">📊 Dashboard Utama RENCANG</h1>
            <p style="font-size: 1.15rem; margin-top: 10px; opacity: 0.9;">
                Sistem Informasi Terintegrasi Perencanaan dan Keuangan Fakultas Kedokteran Universitas Padjadjaran.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 📌 **Statistik Ringkas Sistem**")
    
    col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns(5)
    with col_h1:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #1e3a8a; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <p style="color: #64748b; margin: 0; font-size: 0.8rem; font-weight: 600;">👨‍⚕️ Data Dosen</p>
                <h3 style="color: #1e3a8a; margin: 6px 0 0 0; font-size: 1.5rem;">{len(st.session_state.df_dosen)}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_h2:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #0d9488; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <p style="color: #64748b; margin: 0; font-size: 0.8rem; font-weight: 600;">👨‍💼 Data Staff</p>
                <h3 style="color: #0d9488; margin: 6px 0 0 0; font-size: 1.5rem;">{len(st.session_state.df_staff)}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_h3:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #2563eb; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <p style="color: #64748b; margin: 0; font-size: 0.8rem; font-weight: 600;">🏥 Data Klinik</p>
                <h3 style="color: #2563eb; margin: 6px 0 0 0; font-size: 1.5rem;">{len(st.session_state.df_klinik)}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_h4:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #7c3aed; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <p style="color: #64748b; margin: 0; font-size: 0.8rem; font-weight: 600;">🎓 TOR Mhs</p>
                <h3 style="color: #7c3aed; margin: 6px 0 0 0; font-size: 1.5rem;">{len(st.session_state.df_tor_mhs)}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_h5:
        st.markdown(
            f"""
            <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 5px solid #d97706; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <p style="color: #64748b; margin: 0; font-size: 0.8rem; font-weight: 600;">📄 Verif SPTJB</p>
                <h3 style="color: #d97706; margin: 6px 0 0 0; font-size: 1.5rem;">{len(st.session_state.df_verif_sptjb)}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(f"💡 Anda sedang masuk sebagai: **{st.session_state.current_user}** dengan peran (**{st.session_state.current_role.upper()}**). Silakan gunakan menu navigasi di sidebar sebelah kiri untuk mulai mengelola atau memeriksa data.")

elif menu == "🔍 Verifikasi & Cek Dokumen SPTJB":
    st.markdown(
        f"""
        <div class="sticky-wrapper">
            <h2 style="margin:0; padding:0; font-size: 1.75rem;">✔️ Panel Khusus Verifikator SPTJB</h2>
            <p style="margin: 5px 0 0 0; color: #6b7280; font-size: 0.95rem;">Total Data Verifikasi SPTJB: <b>{len(df_aktif)}</b></p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    keyword_verif = st.text_input("Cari data verifikasi SPTJB:", placeholder="Ketik kata kunci...")
    df_verif = df_aktif.copy()
    if keyword_verif and len(df_verif.columns) > 0:
        mask = df_verif.apply(lambda row: row.astype(str).str.contains(keyword_verif, case=False, na=False).any(), axis=1)
        df_verif = df_verif[mask]

    column_config_dict = {}
    for col in df_verif.columns:
        if any(k in col.lower() for k in ["link", "dokumen", "url", "file", "upload"]):
            column_config_dict[col] = st.column_config.LinkColumn(
                col,
                help="Klik untuk membuka tautan dokumen upload",
                display_text="🔗 Buka Dokumen"
            )
        elif col == "Checklist":
            column_config_dict[col] = st.column_config.CheckboxColumn(
                "Checklist",
                help="Centang untuk menandai verifikasi",
                default=False
            )

    st.markdown("**Daftar Tabel Verifikasi SPTJB:**")
    st.dataframe(
        df_verif,
        use_container_width=True,
        height=400,
        hide_index=True,
        column_config=column_config_dict
    )

    if len(df_verif) > 0:
        st.markdown("---")
        st.markdown("### 🔍 **Pilih Baris Data untuk Melihat Detail Lengkap**")
        
        row_options = [f"Baris No. {row.iloc[0]} — ({row.iloc[1] if len(row) > 1 else 'Data'})" for _, row in df_verif.iterrows()]
        selected_option = st.selectbox("Pilih baris yang ingin diperiksa rinciannya:", row_options)
        
        if selected_option:
            selected_idx = row_options.index(selected_option)
            selected_data = df_verif.iloc[selected_idx]
            
            st.markdown(f"**📌 Rincian Lengkap Baris:**")
            
            detail_items = []
            for col_name, val in selected_data.items():
                detail_items.append({"Nama Kolom": col_name, "Isi Data": val})
            
            detail_df = pd.DataFrame(detail_items)
            st.dataframe(detail_df, use_container_width=True, hide_index=True)

elif menu == "📋 Lihat & Cari Data":
    st.markdown(
        f"""
        <div class="sticky-wrapper">
            <h2 style="margin:0; padding:0; font-size: 1.75rem;">🔍 Pencarian & Filter Data {kategori_nama}</h2>
            <p style="margin: 5px 0 0 0; color: #6b7280; font-size: 0.95rem;">Total Data {kategori_nama} Tercatat: <b>{len(df_aktif)}</b></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if kategori_nama == "SPTJB":
        keyword = st.text_input("Cari SPTJB (berdasarkan kata kunci):", placeholder="Ketik di sini...")
        filtered_df = df_aktif.copy()
        if keyword and len(filtered_df.columns) > 0:
            mask = filtered_df.apply(lambda row: row.astype(str).str.contains(keyword, case=False, na=False).any(), axis=1)
            filtered_df = filtered_df[mask]
        
        st.markdown(f"**Menampilkan {len(filtered_df)} data:**")
        
        column_config_dict = {}
        for col in filtered_df.columns:
            if any(k in col.lower() for k in ["link", "dokumen", "url", "file"]):
                column_config_dict[col] = st.column_config.LinkColumn(
                    col,
                    help="Klik untuk membuka tautan dokumen",
                    display_text="🔗 Buka Dokumen"
                )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=500,
            hide_index=True,
            column_config=column_config_dict
        )
    elif kategori_nama == "Klinik":
        keyword = st.text_input("Cari Klinik (berdasarkan kata kunci):", placeholder="Ketik di sini...")
        filtered_df = df_aktif.copy()
        if keyword and len(filtered_df.columns) > 0:
            mask = filtered_df.apply(lambda row: row.astype(str).str.contains(keyword, case=False, na=False).any(), axis=1)
            filtered_df = filtered_df[mask]
        st.markdown(f"**Menampilkan {len(filtered_df)} data:**")
        st.dataframe(filtered_df, use_container_width=True, height=500, hide_index=True)
    elif kategori_nama == "TOR Mahasiswa":
        keyword = st.text_input("Cari TOR Mahasiswa (berdasarkan kata kunci):", placeholder="Ketik di sini...")
        filtered_df = df_aktif.copy()
        if keyword and len(filtered_df.columns) > 0:
            mask = filtered_df.apply(lambda row: row.astype(str).str.contains(keyword, case=False, na=False).any(), axis=1)
            filtered_df = filtered_df[mask]
        st.markdown(f"**Menampilkan {len(filtered_df)} data:**")
        st.dataframe(filtered_df, use_container_width=True, height=500, hide_index=True)
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

elif menu == "➕ Tambah Data Baru":
    st.subheader(f"➕ Form Penambahan Data {kategori_nama}")
    
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
                jabatan = st.text_input("Jabatan")
                unit_kerja = st.text_input("Unit Kerja / Bagian")
            with col2:
                status_pegawai = st.selectbox("Status Pegawai", ["PNS", "Non PNS", "Honorer", "Lainnya"])
                jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-Laki", "Perempuan"])
                hp = st.text_input("Nomor HP")
                email = st.text_input("Email")
        elif kategori_nama == "Klinik":
            with col1:
                nama_klinik = st.text_input("Nama Klinik*")
                kode_klinik = st.text_input("Kode Klinik")
                penanggung_jawab = st.text_input("Penanggung Jawab")
            with col2:
                lokasi = st.text_area("Lokasi / Alamat Klinik")
                telepon = st.text_input("Nomor Telepon")
                keterangan = st.text_input("Keterangan Tambahan")
        elif kategori_nama == "TOR Mahasiswa":
            with col1:
                nama_mhs = st.text_input("Nama Mahasiswa*")
                npm_mhs = st.text_input("NPM*")
                judul_tor = st.text_input("Judul Kegiatan TOR*")
            with col2:
                departemen_mhs = st.text_input("Departemen / Program Studi")
                nominal_tor = st.text_input("Nominal Pengajuan (Rp)")
                status_tor = st.selectbox("Status Pengajuan", ["Diajukan", "Verifikasi", "Disetujui", "Ditolak"])
                
        submit_button = st.form_submit_button(f"💾 Simpan Data {kategori_nama}", use_container_width=True)
        if submit_button:
            if kategori_nama == "Klinik" and not nama_klinik:
                st.warning("⚠️ Nama Klinik wajib diisi!")
            elif kategori_nama == "TOR Mahasiswa" and (not nama_mhs or not npm_mhs):
                st.warning("⚠️ Nama Mahasiswa dan NPM wajib diisi!")
            elif kategori_nama in ["Dosen", "Staff"] and not locals().get("nama", ""):
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
                elif kategori_nama == "Klinik":
                    new_data = {"No.": len(df_aktif)+1, "Nama Klinik": nama_klinik, "Kode Klinik": kode_klinik, "Penanggung Jawab": penanggung_jawab, "Lokasi / Alamat": lokasi, "Nomor Telepon": telepon, "Keterangan": keterangan}
                    st.session_state.df_klinik = pd.concat([st.session_state.df_klinik, pd.DataFrame([new_data])], ignore_index=True)
                    simpan_backup()
                elif kategori_nama == "TOR Mahasiswa":
                    new_data = {"No.": len(df_aktif)+1, "Nama Mahasiswa": nama_mhs, "NPM": npm_mhs, "Judul Kegiatan TOR": judul_tor, "Departemen / Program Studi": departemen_mhs, "Nominal Pengajuan": nominal_tor, "Status Pengajuan": status_tor}
                    st.session_state.df_tor_mhs = pd.concat([st.session_state.df_tor_mhs, pd.DataFrame([new_data])], ignore_index=True)
                    simpan_backup()
                
                st.success(f"🎉 Data {kategori_nama} berhasil ditambahkan!")
                time.sleep(1.5)
                st.rerun()

elif menu == "✏️ Edit Data":
    st.subheader(f"✏️ Edit Data {kategori_nama}")
    if len(df_aktif) == 0:
        st.info(f"Belum ada data {kategori_nama} untuk diedit.")
    else:
        if kategori_nama in ["Klinik", "TOR Mahasiswa"]:
            identitas_kolom = next((col for col in df_aktif.columns if "nama" in col.lower()), df_aktif.columns[1] if len(df_aktif.columns) > 1 else df_aktif.columns[0])
        else:
            identitas_kolom = "NAMA" if "NAMA" in df_aktif.columns else df_aktif.columns[1]

        pilihan = df_aktif[identitas_kolom].dropna().tolist() if identitas_kolom in df_aktif.columns else []
        if not pilihan:
            st.warning(f"Kolom identitas tidak ditemukan pada data.")
        else:
            to_edit = st.selectbox(f"Pilih data {kategori_nama} yang ingin diedit:", pilihan)
            old_data = df_aktif[df_aktif[identitas_kolom] == to_edit].iloc[0]
            idx = df_aktif[df_aktif[identitas_kolom] == to_edit].index[0]
            
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
                elif kategori_nama == "Klinik":
                    c_list = list(df_aktif.columns)
                    val_nm = clean_val(old_data[c_list[1]]) if len(c_list) > 1 else ""
                    val_kd = clean_val(old_data[c_list[2]]) if len(c_list) > 2 else ""
                    val_pj = clean_val(old_data[c_list[3]]) if len(c_list) > 3 else ""
                    val_lok = clean_val(old_data[c_list[4]]) if len(c_list) > 4 else ""
                    val_tel = clean_val(old_data[c_list[5]]) if len(c_list) > 5 else ""
                    val_ket = clean_val(old_data[c_list[6]]) if len(c_list) > 6 else ""

                    with col1:
                        nama_klinik = st.text_input("Nama Klinik*", value=val_nm)
                        kode_klinik = st.text_input("Kode Klinik", value=val_kd)
                        penanggung_jawab = st.text_input("Penanggung Jawab", value=val_pj)
                    with col2:
                        lokasi = st.text_area("Lokasi / Alamat Klinik", value=val_lok)
                        telepon = st.text_input("Nomor Telepon", value=val_tel)
                        keterangan = st.text_input("Keterangan Tambahan", value=val_ket)
                elif kategori_nama == "TOR Mahasiswa":
                    c_list = list(df_aktif.columns)
                    val_nm_mhs = clean_val(old_data[c_list[0]]) if len(c_list) > 0 else ""
                    val_npm_mhs = clean_val(old_data[c_list[1]]) if len(c_list) > 1 else ""
                    val_jdl_tor = clean_val(old_data[c_list[2]]) if len(c_list) > 2 else ""
                    val_dept_mhs = clean_val(old_data[c_list[3]]) if len(c_list) > 3 else ""
                    val_nom_tor = clean_val(old_data[c_list[4]]) if len(c_list) > 4 else ""
                    val_stat_tor = clean_val(old_data[c_list[5]]) if len(c_list) > 5 else "Diajukan"

                    with col1:
                        nama_mhs = st.text_input("Nama Mahasiswa*", value=val_nm_mhs)
                        npm_mhs = st.text_input("NPM*", value=val_npm_mhs)
                        judul_tor = st.text_input("Judul Kegiatan TOR*", value=val_jdl_tor)
                    with col2:
                        departemen_mhs = st.text_input("Departemen / Program Studi", value=val_dept_mhs)
                        nominal_tor = st.text_input("Nominal Pengajuan (Rp)", value=val_nom_tor)
                        status_opts_tor = ["Diajukan", "Verifikasi", "Disetujui", "Ditolak"]
                        idx_status_tor = status_opts_tor.index(val_stat_tor) if val_stat_tor in status_opts_tor else 0
                        status_tor = st.selectbox("Status Pengajuan", status_opts_tor, index=idx_status_tor)

                submit_edit = st.form_submit_button("🔄 Perbarui Data", use_container_width=True)
                if submit_edit:
                    if kategori_nama == "Klinik" and not nama_klinik:
                        st.warning("⚠️ Nama Klinik wajib diisi!")
                    elif kategori_nama == "TOR Mahasiswa" and not nama_mhs:
                        st.warning("⚠️ Nama Mahasiswa wajib diisi!")
                    elif kategori_nama in ["Dosen", "Staff"] and not locals().get("nama", ""):
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
                        elif kategori_nama == "Klinik":
                            c_list = list(df_aktif.columns)
                            if len(c_list) > 1: st.session_state.df_klinik.at[idx, c_list[1]] = nama_klinik
                            if len(c_list) > 2: st.session_state.df_klinik.at[idx, c_list[2]] = kode_klinik
                            if len(c_list) > 3: st.session_state.df_klinik.at[idx, c_list[3]] = penanggung_jawab
                            if len(c_list) > 4: st.session_state.df_klinik.at[idx, c_list[4]] = lokasi
                            if len(c_list) > 5: st.session_state.df_klinik.at[idx, c_list[5]] = telepon
                            if len(c_list) > 6: st.session_state.df_klinik.at[idx, c_list[6]] = keterangan
                            simpan_backup()
                        elif kategori_nama == "TOR Mahasiswa":
                            c_list = list(df_aktif.columns)
                            if len(c_list) > 0: st.session_state.df_tor_mhs.at[idx, c_list[0]] = nama_mhs
                            if len(c_list) > 1: st.session_state.df_tor_mhs.at[idx, c_list[1]] = npm_mhs
                            if len(c_list) > 2: st.session_state.df_tor_mhs.at[idx, c_list[2]] = judul_tor
                            if len(c_list) > 3: st.session_state.df_tor_mhs.at[idx, c_list[3]] = departemen_mhs
                            if len(c_list) > 4: st.session_state.df_tor_mhs.at[idx, c_list[4]] = nominal_tor
                            if len(c_list) > 5: st.session_state.df_tor_mhs.at[idx, c_list[5]] = status_tor
                            simpan_backup()
                        
                        st.success(f"✅ Data {kategori_nama} berhasil diperbarui!")
                        time.sleep(1.5)
                        st.rerun()

elif menu == "🗑️ Hapus Data":
    st.subheader(f"🗑️ Penghapusan Data {kategori_nama}")
    if len(df_aktif) == 0:
        st.info(f"Tidak ada data {kategori_nama} untuk dihapus.")
    else:
        if kategori_nama in ["Klinik", "TOR Mahasiswa"]:
            identitas_kolom = next((col for col in df_aktif.columns if "nama" in col.lower()), df_aktif.columns[1] if len(df_aktif.columns) > 1 else df_aktif.columns[0])
        else:
            identitas_kolom = "NAMA" if "NAMA" in df_aktif.columns else df_aktif.columns[1]

        pilihan = df_aktif[identitas_kolom].dropna().tolist() if identitas_kolom in df_aktif.columns else []
        if not pilihan:
            st.warning(f"Kolom identitas tidak ditemukan pada data.")
        else:
            to_delete = st.selectbox(f"Pilih data {kategori_nama} yang ingin dihapus:", pilihan)

            if st.button("🗑️ Hapus Data", type="primary"):
                if kategori_nama == "Dosen":
                    st.session_state.df_dosen = st.session_state.df_dosen[st.session_state.df_dosen["NAMA"] != to_delete].reset_index(drop=True)
                    simpan_backup()
                elif kategori_nama == "Staff":
                    st.session_state.df_staff = st.session_state.df_staff[st.session_state.df_staff["NAMA"] != to_delete].reset_index(drop=True)
                    simpan_backup()
                elif kategori_nama == "Klinik":
                    st.session_state.df_klinik = st.session_state.df_klinik[st.session_state.df_klinik[identitas_kolom] != to_delete].reset_index(drop=True)
                    simpan_backup()
                elif kategori_nama == "TOR Mahasiswa":
                    st.session_state.df_tor_mhs = st.session_state.df_tor_mhs[st.session_state.df_tor_mhs[identitas_kolom] != to_delete].reset_index(drop=True)
                    simpan_backup()
                
                st.success(f"✅ Data {kategori_nama} **{to_delete}** berhasil dihapus!")
                time.sleep(1.5)
                st.rerun()

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
