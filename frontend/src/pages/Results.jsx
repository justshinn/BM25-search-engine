
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import articles from "../data/articles";
import "../styles/Results.css";

function Results() {
  const navigate = useNavigate();

  const [searchData, setSearchData] = useState(null);
  const [results, setResults] = useState([]);

  useEffect(() => {
    const savedSearch = sessionStorage.getItem("searchData");

    if (!savedSearch) {
      navigate("/");
      return;
    }

    const parsedSearch = JSON.parse(savedSearch);

    setSearchData(parsedSearch);

    const filteredArticles = articles.filter((article) => {
      if (parsedSearch.country === "Semua Negara") {
        return true;
      }

      return article.country === parsedSearch.country;
    });

    setResults(filteredArticles);
  }, [navigate]);

  function handleDetail(article) {
    sessionStorage.setItem(
      "selectedArticle",
      JSON.stringify(article)
    );

    navigate("/detail");
  }

  if (!searchData) {
    return <div className="loading">Memuat hasil pencarian...</div>;
  }

  return (
    <div className="results-page">

      <div className="results-header">
        <button onClick={() => navigate("/")}>
          ← Kembali
        </button>

        <h1>Hasil Pencarian</h1>

        <p>
          Kata kunci: <strong>{searchData.query}</strong>
        </p>

        <p>
          Metode: <strong>{searchData.method}</strong>
          {" | "}
          Negara: <strong>{searchData.country}</strong>
        </p>
      </div>

      <div className="results-container">

        <h2>
          {results.length} Artikel Ditemukan
        </h2>

        {results.length === 0 ? (
          <p className="empty-result">
            Tidak ada artikel yang ditemukan.
          </p>
        ) : (
          results.map((article) => (
            <div className="article-card" key={article.id}>

              <div className="article-info">
                <span>{article.source}</span>
                <span>{article.date}</span>
                <span>{article.country}</span>
              </div>

              <h3>{article.title}</h3>

              <p>{article.snippet}</p>

              <div className="article-footer">
                <span>
                  Score: {article.score.toFixed(3)}
                </span>

                <button onClick={() => handleDetail(article)}>
                  Baca Selengkapnya →
                </button>
              </div>

            </div>
          ))
        )}

      </div>
    </div>
  );
}

export default Results;
