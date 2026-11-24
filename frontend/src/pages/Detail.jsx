import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import "../styles/Detail.css";

function Detail() {
  const navigate = useNavigate();

  const [article, setArticle] = useState(null);
  const [score, setScore] = useState(null);
  const [searchData, setSearchData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const savedArticle = sessionStorage.getItem("selectedArticle");
    const savedSearch = sessionStorage.getItem("searchData");

    if (!savedArticle || !savedSearch) {
      navigate("/");
      return;
    }

    const selected = JSON.parse(savedArticle);
    setSearchData(JSON.parse(savedSearch));
    setScore(selected.score);

    const controller = new AbortController();

    fetch(`/api/article/${selected.doc_id}`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error("Artikel tidak ditemukan.");
        return res.json();
      })
      .then(setArticle)
      .catch((err) => {
        if (err.name === "AbortError") return;
        setError(
          err.message === "Failed to fetch"
            ? "Gagal terhubung ke server. Pastikan backend sudah berjalan."
            : err.message
        );
      });

    return () => controller.abort();
  }, [navigate]);

  if (error) {
    return (
      <div className="detail-page">
        <div className="detail-container">
          <button
            className="back-button"
            onClick={() => navigate("/results")}
          >
            ← Kembali ke Hasil
          </button>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!article || !searchData) {
    return <div className="loading">Memuat artikel...</div>;
  }

  const paragraphs = article.text
    .split(/\n+/)
    .map((p) => p.trim())
    .filter(Boolean);

  return (
    <div className="detail-page">

      <div className="detail-container">

        <button
          className="back-button"
          onClick={() => navigate("/results")}
        >
          ← Kembali ke Hasil
        </button>

        <div className="detail-meta">
          <span>{article.media}</span>
          <span>{article.date}</span>
          <span>{article.negara.join(", ")}</span>
        </div>

        <h1>{article.title}</h1>

        <div className="detail-score">
          Relevance Score: {score.toFixed(3)}
        </div>

        <div className="detail-content">
          {paragraphs.map((p, i) => (
            <p key={i}>{p}</p>
          ))}
        </div>

        {article.url && (
          <p>
            <a href={article.url} target="_blank" rel="noreferrer">
              Baca di sumber asli →
            </a>
          </p>
        )}

        <div className="search-metadata">
          <h3>Informasi Pencarian</h3>

          <p>Kata kunci: {searchData.query}</p>

          <p>Metode: {searchData.method}</p>

          <p>Filter negara: {searchData.country}</p>
        </div>

      </div>
    </div>
  );
}

export default Detail;