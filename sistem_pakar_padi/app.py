"""
app.py - Sawah Sehat: Sistem Pakar Diagnosis Penyakit Padi (Forward Chaining + CBR)
Jalankan:  streamlit run app.py
"""
import re

import pandas as pd
import streamlit as st

import engine as eng
import theme

st.set_page_config(
    page_title="Sawah Sehat | Sistem Pakar Penyakit Padi",
    page_icon=":material/grass:",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(theme.css(), unsafe_allow_html=True)

STATUS = {
    "terkonfirmasi": ("Terkonfirmasi", "ok"),
    "dugaan": ("Dugaan kuat", "mid"),
    "lemah": ("Kurang meyakinkan", "low"),
}
MENU = ["Konsultasi", "Basis Pengetahuan", "Uji Akurasi", "Tentang"]


# ----------------------------------------------------------------------
# Helper
# ----------------------------------------------------------------------
def reset_form(kode_gejala):
    """Callback tombol 'Kosongkan': hapus semua centang dan hasil."""
    for g in kode_gejala:
        st.session_state[f"cb_{g}"] = False
    st.session_state.pop("hasil", None)


def slug(teks):
    return re.sub(r"[^a-z0-9]+", "_", teks.lower()).strip("_")


# ----------------------------------------------------------------------
# Hasil diagnosis
# ----------------------------------------------------------------------
def tampil_hasil(data, res, pilihan_sekarang):
    h = res["hasil"]
    top = h["top"]
    st.html(theme.section("Hasil diagnosis", "Berdasarkan gejala yang Anda pilih."))

    if sorted(pilihan_sekarang) != sorted(res["facts"]):
        st.caption("Pilihan gejala sudah berubah. Tekan **Diagnosa** lagi untuk memperbarui hasil.")

    if top is None:
        st.error(h["pesan"])
    else:
        label, key = STATUS[h["status"]]
        peny = data["penyakit"].set_index("kode_penyakit").loc[top["kode_penyakit"]]
        st.html(theme.diagnosis_card(top, label, key, peny["deskripsi"]))
        st.caption(h["pesan"])
        if h["ambigu"]:
            st.warning("Ada lebih dari satu penyakit dengan nilai yang sama. Tambahkan gejala agar hasilnya lebih spesifik.")
        kiri, kanan = st.columns([3, 2], gap="large")
        kiri.html(theme.penanganan(peny["solusi"]))
        kanan.html(theme.rank_bars(h["ranking"]))

    with st.expander("Lihat proses perhitungan", icon=":material/calculate:"):
        t1, t2, t3 = st.tabs(["Ranking CBR", "Aturan Forward Chaining", "Perhitungan similarity"])
        with t1:
            r = h["ranking"][["kode_penyakit", "nama_penyakit", "id_kasus", "similarity",
                              "jumlah_cocok", "gejala_cocok", "fc_aktif"]]
            st.dataframe(
                r, hide_index=True, width="stretch",
                column_config={"similarity": st.column_config.ProgressColumn(
                    "similarity", min_value=0.0, max_value=1.0, format="%.3f")})
        with t2:
            st.caption("fired = True berarti semua premis aturan terpenuhi (aturan menyala).")
            st.dataframe(h["rules"], hide_index=True, width="stretch")
        with t3:
            if h["perhitungan"] is not None:
                p = h["perhitungan"]
                st.dataframe(p, hide_index=True, width="stretch")
                a, b = int(p["s x w"].sum()), int(p["bobot (w)"].sum())
                st.latex(rf"Similarity(T,S)=\frac{{\sum s_i \cdot w_i}}{{\sum w_i}}=\frac{{{a}}}{{{b}}}={a/b:.3f}")
            else:
                st.write("Tidak ada perhitungan untuk ditampilkan.")

    # ---------------- Revise & Retain ----------------
    st.html(theme.section("Sudah cocok dengan sawah Anda?",
                          "Konfirmasi atau koreksi hasilnya. Kasus yang benar disimpan agar sistem makin pintar."))
    kode_semua = list(data["penyakit"].kode_penyakit)
    nama = dict(zip(data["penyakit"].kode_penyakit, data["penyakit"].nama_penyakit))
    opsi = ["Ya, sesuai", "Tidak, saya koreksi"]
    pilih = st.radio("Diagnosis sistem", opsi, index=0 if top else 1,
                     horizontal=True, key="rev_radio", label_visibility="collapsed")
    kode_final = top["kode_penyakit"] if top else None
    if pilih == opsi[1]:
        kode_final = st.selectbox("Diagnosis yang benar", kode_semua,
                                  format_func=lambda k: f"{k} - {nama[k]}", key="rev_select")
    if st.button("Simpan sebagai kasus baru", icon=":material/save:", disabled=kode_final is None):
        ok, msg = eng.retain_case(res["facts"], kode_final)
        (st.success if ok else st.info)(msg)


# ----------------------------------------------------------------------
# Halaman
# ----------------------------------------------------------------------
def halaman_konsultasi(data, ambang):
    gejala = data["gejala"]
    if "bagian" not in gejala.columns:
        gejala = gejala.assign(bagian="Semua gejala")
    kode = list(gejala.kode_gejala)
    nama_g = dict(zip(gejala.kode_gejala, gejala.nama_gejala))

    st.html(theme.section("Apa yang terlihat di sawah Anda?",
                          "Centang semua gejala yang teramati. Makin lengkap, makin tepat hasilnya."))

    semua = list(dict.fromkeys(gejala.bagian))
    kiri = [b for b in theme.LAYOUT[0] if b in semua]
    kanan = [b for b in theme.LAYOUT[1] if b in semua]
    kiri += [b for b in semua if b not in kiri + kanan]  # kelompok tak dikenal ikut di kiri

    for kolom, daftar in zip(st.columns(2, gap="large"), (kiri, kanan)):
        with kolom:
            for b in daftar:
                sub = gejala[gejala.bagian == b]
                dipilih = sum(bool(st.session_state.get(f"cb_{g}")) for g in sub.kode_gejala)
                with st.container(key=f"grp_{slug(b)}"):
                    st.html(theme.group_header(b, dipilih, len(sub)))
                    for r in sub.itertuples():
                        st.checkbox(f"{r.kode_gejala} · {r.nama_gejala}", key=f"cb_{r.kode_gejala}")

    pilihan = [g for g in kode if st.session_state.get(f"cb_{g}")]
    st.html(theme.ringkasan(pilihan, nama_g))

    b1, b2, _ = st.columns([1.3, 1.1, 4])
    diagnosa = b1.button("Diagnosa", type="primary", icon=":material/search:")
    b2.button("Kosongkan", icon=":material/restart_alt:", on_click=reset_form, args=(kode,))

    if diagnosa:
        if not pilihan:
            st.warning("Pilih minimal satu gejala dulu.")
            st.session_state.pop("hasil", None)
        else:
            st.session_state["hasil"] = {"facts": list(pilihan),
                                         "hasil": eng.diagnose(pilihan, data, ambang)}

    if "hasil" in st.session_state:
        tampil_hasil(data, st.session_state["hasil"], pilihan)


def halaman_basis(data):
    st.html(theme.section("Basis pengetahuan", "Seluruh pengetahuan sistem tersimpan sebagai file CSV di folder data/."))
    nama_tab = ["Penyakit", "Gejala", "Aturan (FC)", "Bobot", "Basis kasus (CBR)"]
    kunci = ["penyakit", "gejala", "rules", "bobot", "kasus"]
    for tab, k in zip(st.tabs(nama_tab), kunci):
        with tab:
            st.dataframe(data[k], hide_index=True, width="stretch")
            st.download_button(f"Unduh {k}.csv", data[k].to_csv(index=False).encode("utf-8"),
                               file_name=f"{k}.csv", mime="text/csv", key=f"dl_{k}",
                               icon=":material/download:")


def halaman_evaluasi(data, ambang):
    st.html(theme.section("Uji akurasi", "Bandingkan diagnosis sistem dengan diagnosis pakar pada data uji."))
    st.markdown("Format CSV: kolom `id_uji`, `gejala` (dipisah titik koma, mis. `G01;G02`), dan `diagnosis_pakar` (mis. `P01`).")
    st.warning("data_uji.csv bawaan hanya contoh sintetis untuk demo. Ganti dengan data uji yang divalidasi pakar sebelum dilaporkan.")
    up = st.file_uploader("Unggah CSV data uji (opsional)", type="csv")
    uji = pd.read_csv(up, dtype=str) if up else pd.read_csv(eng.DATA_DIR / "data_uji.csv", dtype=str)
    if st.button("Jalankan uji", type="primary", icon=":material/play_arrow:"):
        hasil, akurasi = eng.evaluasi(uji, data, ambang)
        st.html(theme.tiles([("Data uji", len(hasil)), ("Benar", int(hasil["benar"].sum())),
                             ("Akurasi", f"{akurasi * 100:.1f}%")]))
        st.dataframe(hasil, hide_index=True, width="stretch")


def halaman_tentang():
    st.html(theme.section("Cara kerja", "Dari gejala di sawah sampai diagnosis, dalam lima langkah."))
    st.html(theme.alur())
    st.markdown(
        "**Tentang ambang similarity.** Nilai di pengaturan menentukan batas hasil dianggap meyakinkan. "
        "Di bawah batas itu, sistem tetap menampilkan kandidat terbaik tetapi memberi label *kurang meyakinkan*."
    )


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    data = eng.load_data()
    st.html(theme.hero(len(data["penyakit"]), len(data["gejala"])))

    c1, c2 = st.columns([5, 1.5], vertical_alignment="center")
    with c1:
        menu = st.segmented_control("Menu", MENU, default="Konsultasi", key="nav",
                                    label_visibility="collapsed")
    with c2.popover("Pengaturan", icon=":material/tune:"):
        st.slider("Ambang similarity", 0.1, 1.0, 0.5, 0.05, key="ambang",
                  help="Di bawah nilai ini, hasil dianggap kurang meyakinkan.")
    ambang = st.session_state.get("ambang", 0.5)

    menu = menu or "Konsultasi"
    if menu == "Konsultasi":
        halaman_konsultasi(data, ambang)
    elif menu == "Basis Pengetahuan":
        halaman_basis(data)
    elif menu == "Uji Akurasi":
        halaman_evaluasi(data, ambang)
    else:
        halaman_tentang()

    st.html(theme.footer())


main()
