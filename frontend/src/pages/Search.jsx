
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Search.css";

function Search() {
  const navigate = useNavigate();

  const [query, setQuery] = useState("");
  const [method, setMethod] = useState("BM25");
  const [country, setCountry] = useState("Semua Negara");

  const countries = [
    "Semua Negara",
    "Indonesia",
    "China",
    "Jepang",
    "Korea Selatan",
    "Malaysia",
    "Denmark",
    "India",
    "Thailand",
    "Taiwan",
    "Prancis"
  ];

  function handleSearch(e) {
    e.preventDefault();

    if (!query.trim()) {
      alert("Masukkan kata kunci pencarian terlebih dahulu.");
      return;
    }

    const searchData = {
      query: query.trim(),
      method,
      country
    };

    sessionStorage.setItem("searchData", JSON.stringify(searchData));

    navigate("/results");
  }

  return (
    <div className="search-page">
      <div className="search-container">

        <h1>Badminton News Search Engine</h1>

        <p className="search-subtitle">
          Temukan berita badminton berdasarkan kata kunci yang kamu cari.
        </p>

        <form onSubmit={handleSearch}>

          <input
            type="text"
            className="search-input"
            placeholder="Cari berita badminton..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          <div className="search-options">

            <div className="option-group">
              <label>Metode Pencarian</label>

              <select
                value={method}
                onChange={(e) => setMethod(e.target.value)}
              >
                <option value="BM25">BM25</option>
                <option value="BM25+">BM25+</option>
              </select>
            </div>

            <div className="option-group">
              <label>Filter Negara</label>

              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
              >
                {countries.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

          </div>

          <button type="submit" className="search-button">
            Cari Berita
          </button>

        </form>
      </div>
    </div>
  );
}

export default Search;
