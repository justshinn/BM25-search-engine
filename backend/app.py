from flask import Flask, request, jsonify
from flask_cors import CORS

import search_engine as se

app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health():
    return {"status": "ok", "documents": se.N}


@app.get("/api/countries")
def countries():
    return jsonify(se.DAFTAR_NEGARA)


@app.post("/api/search")
def search():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()
    method = data.get("method", "BM25")
    country = data.get("country", se.SEMUA_NEGARA)

    try:
        top_k = int(data.get("top_k", 10))
    except (TypeError, ValueError):
        return {"error": "top_k harus berupa angka"}, 400
    top_k = max(1, min(top_k, 50))

    if not query:
        return {"error": "Query tidak boleh kosong"}, 400
    if country not in se.DAFTAR_NEGARA:
        return {"error": f"Negara tidak dikenal: {country}"}, 400
    if method not in ("BM25", "BM25+QE"):
        return {"error": f"Metode tidak dikenal: {method}"}, 400

    out = se.search_expanded(
        query,
        method="bm25",
        negara=country,
        expand=(method == "BM25+QE"),
        top_k=top_k,
    )
    return jsonify(out)


@app.get("/api/article/<doc_id>")
def article(doc_id):
    m = se.doc_lookup.get(doc_id)
    if m is None:
        return {"error": "Artikel tidak ditemukan"}, 404
    return jsonify({
        "doc_id": doc_id,
        "title": m["title"],
        "date": m["date"],
        "media": m["media_clean"],
        "author": m["author"],
        "url": m["url"],
        "text": m["text"],
        "negara": m["negara"],
    })


if __name__ == "__main__":
    # debug=False supaya model tidak dimuat dua kali oleh reloader Flask
    app.run(port=5000, debug=False)