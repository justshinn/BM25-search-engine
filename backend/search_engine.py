import json
import math
import re
from collections import Counter
from pathlib import Path

import pandas as pd

from preprocessing import (
    preprocess_pipeline, case_folding, tokenize, filtering,
    stopword_removal, stemming, stopwords_final,
)

DATA_DIR = Path(__file__).parent / "data"

df_docs = pd.read_csv(DATA_DIR / "corpus_processed.csv", encoding="utf-8-sig").fillna("")
with open(DATA_DIR / "inverted_index_tf.json", encoding="utf-8") as f:
    _data = json.load(f)

inv_index = _data["index"]
N = _data["meta"]["N"]
avgdl = _data["meta"]["avgdl"]
doc_lengths = _data["meta"]["doc_length"]

#pemenataan negara
COUNTRY_MAP = {
    "Indonesia": {
        "alias": [r"\bindonesia\b"],
        "expand": ["merah putih", "pbsi", "pelatnas", "jonatan christie", "alwi farhan", "fajar alfian",
                   "fikri", "amri syahnawi", "nita violina", "rachel allessya", "febi setianingrum",
                   "apriyani rahayu", "thalita", "ana", "trias", "putri kusuma wardani", "leo rolly carnando",
                   "daniel marthin", "zaki ubaidillah", "raymond", "nikolaus", "marwan", "faza", "aisyah",
                   "rehan", "gloria", "jakarta"],
    },
    "China": {
        "alias": [r"\bchina\b", r"\btiongkok\b", r"\bcina\b"],
        "expand": ["tiongkok", "shi yuqi", "chen yu fei", "wang zhi yi", "han yue", "liang weikeng",
                   "wang chang", "zhang shu xian", "li shi feng", "huang dong ping", "wei ya xin",
                   "tan ning", "liu sheng shu", "feng yan zhe", "luo xu min", "jia yi fan"],
    },
    "Jepang": {
        "alias": [r"\bjepang\b", r"\bjapan\b"],
        "expand": ["akane yamaguchi", "kodai naraoka", "yuki fukushima", "mayu matsumoto", "tomoka miyazaki",
                   "takuro hoki", "yugo kobayashi", "rin iwanaga", "kie nakanishi", "yudai okimoto",
                   "rui hirokami", "sayaka hobara", "sumire nakade", "miyu takahashi", "tokyo", "kumamoto"],
    },
    "Korea Selatan": {
        "alias": [r"\bkorea selatan\b", r"\bkorsel\b", r"\bkorea\b"],
        "expand": ["korsel", "kim won ho", "seo seung jae", "an se young", "lee so hee", "baek ha na",
                   "kim hye jeong", "kong hee yong", "ki dong ju", "jeong na eun"],
    },
    "Malaysia": {
        "alias": [r"\bmalaysia\b"],
        "expand": ["aaron chia", "soh wooi yik", "pearly tan", "thinaah muralitharan", "goh sze fei",
                   "nur izzuddin", "tee kai wun", "toh ee wei", "chong"],
    },
    "Denmark": {
        "alias": [r"\bdenmark\b", r"\bdenmark\b"],
        "expand": ["rasmus gemke", "line christophersen", "anders antonsen", "mathias christiansen",
                   "alexandra boje"],
    },
    "India": {
        "alias": [r"\bindia\b"],
        "expand": ["ayush shetty", "satwiksairaj rankireddy", "chirag shetty", "sindhu", "arjun"],
    },
    "Thailand": {
        "alias": [r"\bthailand\b"],
        "expand": ["kunlavut vitidsarn", "dechapol puavaranukroh", "supissara paewsampran",
                   "ratchanok intanon", "pornpawee chochuwong"],
    },
    "Taiwan": {
        "alias": [r"\btaiwan\b", r"\bchinese taipei\b", r"\btaipei\b"],
        "expand": ["chinese taipei", "chou tien chen", "hsuan", "hu ling fang", "nicole chan"],
    },
    "Prancis": {
        "alias": [r"\bprancis\b", r"\bperancis\b", r"\bfrance\b"],
        "expand": ["alex lanier", "brice leverdez", "christo popov", "thom gicquel", "delphine delrue"],
    },
}
SEMUA_NEGARA = "Semua Negara"
DAFTAR_NEGARA = [SEMUA_NEGARA] + list(COUNTRY_MAP.keys())

ABAIKAN_NAMA_TURNAMEN = True
POLA_TURNAMEN = r"\b(?:china|japan|korea|denmark|india|australia|thailand|malaysia|indonesia|taipei|french|hong kong)\s+(?:open|masters|super)\b"
MIN_MENTION_BADAN = 2
MIN_BUKTI_FRASA = 2

def hitung_mention(teks, negara):
    return sum(len(re.findall(p, teks)) for p in COUNTRY_MAP[negara]["alias"])

def tandai_negara(judul, teks):
    judul, teks = str(judul).lower(), str(teks).lower()
    if ABAIKAN_NAMA_TURNAMEN:
        judul = re.sub(POLA_TURNAMEN, " ", judul)
        teks = re.sub(POLA_TURNAMEN, " ", teks)
    semua = judul + " " + teks
    hasil = []
    for negara, cfg in COUNTRY_MAP.items():
        bukti = {p for p in cfg["expand"] if len(p) >= 4 and re.search(rf"\b{re.escape(p)}\b", semua)}
        if (hitung_mention(judul, negara) >= 1
                or hitung_mention(teks, negara) >= MIN_MENTION_BADAN
                or len(bukti) >= MIN_BUKTI_FRASA):
            hasil.append(negara)
    return hasil

df_docs["negara"] = [tandai_negara(j, t) for j, t in zip(df_docs["title"], df_docs["text"])]
doc_negara = dict(zip(df_docs["doc_id"], df_docs["negara"]))
negara_docs = {n: {d for d, lst in doc_negara.items() if n in lst} for n in COUNTRY_MAP}

# doc_lookup dibuat SETELAH kolom "negara" ada
doc_lookup = df_docs.set_index("doc_id").to_dict(orient="index")

def get_allowed_doc_ids(negara):
    """None = tanpa filter. Selain itu: set doc_id yang terkait negara terpilih."""
    if negara is None or negara == SEMUA_NEGARA:
        return None
    if negara not in COUNTRY_MAP:
        raise ValueError(f"Negara '{negara}' tidak ada di COUNTRY_MAP")
    return negara_docs[negara]

def deteksi_negara(query):
    """Negara yang disebut langsung di teks query."""
    q = str(query).lower()
    return [n for n in COUNTRY_MAP if hitung_mention(q, n) > 0]

#query expansion
SINONIM_GRUP = [
    ["menang", "bekuk", "bungkam", "takluk", "tekuk", "tundukkan"],
    ["kalah", "tumbang", "gugur", "kandas", "tersingkir", "terhenti"],
    ["juara", "kampiun", "titel", "gelar"],
    ["lawan", "hadapi", "jumpa", "duel", "bentrok", "bertemu"],
    ["raih", "rebut", "sabet", "kantongi", "bawa pulang"],
    ["gagal", "nirgelar", "paceklik"],
    ["wakil", "pemain", "atlet", "pebulu tangkis"],
    ["pertandingan", "laga", "partai", "match", "pertarungan"],
    ["lolos", "melaju", "tembus", "melangkah"],
    ["bidik", "incar", "target", "tatap"],
    ["sengit", "ketat", "seru", "dramatis"],
    ["penampilan", "performa"],
    ["pelatih", "coach"],
    ["peringkat", "ranking"],
    ["medali", "podium"],
    ["bangkit", "comeback"],
    ["turnamen", "ajang"],
    ["jojo", "jonatan"],
]

# "Kejuaraan Dunia" (nama ajang) di-stem menjadi "juara", jangan memicu ekspansi grup "juara"
PEMICU_DIABAIKAN = {"kejuaraan"}

BOBOT_SINONIM = 0.4     # bobot kata sinonim (kata asli query = 1.0)
MAKS_DF_SINONIM = 0.6   # sinonim yang muncul di >60% dokumen terlalu umum, tidak dipakai

def _stem_kata(teks):
    """Teks -> token hasil preprocessing yang sama dengan korpus (tanpa clean_noise)."""
    t = filtering(tokenize(case_folding(teks)))
    return stemming(stopword_removal(t, stopwords_final))

SINONIM_STEM = []
for _grup in SINONIM_GRUP:
    _anggota = []
    for _m in _grup:
        _st = tuple(dict.fromkeys(_stem_kata(_m)))
        if _st:
            _anggota.append((_m, _st))
    if len(_anggota) >= 2:
        SINONIM_STEM.append(_anggota)

def expand_query(query, query_tokens, bobot_ekspansi=BOBOT_SINONIM, rasio_maks=1.0):
    """Mengembalikan (query_weights, term_ekspansi, detail).
    Term asli berbobot sesuai frekuensinya; sinonim berbobot kecil, dan total bobot
    ekspansi dibatasi <= rasio_maks x total bobot query asli."""
    weights = {t: float(c) for t, c in Counter(query_tokens).items()}
    total_asli = sum(weights.values())

    stem_pemicu = set()
    for w in filtering(tokenize(case_folding(query))):
        if w not in PEMICU_DIABAIKAN:
            stem_pemicu.update(_stem_kata(w))

    kandidat, detail = [], []
    for grup in SINONIM_STEM:
        pemicu = [m for m, st in grup if set(st) <= stem_pemicu]
        if not pemicu:
            continue
        baru = []
        for m, st in grup:
            if set(st) <= stem_pemicu:      # anggota ini sudah ada di query
                continue
            for t in st:
                if (t in inv_index and inv_index[t]["df"] <= MAKS_DF_SINONIM * N
                        and t not in weights and t not in kandidat):
                    kandidat.append(t)
                    baru.append(t)
        if baru:
            detail.append({"pemicu": pemicu, "tambahan": baru})

    if kandidat:
        bobot = min(bobot_ekspansi, rasio_maks * total_asli / len(kandidat))
        for t in kandidat:
            weights[t] = bobot
    return weights, kandidat, detail

#BM25 berbobot
def hitung_bm25_weighted(query_weights, k1=1.5, b=0.75, allowed_doc_ids=None):
    scores = {}
    for term, w in query_weights.items():
        if term not in inv_index:
            continue
        df_term = inv_index[term]["df"]
        idf = math.log(((N - df_term + 0.5) / (df_term + 0.5)) + 1.0)
        for doc_id, tf in inv_index[term]["postings"].items():
            if allowed_doc_ids is not None and doc_id not in allowed_doc_ids:
                continue
            dl = doc_lengths[doc_id]
            skor_term = idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (dl / avgdl)))
            scores[doc_id] = scores.get(doc_id, 0.0) + w * skor_term
    return scores

def search_expanded(query, method="bm25", negara=SEMUA_NEGARA, expand=True,
                    top_k=10, bobot_ekspansi=BOBOT_SINONIM):
    if method.lower() != "bm25":
        raise ValueError("Metode harus 'bm25'")

    q_tokens = preprocess_pipeline(query, "")
    negara_aktif = list(dict.fromkeys(([negara] if negara in COUNTRY_MAP else []) + deteksi_negara(query)))
    allowed = get_allowed_doc_ids(negara)

    # Query kosong tapi negara dipilih (mode "jelajah negara"): pakai nama negara sebagai query
    if not q_tokens and negara_aktif:
        for n in negara_aktif:
            for p in COUNTRY_MAP[n]["alias"]:
                q_tokens += preprocess_pipeline(re.sub(r"\\b", "", p), "")
    if not q_tokens:
        return {"query_tokens": [], "negara_aktif": negara_aktif, "term_ekspansi": [],
                "detail_ekspansi": [], "results": []}

    if expand:
        weights, term_ekspansi, detail_ekspansi = expand_query(query, q_tokens, bobot_ekspansi)
    else:
        weights = {t: float(c) for t, c in Counter(q_tokens).items()}
        term_ekspansi, detail_ekspansi = [], []

    raw = hitung_bm25_weighted(weights, allowed_doc_ids=allowed)

    results = []
    urut = sorted(raw.items(), key=lambda x: x[1], reverse=True)[:top_k]
    for rank, (doc_id, score) in enumerate(urut, start=1):
        m = doc_lookup[doc_id]
        teks = str(m.get("text", ""))
        results.append({
            "rank": rank,
            "doc_id": doc_id,
            "title": m.get("title", ""),
            "snippet": teks[:200].strip() + ("..." if len(teks) > 200 else ""),
            "score": round(score, 4),
            "media": m.get("media_clean", m.get("media", "")),
            "date": m.get("date", ""),
            "url": m.get("url", ""),
            "negara": doc_negara.get(doc_id, []),
        })

    return {"query_tokens": q_tokens, "negara_aktif": negara_aktif,
            "term_ekspansi": term_ekspansi, "detail_ekspansi": detail_ekspansi,
            "results": results}


if __name__ == "__main__":
    # Tes cepat, hasilnya harus sama dengan notebook
    print("Dokumen per negara:", {n: len(s) for n, s in negara_docs.items()})
    print("Dokumen tanpa negara:", sum(1 for v in doc_negara.values() if not v))

    out = search_expanded("Jonatan Christie kalah dari wakil Denmark", expand=True)
    for r in out["results"][:3]:
        print(r["rank"], r["doc_id"], r["score"], r["title"][:60])

    out = search_expanded("juara dunia", negara="Jepang", expand=True)
    for r in out["results"][:1]:
        print(r["rank"], r["doc_id"], r["score"], r["title"][:60])
