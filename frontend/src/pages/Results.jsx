import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Results.css";

function Results() {
  const navigate = useNavigate();

  const [searchData, setSearchData] = useState(null);
  const [results, setResults] = useState([]);
  const [expansion, setExpansion] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const savedSearch = sessionStorage.getItem("searchData");
    if (!savedSearch) {
      navigate("/");
      return;
    }

    const parsed = JSON.parse(savedSearch);
    setSearchData(parsed);
    setLoading(true);
    setError("");

    const controller = new AbortController();

    fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: parsed.query,
        method: parsed.method,
        country: parsed.country,
        top_k: 10,
      }),
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error("Server error");
        return res.json();
      })
      .then((data) => {
        setResults(data.results);
        setExpansion(data.term_ekspansi || []);
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(
            "Gagal terhubung ke server pencarian. Pastikan backend sudah berjalan."
          );
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [navigate]);

  function handleDetail(article) {
    sessionStorage.setItem("selectedArticle", JSON.stringify(article));
    navigate("/detail");
  }

  if (!searchData) {
    return <div className="loading">Memuat hasil pencarian...</div>;
  }

  return (
    <div className="results-page">
      <div className="results-header">
        <button onClick={() => navigate("/")}>← Kembali</button>

        <h1>Hasil Pencarian</h1>

        <p>
          Kata kunci: <strong>{searchData.query}</strong>
        </p>

        <p>
          Metode: <strong>{searchData.method}</strong>
          {" | "}
          Negara: <strong>{searchData.country}</strong>
        </p>

        {expansion.length > 0 && (
          <p>Pencarian diperluas dengan: {expansion.slice(0, 8).join(", ")}</p>
        )}
      </div>

      <div className="results-container">
        {loading && <p className="loading">Mencari...</p>}
        {error && <p className="empty-result">{error}</p>}

        {!loading && !error && (
          <>
            <h2>{results.length} Artikel Ditemukan</h2>

            {results.length === 0 ? (
              <p className="empty-result">
                Tidak ada artikel yang ditemukan.
              </p>
            ) : (
              results.map((article) => (
                <div className="article-card" key={article.doc_id}>
                  <div className="article-info">
                    <span>{article.media}</span>
                    <span>{article.date}</span>
                    <span>{article.negara.slice(0, 3).join(", ")}</span>
                  </div>

                  <h3>{article.title}</h3>

                  <p>{article.snippet}</p>

                  <div className="article-footer">
                    <span>Score: {article.score.toFixed(3)}</span>

                    <button onClick={() => handleDetail(article)}>
                      Baca Selengkapnya →
                    </button>
                  </div>
                </div>
              ))
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default Results;