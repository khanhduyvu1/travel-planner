export default function LoadingScreen() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-sky-50 to-indigo-100">
      <div className="flex flex-col items-center gap-6">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 rounded-full border-4 border-indigo-200"></div>
          <div className="absolute inset-0 rounded-full border-4 border-t-indigo-600 animate-spin"></div>
        </div>
        <div className="text-center">
          <p className="text-lg font-semibold text-gray-800">Planning your trip...</p>
          <p className="text-sm text-gray-500 mt-1">Searching flights and generating recommendations</p>
          <p className="text-xs text-gray-400 mt-3">This may take a few minutes</p>
        </div>
      </div>
    </div>
  );
}
