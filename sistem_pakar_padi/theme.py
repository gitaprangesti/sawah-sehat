"""
theme.py - Tampilan "Sawah Sehat": CSS, hero, dan komponen HTML.

Palet diambil dari foto sawah: hijau padi, hijau hutan, kabut keemasan, cokelat tanah.
Ubah warna/font cukup di blok :root pada CSS di bawah.
"""
import base64
import html
from functools import lru_cache
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"
esc = html.escape

# Susunan kelompok gejala pada dua kolom halaman konsultasi
LAYOUT = [
    ["Daun & Pelepah", "Malai & Bulir", "Kondisi Tanaman"],
    ["Batang & Anakan", "Tanda di Sawah"],
]
BAGIAN_META = {
    "Daun & Pelepah": ("#6DAF2A", "Warna, bercak, dan bentuk daun"),
    "Batang & Anakan": ("#E3B03F", "Batang, anakan, dan isi batang"),
    "Malai & Bulir": ("#6B4E2E", "Bulir hampa dan leher malai"),
    "Kondisi Tanaman": ("#C0583A", "Layu, kerdil, kering, atau mati"),
    "Tanda di Sawah": ("#7C9A6B", "Lubang, jejak, larva, dan bau"),
}
STATUS_WARNA = {"ok": "#5E9E22", "mid": "#E3B03F", "low": "#C0583A"}


# ----------------------------------------------------------------------
# Gambar hero: pakai assets/hero.jpg bila ada, jika tidak pakai ilustrasi gradien
# ----------------------------------------------------------------------
@lru_cache(maxsize=1)
def hero_image_css():
    overlay = ("linear-gradient(90deg, rgba(251,246,230,.97) 0%, rgba(251,246,230,.90) 34%, "
               "rgba(251,246,230,.25) 70%, rgba(251,246,230,0) 100%)")
    foto = ASSETS / "hero.jpg"
    if foto.exists():
        b64 = base64.b64encode(foto.read_bytes()).decode()
        return f"{overlay}, url(data:image/jpeg;base64,{b64})"
    return overlay + ", linear-gradient(180deg,#F6E7A8 0%,#F1EDBE 42%,#A9D24E 42%,#5E9E22 100%)"


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400..800&family=Nunito+Sans:wght@400;600;700;800&display=swap');

:root{
  --g900:#1D3A19; --g800:#2A5220; --g700:#3B7020; --g500:#6DAF2A; --g300:#B9DB72; --g100:#E9F3CB;
  --cream:#FBF6E6; --cream2:#F3EBCB; --paper:#FFFDF4;
  --gold:#E3B03F; --gold-d:#A97A1E; --soil:#6B4E2E; --brick:#C0583A;
  --ink:#26331F; --ink-soft:#5B6B50; --line:rgba(29,58,25,.16);
  --display:'Fraunces','Georgia',serif;
  --body:'Nunito Sans','Segoe UI',system-ui,sans-serif;
}

/* ---------- dasar ---------- */
html, body, .stApp, [data-testid="stAppViewContainer"]{
  background-color:var(--cream) !important; color:var(--ink); font-family:var(--body);
}
.stApp{
  background-image:radial-gradient(rgba(107,78,46,.07) 1px, transparent 1px);
  background-size:22px 22px;
}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"]{display:none !important;}
header[data-testid="stHeader"]{background:transparent !important; height:0;}
.block-container{max-width:1080px; padding:1.2rem 1.4rem 3rem;}
p, li, label, span, div{font-family:var(--body);}
h1,h2,h3,h4{font-family:var(--display) !important; color:var(--g900) !important; letter-spacing:-.01em;}

/* ---------- hero ---------- */
.hero{
  position:relative; min-height:310px; display:flex; align-items:center; overflow:hidden;
  border:1.5px solid var(--line); border-radius:28px 28px 28px 6px;
  background-image:__HERO__; background-size:cover; background-position:center 64%;
}
.hero-in{padding:2rem 2.4rem; max-width:560px;}
.brand{display:flex; align-items:center; gap:.55rem; margin-bottom:.9rem;}
.brand b{font-family:var(--display); font-size:1.15rem; color:var(--g800); letter-spacing:.01em;}
.kicker{font-size:.74rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; color:var(--g700);}
.hero h1{font-size:3.3rem; line-height:1; margin:.3rem 0 .7rem; font-weight:700;}
.hero p{font-size:1.04rem; line-height:1.55; color:var(--ink-soft); margin:0 0 1rem; max-width:470px;}
.facts{display:flex; flex-wrap:wrap; gap:.45rem;}
.facts span{
  font-size:.8rem; font-weight:700; color:var(--g800); background:rgba(255,253,244,.9);
  border:1.5px solid var(--line); padding:.25rem .7rem; border-radius:999px;
}
@media (max-width:700px){
  .hero{background-position:72% 60%;}
  .hero-in{padding:1.4rem 1.2rem; background:rgba(251,246,230,.86);}
  .hero h1{font-size:2.5rem;}
}

/* ---------- judul bagian ---------- */
.sec{margin:2rem 0 1rem;}
.sec h2{font-size:1.75rem; margin:0 0 .15rem; font-weight:700;}
.sec p{color:var(--ink-soft); margin:0 0 .35rem; font-size:.98rem;}
.sec .wave{
  height:10px; width:120px;
  background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='30' height='10'><path d='M0 5 Q7.5 -1 15 5 T30 5' fill='none' stroke='%236DAF2A' stroke-width='2.4' stroke-linecap='round'/></svg>") repeat-x;
}

/* ---------- kelompok gejala ---------- */
[class*="st-key-grp_"]{
  background:var(--paper); border:1.5px solid var(--line); border-radius:22px 22px 22px 6px;
  padding:1rem 1.1rem 1.1rem; margin-bottom:1rem; gap:.4rem;
}
.grp-h{display:flex; align-items:center; gap:.55rem; margin-bottom:.1rem;}
.grp-h .dot{width:12px; height:12px; border-radius:50% 50% 50% 15%; flex:none;}
.grp-h b{font-family:var(--display); font-size:1.12rem; color:var(--g900);}
.grp-h .cnt{
  margin-left:auto; font-size:.74rem; font-weight:800; padding:.12rem .6rem; border-radius:999px;
  background:var(--cream2); color:var(--ink-soft);
}
.grp-h .cnt.on{background:var(--g500); color:#fff;}
.grp-sub{font-size:.85rem; color:var(--ink-soft); margin:0 0 .35rem 1.35rem;}

[data-testid="stCheckbox"]{
  background:#fff; border:1.5px solid var(--line); border-radius:14px;
  padding:.5rem .8rem; transition:border-color .15s, background .15s, transform .15s;
}
[data-testid="stCheckbox"]:hover{border-color:var(--g500); transform:translateY(-1px);}
[data-testid="stCheckbox"]:has(input:checked){background:var(--g100); border-color:var(--g500);}
[data-testid="stCheckbox"] label p{font-size:.93rem; line-height:1.35;}

/* ---------- ringkasan pilihan ---------- */
.pick{
  display:flex; flex-wrap:wrap; align-items:center; gap:.4rem;
  background:var(--paper); border:1.5px dashed rgba(29,58,25,.3); border-radius:18px;
  padding:.8rem 1rem; margin:.4rem 0 1rem;
}
.pick .lbl{font-size:.82rem; font-weight:800; color:var(--ink-soft); margin-right:.3rem;}
.pick .empty{font-size:.92rem; color:var(--ink-soft);}
.chip{
  font-size:.78rem; font-weight:800; color:var(--g900); background:var(--g100);
  border:1.5px solid var(--g300); padding:.1rem .6rem; border-radius:999px;
}

/* ---------- tombol ---------- */
button[data-testid="stBaseButton-primary"]{
  background:var(--g800) !important; border:1.5px solid var(--g800) !important;
  border-radius:999px !important; font-weight:800 !important; padding:.45rem 1.3rem;
}
button[data-testid="stBaseButton-primary"] p{color:var(--cream) !important;}
button[data-testid="stBaseButton-primary"]:hover{background:var(--g900) !important;}
button[data-testid="stBaseButton-secondary"]{
  background:transparent !important; border:1.5px solid var(--g800) !important;
  border-radius:999px !important; font-weight:800 !important; color:var(--g800) !important;
}
button[data-testid="stBaseButton-secondary"]:hover{background:var(--g100) !important;}
button[data-testid="stBaseButton-secondary"] p{color:var(--g800) !important;}

/* ---------- kartu diagnosis ---------- */
.dx{
  display:flex; gap:1.6rem; align-items:center; flex-wrap:wrap;
  background:var(--paper); border:1.5px solid var(--line); border-radius:26px 26px 26px 6px;
  padding:1.4rem 1.6rem; margin:.4rem 0 1.2rem; position:relative; overflow:hidden;
}
.dx::after{
  content:""; position:absolute; left:0; top:0; bottom:0; width:8px; background:var(--g500);
}
.dx-mid::after{background:var(--gold);} .dx-low::after{background:var(--brick);}
.ring-t{font-family:var(--display); font-size:30px; font-weight:700; fill:var(--g900);}
.dx-body{flex:1; min-width:260px;}
.badge{
  display:inline-block; font-size:.72rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase;
  padding:.18rem .7rem; border-radius:999px;
}
.b-ok{background:var(--g100); color:var(--g800);}
.b-mid{background:#FBEDC4; color:var(--gold-d);}
.b-low{background:#F6DDD3; color:#9B3F22;}
.dx-name{font-family:var(--display); font-size:2.1rem; font-weight:700; color:var(--g900); line-height:1.1; margin:.45rem 0 .25rem;}
.dx-meta{font-size:.85rem; font-weight:700; color:var(--ink-soft);}
.dx-desc{margin:.6rem 0 0; line-height:1.55; color:var(--ink);}

.card{background:var(--paper); border:1.5px solid var(--line); border-radius:20px 20px 20px 6px; padding:1.1rem 1.3rem;}
.card h4{font-size:1.15rem; margin:0 0 .7rem;}
.steps{counter-reset:s; list-style:none; padding:0; margin:0;}
.steps li{
  counter-increment:s; position:relative; padding:.35rem 0 .35rem 2.5rem; line-height:1.5; font-size:.96rem;
}
.steps li::before{
  content:counter(s); position:absolute; left:0; top:.3rem; width:1.75rem; height:1.75rem; border-radius:50%;
  background:var(--g800); color:var(--cream); font-weight:800; font-size:.85rem;
  display:grid; place-items:center;
}
.note{font-size:.82rem; color:var(--ink-soft); margin-top:.7rem;}

.bar-row{display:grid; grid-template-columns:minmax(120px,1.2fr) 2fr 3rem; gap:.7rem; align-items:center; margin:.5rem 0;}
.bar-name{font-size:.9rem; font-weight:700; line-height:1.2;}
.bar-name small{display:block; font-weight:600; color:var(--ink-soft);}
.bar{height:12px; background:var(--cream2); border-radius:999px; overflow:hidden;}
.bar i{display:block; height:100%; border-radius:999px; background:var(--g300);}
.bar-row.top .bar i{background:var(--g500);}
.bar-val{font-weight:800; font-size:.9rem; text-align:right; font-variant-numeric:tabular-nums;}

/* ---------- kotak statistik & alur ---------- */
.tiles{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:.8rem; margin:.6rem 0 1rem;}
.tile{background:var(--paper); border:1.5px solid var(--line); border-radius:18px; padding:.9rem 1.1rem;}
.tile small{font-size:.78rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--ink-soft);}
.tile div{font-family:var(--display); font-size:2rem; font-weight:700; color:var(--g900);}
.flow{display:grid; grid-template-columns:repeat(auto-fit,minmax(185px,1fr)); gap:.9rem; margin:.6rem 0 1.2rem;}
.flow .st{background:var(--paper); border:1.5px solid var(--line); border-radius:20px 20px 20px 6px; padding:1rem 1.1rem;}
.flow .n{
  width:2rem; height:2rem; border-radius:50%; background:var(--gold); color:var(--g900);
  font-family:var(--display); font-weight:800; display:grid; place-items:center; margin-bottom:.5rem;
}
.flow h4{font-size:1.05rem; margin:0 0 .3rem;}
.flow p{font-size:.9rem; line-height:1.5; margin:0; color:var(--ink-soft);}

.foot{margin-top:2.5rem; padding-top:1rem; border-top:1.5px solid var(--line); font-size:.85rem; color:var(--ink-soft);}

/* ---------- komponen bawaan Streamlit ---------- */
button[role="tab"] p{font-weight:700; font-size:.98rem;}
[data-testid="stExpander"] details{border:1.5px solid var(--line) !important; border-radius:16px !important; background:var(--paper);}
[data-testid="stAlert"]{border-radius:14px;}
[data-testid="stSegmentedControl"] button p{font-weight:700;}
"""


def css():
    return "<style>" + CSS.replace("__HERO__", hero_image_css()) + "</style>"


# ----------------------------------------------------------------------
# Komponen HTML (dipakai dengan st.html)
# ----------------------------------------------------------------------
LOGO = (
    '<svg width="34" height="34" viewBox="0 0 40 40" aria-hidden="true">'
    '<path d="M17 38 C18 26 20 16 25 4" stroke="#2A5220" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
    '<ellipse cx="26" cy="8" rx="2.3" ry="4.4" transform="rotate(18 26 8)" fill="#E3B03F"/>'
    '<ellipse cx="22" cy="13" rx="2.3" ry="4.4" transform="rotate(-24 22 13)" fill="#E3B03F"/>'
    '<ellipse cx="27" cy="15" rx="2.3" ry="4.4" transform="rotate(28 27 15)" fill="#E3B03F"/>'
    '<ellipse cx="21" cy="21" rx="2.3" ry="4.2" transform="rotate(-26 21 21)" fill="#E3B03F"/>'
    '<path d="M17.5 34 C9 33 5 27 4 21 C12 22 17 26 17.5 34Z" fill="#6DAF2A"/>'
    '</svg>'
)


def hero(n_penyakit, n_gejala):
    return (
        '<div class="hero"><div class="hero-in">'
        f'<div class="brand">{LOGO}<b>Sawah Sehat</b></div>'
        '<div class="kicker">Sistem pakar penyakit padi</div>'
        '<h1>Kenali sakitnya padi, sebelum menyebar.</h1>'
        '<p>Pilih gejala yang terlihat di sawah, lalu sistem mencocokkannya dengan aturan pakar '
        'dan kasus-kasus sebelumnya.</p>'
        f'<div class="facts"><span>{n_penyakit} penyakit &amp; hama</span>'
        f'<span>{n_gejala} gejala</span><span>Forward Chaining + CBR</span></div>'
        '</div></div>'
    )


def section(judul, sub=None):
    s = f"<p>{esc(sub)}</p>" if sub else ""
    return f'<div class="sec"><h2>{esc(judul)}</h2>{s}<div class="wave"></div></div>'


def group_header(nama, dipilih, total):
    warna, hint = BAGIAN_META.get(nama, ("#7C9A6B", ""))
    on = " on" if dipilih else ""
    cnt = f"{dipilih} dipilih" if dipilih else f"{total} gejala"
    sub = f'<div class="grp-sub">{esc(hint)}</div>' if hint else ""
    return (f'<div class="grp-h"><span class="dot" style="background:{warna}"></span>'
            f'<b>{esc(nama)}</b><span class="cnt{on}">{cnt}</span></div>{sub}')


def ringkasan(pilihan, nama_gejala):
    if not pilihan:
        isi = '<span class="empty">Belum ada gejala yang dipilih.</span>'
    else:
        isi = "".join(f'<span class="chip" title="{esc(nama_gejala.get(g, g))}">{esc(g)}</span>' for g in pilihan)
    return f'<div class="pick"><span class="lbl">Gejala terpilih ({len(pilihan)})</span>{isi}</div>'


def diagnosis_card(top, label, key, deskripsi):
    pct = round(top["similarity"] * 100)
    warna = STATUS_WARNA[key]
    d = 301.6 * top["similarity"]
    ring = (
        '<svg viewBox="0 0 120 120" width="120" height="120" aria-hidden="true">'
        '<circle cx="60" cy="60" r="48" fill="none" stroke="#EFE6C4" stroke-width="12"/>'
        f'<circle cx="60" cy="60" r="48" fill="none" stroke="{warna}" stroke-width="12" stroke-linecap="round" '
        f'stroke-dasharray="{d:.1f} 301.6" transform="rotate(-90 60 60)"/>'
        f'<text x="60" y="70" text-anchor="middle" class="ring-t">{pct}%</text></svg>'
    )
    return (
        f'<div class="dx dx-{key}">{ring}<div class="dx-body">'
        f'<span class="badge b-{key}">{esc(label)}</span>'
        f'<div class="dx-name">{esc(top["nama_penyakit"])}</div>'
        f'<div class="dx-meta">Kode {esc(top["kode_penyakit"])} &middot; paling mirip kasus {esc(top["id_kasus"])} '
        f'&middot; {esc(top["jumlah_cocok"])} gejala cocok</div>'
        f'<p class="dx-desc">{esc(deskripsi)}</p></div></div>'
    )


def penanganan(solusi):
    langkah = [s.strip().rstrip(".") for s in str(solusi).split(";") if s.strip()]
    li = "".join(f"<li>{esc(s[0].upper() + s[1:])}.</li>" for s in langkah)
    return (f'<div class="card"><h4>Langkah penanganan</h4><ol class="steps">{li}</ol>'
            '<div class="note">Panduan umum. Untuk jenis dan dosis pestisida, tanyakan ke penyuluh pertanian setempat.</div></div>')


def rank_bars(ranking, maks=5):
    baris = []
    tampil = ranking[ranking.similarity > 0].head(maks)
    for i, r in enumerate(tampil.itertuples()):
        pct = round(r.similarity * 100)
        top = " top" if i == 0 else ""
        baris.append(
            f'<div class="bar-row{top}"><div class="bar-name">{esc(r.nama_penyakit)}<small>{esc(r.id_kasus)}</small></div>'
            f'<div class="bar"><i style="width:{pct}%"></i></div><div class="bar-val">{pct}%</div></div>'
        )
    return f'<div class="card"><h4>Kandidat lain</h4>{"".join(baris)}</div>'


def tiles(daftar):
    isi = "".join(f"<div class='tile'><small>{esc(k)}</small><div>{esc(str(v))}</div></div>" for k, v in daftar)
    return f'<div class="tiles">{isi}</div>'


def alur():
    langkah = [
        ("Gejala jadi fakta", "Gejala yang Anda pilih masuk sebagai fakta awal sistem."),
        ("Forward Chaining", "Aturan IF-THEN dicek. Aturan menyala bila semua premisnya terpenuhi."),
        ("Retrieve", "Kemiripan gejala dihitung ke setiap kasus: jumlah bobot cocok dibagi total bobot."),
        ("Reuse", "Kasus paling mirip dipakai sebagai diagnosis. Aturan FC jadi penguat."),
        ("Revise & Retain", "Anda memastikan hasilnya. Kasus yang sudah benar disimpan untuk dipakai lagi."),
    ]
    isi = "".join(f'<div class="st"><div class="n">{i}</div><h4>{esc(j)}</h4><p>{esc(d)}</p></div>'
                  for i, (j, d) in enumerate(langkah, 1))
    return f'<div class="flow">{isi}</div>'


def footer():
    return ('<div class="foot">Sawah Sehat &middot; sistem pakar sederhana (Forward Chaining + Case Based Reasoning). '
            'Hasilnya alat bantu, bukan pengganti penyuluh atau pakar pertanian.</div>')
