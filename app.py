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
    page_title="Sistem Manajemen Data Terintegrasi FK UNPAD",
    page_icon="🏥",
    layout="wide",
)

# ==========================================
# LINK GOOGLE SHEETS SPTJB (Tempel link Google Sheets biasa Anda di sini)
# ==========================================
URL_ASLI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSm7LCABdy45Kmaid-V2eab1MA9so7Os7Nt01FeQlIaAcHxNksu6PrfgJQaVQPWWAPNxhvwdrSXoaOq/pub?gid=87462462&single=true&output=csv"

# Konversi otomatis link biasa menjadi link CSV otomatis
def convert_sheets_url(url):
    if "export?format=csv" in url:
        return url
    if "/edit" in url:
        base_url = url.split("/edit")[0]
        if "gid=" in url:
            gid = url.split("gid=")[1].split("&")[0]
            return f"{base_url}/export?format=csv&gid={gid}"
        return f"{base_url}/export?format=csv"
    return url

URL_SPTJB = convert_sheets_url(URL_ASLI)

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

def load_data_sptjb():
    try:
        # Membaca data Google Sheets dengan header berada di baris ke-9 (index 8)
        df = pd.read_csv(URL_SPTJB, header=8, dtype=str)
        df.columns = df.columns.str.strip()
        
        # Memilih kolom spesifik berdasarkan indeks kolom Excel (C, E, G, J, K, S, T, CG, CI, CJ)
        target_indices = [2, 4, 6, 9, 10, 18, 19, 84, 86, 87]
        
        valid_indices = [i for i in target_indices if i < len(df.columns)]
        if valid_indices:
            df = df.iloc[:, valid_indices]

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

        return df.fillna("")
    except Exception as e:
        st.error(f"Gagal memuat Google Sheets SPTJB: {e}")
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

kategori_data = st.sidebar.radio(
    "👥 Pilih Kategori Data:",
    ["👨‍⚕️ Data Dosen", "👨‍💼 Data Staff", "📄 Nomor SPTJB"]
)

st.sidebar.markdown("---")

# Mengatur menu khusus SPTJB (Hanya Lihat & Cari Data saja)
if kategori_data == "📄 Nomor SPTJB":
    menu = st.sidebar.selectbox(
        "Pilih Menu Navigasi",
        ["📋 Lihat & Cari Data"]
    )
else:
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
    df_aktif = st.session_state.df_sptjb
    kategori_nama = "SPTJB"

def clean_val(val):
    if pd.isna(val) or str(val).lower() == 'nan': return ""
    val_str = str(val)
    if val_str.endswith('.0'): val_str = val_str[:-2]
    return val_str

if menu == "📋 Lihat & Cari Data":
    st.subheader(f"🔍 Pencarian & Filter Data {kategori_nama}")
    st.metric(f"Total Data {kategori_nama} Tercatat", len(df_aktif))
    st.markdown("---")

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
                
        submit_button = st.form_submit_button(f"💾 Simpan Data {kategori_nama}", use_container_width=True)
        if submit_button:
            if not nama:
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
                
                st.success(f"🎉 Data {kategori_nama} **{nama}** berhasil ditambahkan!")
                time.sleep(1.5)
                st.rerun()

elif menu == "✏️ Edit Data":
    st.subheader(f"✏️ Edit Data {kategori_nama}")
    if len(df_aktif) == 0:
        st.info(f"Belum ada data {kategori_nama} untuk diedit.")
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

            submit_edit = st.form_submit_button("🔄 Perbarui Data", use_container_width=True)
            if submit_edit:
                if not nama:
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
                    
                    st.success(f"✅ Data {kategori_nama} **{nama}** berhasil diperbarui!")
                    time.sleep(1.5)
                    st.rerun()

elif menu == "🗑️ Hapus Data":
    st.subheader(f"🗑️ Penghapusan Data {kategori_nama}")
    if len(df_aktif) == 0:
        st.info(f"Tidak ada data {kategori_nama} untuk dihapus.")
    else:
        pilihan = df_aktif["NAMA"].dropna().tolist()
        to_delete = st.selectbox(f"Pilih Nama {kategori_nama} yang ingin dihapus:", pilihan)

        if st.button("🗑️ Hapus Data", type="primary"):
            if kategori_nama == "Dosen":
                st.session_state.df_dosen = st.session_state.df_dosen[st.session_state.df_dosen["NAMA"] != to_delete].reset_index(drop=True)
                simpan_backup()
            elif kategori_nama == "Staff":
                st.session_state.df_staff = st.session_state.df_staff[st.session_state.df_staff["NAMA"] != to_delete].reset_index(drop=True)
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
