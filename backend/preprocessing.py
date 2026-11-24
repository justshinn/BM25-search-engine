import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

PERTAHANKAN_NEGASI = True
KATA_NEGASI = {"tidak", "bukan", "jangan", "tanpa", "belum"}

stopwords_final = set(StopWordRemoverFactory().get_stop_words())
if PERTAHANKAN_NEGASI:
    stopwords_final -= KATA_NEGASI

stemmer = StemmerFactory().create_stemmer()

#case folding
def case_folding(text: str) -> str:
    return text.lower()

#normalisasi media
def normalisasi_media(media: str) -> str:
    """Menyeragamkan nama media. Di data ada 'idntimes', 'idntimes.com', 'kompas',
    'Antara', 'antaranews.com' -> dijadikan 3 nama saja."""
    m = str(media).lower().replace(" ", "")
    if "idntimes" in m:
        return "IDN Times"
    if "kompas" in m:
        return "Kompas"
    if "antara" in m:
        return "Antara"
    return str(media)

#clean noise & clean noise tambahan
def clean_noise(text: str, media: str) -> str:
    text = text.replace("\xa0", " ")

    text = re.sub(r"baca juga\s*:?\s*(?:\S+\s+){0,20}", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"^[^,\n]+,\s*idn times\s*[-–—]\s*", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\bkompas\.com\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"lihat foto.*?\(dok\.[^)]*\)", " ", text, flags=re.IGNORECASE)

    # Cleaning khusus IDN Times
    # (FIX: sebelumnya membandingkan dengan "idn times", padahal nilai kolom media di data
    #  adalah "idntimes" / "idntimes.com", sehingga blok ini tidak pernah jalan.)
    if normalisasi_media(media) == "IDN Times":
        text = re.sub(r"\(idn times/[^)]*\)", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"\(dok\.[^)]*\)", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"\(instagram\.com/[^)]*\)", " ", text, flags=re.IGNORECASE)

    # Menghapus informasi redaksi ANTARA
    text = re.sub(r"\b(pewarta|editor|copyright)\s*:?.*", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()

    return text

def clean_noise_tambahan(text: str) -> str:
    # Menghapus caption foto Kompas yang diawali "lihat foto"
    # sampai sumber foto yang ditulis dalam tanda kurung.
    text = re.sub(r"lihat foto.*?\)\s*", " ", text)

    # Merapikan spasi setelah penghapusan
    text = re.sub(r"\s+", " ", text).strip()
    return text

#tokenization
def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text)

#filtering
def filtering(tokens: list[str]) -> list[str]:
    return [token for token in tokens if token.isalpha()]

#stopword removal
def stopword_removal(tokens: list[str], stopwords: set[str]) -> list[str]:
    return [t for t in tokens if t.lower() not in stopwords]

#stemming
def stemming(tokens: list[str]) -> list[str]:
    return [stemmer.stem(t) for t in tokens]

#pipeline lengkap
def preprocess_pipeline(raw_text: str, media: str) -> list[str]:
    text = case_folding(raw_text)
    text = clean_noise(text, media)
    text = clean_noise_tambahan(text)
    tokens = tokenize(text)
    tokens = filtering(tokens)
    tokens = stopword_removal(tokens, stopwords_final)
    tokens = stemming(tokens)
    return tokens


if __name__ == "__main__":
    # Tes cepat, hasilnya harus sama dengan notebook
    print(preprocess_pipeline("Jonatan Christie kalah dari wakil Denmark", ""))
    # -> ['jonatan', 'christie', 'kalah', 'wakil', 'denmark']
    print(preprocess_pipeline("Kejuaraan Dunia", ""))
    # -> ['juara', 'dunia']