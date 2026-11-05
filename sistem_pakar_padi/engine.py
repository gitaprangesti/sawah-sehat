"""
engine.py - Mesin inferensi Sistem Pakar Diagnosis Penyakit Padi
Integrasi Forward Chaining (FC) + Case Based Reasoning (CBR).
Tidak bergantung pada Streamlit, sehingga bisa diuji terpisah (Colab/VSCode).
"""
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
BOBOT_DEFAULT = 3  # dipakai bila pasangan (penyakit, gejala) tidak ada di bobot.csv


# ----------------------------------------------------------------------
# 1. MUAT DATA
# ----------------------------------------------------------------------
def split_gejala(teks):
    """'G01;G02;G03' -> ['G01','G02','G03']"""
    return [g.strip() for g in str(teks).split(";") if g.strip()]


def load_data(data_dir=DATA_DIR):
    data_dir = Path(data_dir)
    return {
        "penyakit": pd.read_csv(data_dir / "penyakit.csv", dtype=str),
        "gejala": pd.read_csv(data_dir / "gejala.csv", dtype=str),
        "rules": pd.read_csv(data_dir / "rules.csv", dtype=str),
        "bobot": pd.read_csv(data_dir / "bobot.csv", dtype={"kode_penyakit": str, "kode_gejala": str, "bobot": int}),
        "kasus": pd.read_csv(data_dir / "kasus.csv", dtype=str),
    }


def _kamus_bobot(bobot_df):
    return {(r.kode_penyakit, r.kode_gejala): int(r.bobot) for r in bobot_df.itertuples()}


# ----------------------------------------------------------------------
# 2. FORWARD CHAINING
# ----------------------------------------------------------------------
def forward_chaining(fakta, rules_df):
    """
    Forward chaining: mulai dari fakta (gejala yang dipilih), cocokkan dengan
    aturan IF-THEN. Aturan 'menyala' (fired) jika SEMUA premisnya ada di working memory.
    Kesimpulan (kode penyakit) ditambahkan ke working memory, diulang sampai tidak
    ada aturan baru yang menyala.
    Return: DataFrame status tiap aturan (terpenuhi, kurang, rasio, fired).
    """
    memori = set(fakta)
    menyala = set()
    berubah = True
    while berubah:
        berubah = False
        for r in rules_df.itertuples():
            if r.rule_id in menyala:
                continue
            premis = split_gejala(r.gejala)
            if all(p in memori for p in premis):
                menyala.add(r.rule_id)
                memori.add(r.kode_penyakit)
                berubah = True

    baris = []
    for r in rules_df.itertuples():
        premis = split_gejala(r.gejala)
        cocok = [p for p in premis if p in fakta]
        kurang = [p for p in premis if p not in fakta]
        baris.append({
            "rule_id": r.rule_id,
            "kode_penyakit": r.kode_penyakit,
            "premis": ", ".join(premis),
            "terpenuhi": ", ".join(cocok),
            "belum_terpenuhi": ", ".join(kurang),
            "rasio": len(cocok) / len(premis) if premis else 0.0,
            "fired": r.rule_id in menyala,
        })
    return pd.DataFrame(baris)


# ----------------------------------------------------------------------
# 3. CASE BASED REASONING (RETRIEVE)
# ----------------------------------------------------------------------
def hitung_similarity(fakta, gejala_kasus, kode_penyakit, kamus):
    """
    Similarity (T,S) = sum(s_i * w_i) / sum(w_i)
    s_i = 1 jika gejala kasus lama ada pada kasus baru, 0 jika tidak.
    """
    total = sum(kamus.get((kode_penyakit, g), BOBOT_DEFAULT) for g in gejala_kasus)
    cocok = sum(kamus.get((kode_penyakit, g), BOBOT_DEFAULT) for g in gejala_kasus if g in fakta)
    return (cocok / total if total else 0.0), cocok, total


def retrieve(fakta, kasus_df, bobot_df, penyakit_df):
    kamus = _kamus_bobot(bobot_df)
    nama = dict(zip(penyakit_df.kode_penyakit, penyakit_df.nama_penyakit))
    baris = []
    for k in kasus_df.itertuples():
        g_kasus = split_gejala(k.gejala)
        sim, cocok, total = hitung_similarity(fakta, g_kasus, k.kode_penyakit, kamus)
        baris.append({
            "id_kasus": k.id_kasus,
            "kode_penyakit": k.kode_penyakit,
            "nama_penyakit": nama.get(k.kode_penyakit, k.kode_penyakit),
            "similarity": round(sim, 4),
            "gejala_cocok": ", ".join(g for g in g_kasus if g in fakta),
            "jumlah_cocok": f"{sum(1 for g in g_kasus if g in fakta)}/{len(g_kasus)}",
            "bobot_cocok": cocok,
            "bobot_total": total,
        })
    return pd.DataFrame(baris)


def rincian_similarity(fakta, id_kasus, kasus_df, bobot_df, gejala_df):
    """Tabel perhitungan langkah demi langkah (seperti Gambar 2 pada artikel)."""
    k = kasus_df[kasus_df.id_kasus == id_kasus].iloc[0]
    kamus = _kamus_bobot(bobot_df)
    nama_g = dict(zip(gejala_df.kode_gejala, gejala_df.nama_gejala))
    baris = []
    for g in split_gejala(k.gejala):
        w = kamus.get((k.kode_penyakit, g), BOBOT_DEFAULT)
        s = 1 if g in fakta else 0
        baris.append({"kode_gejala": g, "gejala": nama_g.get(g, g), "bobot (w)": w,
                      "cocok (s)": s, "s x w": s * w})
    return pd.DataFrame(baris)


# ----------------------------------------------------------------------
# 4. INTEGRASI FC + CBR  (REUSE)
# ----------------------------------------------------------------------
def diagnose(fakta, data, threshold=0.5):
    """
    Alur integrasi:
      1) FC   : cek aturan yang menyala (kepastian berbasis aturan pakar).
      2) CBR  : retrieve - hitung similarity ke seluruh basis kasus.
      3) Reuse: ambil kasus paling mirip; FC dipakai sebagai konfirmasi dan tie-breaker.
    """
    fakta = set(fakta)
    rules_status = forward_chaining(fakta, data["rules"])
    aktif = set(rules_status.loc[rules_status.fired, "kode_penyakit"])
    rasio_rule = rules_status.groupby("kode_penyakit")["rasio"].max().to_dict()

    semua = retrieve(fakta, data["kasus"], data["bobot"], data["penyakit"])
    terbaik = (semua.sort_values("similarity", ascending=False)
                    .drop_duplicates("kode_penyakit").copy())
    terbaik["fc_aktif"] = terbaik.kode_penyakit.isin(aktif)
    terbaik["rasio_rule"] = terbaik.kode_penyakit.map(rasio_rule).fillna(0.0).round(3)
    ranking = (terbaik.sort_values(["similarity", "rasio_rule"], ascending=False)
                      .reset_index(drop=True))

    hasil = {"fakta": sorted(fakta), "rules": rules_status, "ranking": ranking,
             "semua_kasus": semua, "top": None, "perhitungan": None,
             "ambigu": False, "status": "tidak_ada", "pesan": ""}

    if ranking.empty or ranking.loc[0, "similarity"] <= 0:
        hasil["pesan"] = "Tidak ada kasus pada basis pengetahuan yang cocok dengan gejala yang dipilih."
        return hasil

    top = ranking.loc[0]
    hasil["top"] = top.to_dict()
    hasil["perhitungan"] = rincian_similarity(fakta, top.id_kasus, data["kasus"], data["bobot"], data["gejala"])
    if len(ranking) > 1:
        kedua = ranking.loc[1]
        hasil["ambigu"] = bool(kedua.similarity == top.similarity and kedua.rasio_rule == top.rasio_rule)

    if top.similarity >= threshold and top.fc_aktif:
        hasil["status"] = "terkonfirmasi"
        hasil["pesan"] = "Aturan forward chaining menyala dan similarity CBR melewati ambang: diagnosis terkonfirmasi."
    elif top.similarity >= threshold:
        hasil["status"] = "dugaan"
        hasil["pesan"] = "Similarity CBR melewati ambang, tetapi belum ada aturan FC yang terpenuhi penuh: dugaan kuat."
    else:
        hasil["status"] = "lemah"
        hasil["pesan"] = "Similarity di bawah ambang: hasil kurang meyakinkan, tambahkan gejala yang teramati."
    return hasil


# ----------------------------------------------------------------------
# 5. RETAIN (simpan kasus baru ke CSV)
# ----------------------------------------------------------------------
def retain_case(fakta, kode_penyakit, data_dir=DATA_DIR, sumber="pengguna"):
    path = Path(data_dir) / "kasus.csv"
    df = pd.read_csv(path, dtype=str)
    himpunan = set(fakta)
    for k in df.itertuples():
        if k.kode_penyakit == kode_penyakit and set(split_gejala(k.gejala)) == himpunan:
            return False, f"Kasus identik sudah ada ({k.id_kasus}), tidak disimpan ulang."
    nomor = df.id_kasus.str.extract(r"(\d+)")[0].astype(int).max() + 1
    baru = {"id_kasus": f"K{nomor:02d}", "kode_penyakit": kode_penyakit,
            "gejala": ";".join(sorted(himpunan)), "sumber": sumber}
    pd.concat([df, pd.DataFrame([baru])], ignore_index=True).to_csv(path, index=False)
    return True, f"Kasus {baru['id_kasus']} disimpan ke basis kasus."


# ----------------------------------------------------------------------
# 6. EVALUASI
# ----------------------------------------------------------------------
def evaluasi(uji_df, data, threshold=0.5):
    baris = []
    for u in uji_df.itertuples():
        h = diagnose(split_gejala(u.gejala), data, threshold)
        pred = h["top"]["kode_penyakit"] if h["top"] else "-"
        baris.append({"id_uji": u.id_uji, "gejala": u.gejala, "diagnosis_pakar": u.diagnosis_pakar,
                      "diagnosis_sistem": pred,
                      "similarity": h["top"]["similarity"] if h["top"] else 0.0,
                      "benar": pred == u.diagnosis_pakar})
    hasil = pd.DataFrame(baris)
    return hasil, float(hasil["benar"].mean()) if len(hasil) else 0.0
