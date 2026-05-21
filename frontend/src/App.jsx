import { useState } from "react";
import SearchForm from "./components/SearchForm";
import LoadingScreen from "./components/LoadingScreen";
import Results from "./components/Results";
import { getRecommendations } from "./services/api";

export default function App() {
  const [view, setView] = useState("search");
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  async function handleSearch(form) {
    setView("loading");
    setError(null);

    try {
      const data = await getRecommendations(form);
      setResults(data);
      setView("results");
    } catch (err) {
      setError(err.message);
      setView("search");
    }
  }

  function handleBack() {
    setView("search");
    setResults(null);
  }

  if (view === "loading") return <LoadingScreen />;
  if (view === "results" && results) return <Results data={results} onBack={handleBack} />;

  return (
    <>
      <SearchForm onSubmit={handleSearch} loading={view === "loading"} />
      {error && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-red-50 border border-red-200 text-red-700 px-5 py-3 rounded-xl shadow-lg text-sm max-w-md text-center">
          {error}
        </div>
      )}
    </>
  );
}
