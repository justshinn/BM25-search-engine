import { Routes, Route } from "react-router-dom";

import Search from "./pages/Search.jsx";
import Results from "./pages/Results.jsx";
import Detail from "./pages/Detail.jsx";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Search />} />
      <Route path="/results" element={<Results />} />
      <Route path="/detail" element={<Detail />} />
    </Routes>
  );
}

export default App;
