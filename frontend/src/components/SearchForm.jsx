import { useState } from "react";

const STOP_OPTIONS = [
  { value: "", label: "Any" },
  { value: "0", label: "Nonstop" },
  { value: "1", label: "1 stop" },
  { value: "2", label: "2 stops" },
];

const MODEL_MODES = [
  { value: "open", label: "Open" },
  { value: "local", label: "Local" },
];

export default function SearchForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    startCity: "",
    destination: "",
    startDate: "",
    returnDate: "",
    estimatedBudget: "",
    maxStops: "",
    modelMode: "open",
  });

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit({
      ...form,
      maxStops: form.maxStops === "" ? null : parseInt(form.maxStops),
    });
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-sky-50 to-indigo-100 px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-lg bg-white rounded-2xl shadow-lg p-8 space-y-5"
      >
        <div className="text-center mb-2">
          <h1 className="text-3xl font-bold text-gray-900">Travel Planner</h1>
          <p className="text-gray-500 mt-1">Plan your next trip with AI</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Model source</label>
          <div className="grid grid-cols-2 rounded-lg border border-gray-300 bg-gray-50 p-1">
            {MODEL_MODES.map((mode) => {
              const selected = form.modelMode === mode.value;

              return (
                <button
                  key={mode.value}
                  type="button"
                  onClick={() => setForm({ ...form, modelMode: mode.value })}
                  className={`rounded-md px-3 py-2 text-sm font-semibold transition-colors ${
                    selected
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-gray-600 hover:bg-white hover:text-gray-900"
                  }`}
                  aria-pressed={selected}
                >
                  {mode.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2 sm:col-span-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">From</label>
            <input
              name="startCity"
              value={form.startCity}
              onChange={handleChange}
              placeholder="e.g. Tampa"
              required
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <div className="col-span-2 sm:col-span-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">To</label>
            <input
              name="destination"
              value={form.destination}
              onChange={handleChange}
              placeholder="e.g. Hanoi"
              required
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Departure</label>
            <input
              type="date"
              name="startDate"
              value={form.startDate}
              onChange={handleChange}
              required
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Return</label>
            <input
              type="date"
              name="returnDate"
              value={form.returnDate}
              onChange={handleChange}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Budget</label>
            <input
              name="estimatedBudget"
              value={form.estimatedBudget}
              onChange={handleChange}
              placeholder="e.g. 1000 USD"
              required
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Max stops</label>
            <select
              name="maxStops"
              value={form.maxStops}
              onChange={handleChange}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              {STOP_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold py-2.5 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed"
        >
          {loading ? "Planning your trip..." : "Plan My Trip"}
        </button>
      </form>
    </div>
  );
}
