
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import "../styles/Detail.css";

function Detail() {
  const navigate = useNavigate();

  const [article, setArticle] = useState(null);
  const [searchData, setSearchData] = useState(null);

  useEffect(() => {
    const savedArticle = sessionStorage.getItem("selectedArticle");
    const savedSearch = sessionStorage.getItem("searchData");

    if (!savedArticle || !savedSearch) {
      navigate("/");
      return;
    }

    setArticle(JSON.parse(savedArticle));
    setSearchData(JSON.parse(savedSearch));
  }, [navigate]);

  if (!article || !searchData) {
    return <div className="loading">Memuat artikel...</div>;
  }

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
          <span>{article.source}</span>
          <span>{article.date}</span>
          <span>{article.country}</span>
        </div>

        <h1>{article.title}</h1>

        <div className="detail-score">
          Relevance Score: {article.score.toFixed(3)}
        </div>

        <div className="detail-content">
          <p>{article.content}</p>
        </div>

        <div className="search-metadata">
          <h3>Informasi Pencarian</h3>

          <p>
            Kata kunci: {searchData.query}
          </p>

          <p>
            Metode: {searchData.method}
          </p>

          <p>
            Filter negara: {searchData.country}
          </p>
        </div>

      </div>
    </div>
  );
}

export default Detail;
