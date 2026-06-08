function FlightCard({ flight, index }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <span className="text-xs font-bold bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full">
          #{index + 1}
        </span>
      </div>
      <p className="text-sm text-gray-800 mt-2 font-medium">{flight.summary}</p>
      <p className="text-xs text-gray-500 mt-1">{flight.reason}</p>
    </div>
  );
}

function LocationCard({ location, index }) {
  const thingsToDo = location.things_to_do || [];
  const suggestedDays = location.suggested_days ?? 1;
  const dayLabel = suggestedDays === 1 ? "day" : "days";

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div className="flex items-start gap-3 p-4">
        <span className="text-xs font-bold bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full shrink-0">
          #{index + 1}
        </span>
        <div className="min-w-0">
          <h3 className="font-semibold text-gray-900">
            {location.name}
            <span className="text-xs font-normal text-gray-400 ml-2">
              {suggestedDays} {dayLabel}
            </span>
          </h3>
          {location.details && (
            <p className="text-sm text-gray-700 mt-2 leading-6">{location.details}</p>
          )}
          <p className="text-sm text-gray-600 mt-1">{location.why}</p>
          {thingsToDo.length > 0 && (
            <ul className="mt-2 space-y-1">
              {thingsToDo.map((thing, i) => (
                <li key={i} className="text-xs text-gray-500 flex items-start gap-1.5">
                  <span className="text-indigo-400 mt-0.5">-</span>
                  {thing}
                </li>
              ))}
            </ul>
          )}
          {location.map_url && (
            <a
              href={location.map_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-3 text-sm font-medium text-indigo-600 hover:text-indigo-800"
            >
              View on Google Maps
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

function HotelCard({ hotel, index }) {
  const reviewSummary = hotel.review_summary || [];
  const nearbySummary = hotel.nearby_summary || [];
  const services = hotel.services || [];
  const ratingText = hotel.rating
    ? `${hotel.rating}/5${hotel.reviews ? ` from ${hotel.reviews} reviews` : ""}`
    : "";

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div className="p-4">
        <div className="flex items-start gap-3">
          <span className="text-xs font-bold bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full shrink-0">
            #{index + 1}
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
              <h3 className="font-semibold text-gray-900">{hotel.name}</h3>
              {hotel.hotel_class && (
                <span className="text-xs text-gray-400">{hotel.hotel_class}</span>
              )}
            </div>

            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
              {ratingText && <span>{ratingText}</span>}
              {hotel.location_rating && <span>Location {hotel.location_rating}/5</span>}
              {hotel.price_per_night && <span>{hotel.price_per_night} / night</span>}
              {hotel.total_price && <span>{hotel.total_price} total</span>}
            </div>

            {hotel.address && (
              <p className="text-xs text-gray-500 mt-2">{hotel.address}</p>
            )}
            {hotel.summary && (
              <p className="text-sm text-gray-800 mt-2 font-medium">{hotel.summary}</p>
            )}
            <p className="text-sm text-gray-600 mt-2">{hotel.quality_reason}</p>
            <p className="text-sm text-gray-600 mt-1">{hotel.proximity_reason}</p>

            {nearbySummary.length > 0 && (
              <ul className="mt-3 space-y-1">
                {nearbySummary.slice(0, 3).map((note, i) => (
                  <li key={i} className="text-xs text-gray-500">
                    Nearby: {note}
                  </li>
                ))}
              </ul>
            )}

            {reviewSummary.length > 0 && (
              <ul className="mt-3 space-y-1">
                {reviewSummary.slice(0, 3).map((note, i) => (
                  <li key={i} className="text-xs text-gray-500">
                    {note}
                  </li>
                ))}
              </ul>
            )}

            {services.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {services.map((service, i) => (
                  <span
                    key={i}
                    className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                  >
                    {service}
                  </span>
                ))}
              </div>
            )}

            <div className="mt-3 flex flex-wrap gap-4 text-sm font-medium">
              {hotel.property_link && (
                <a
                  href={hotel.property_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-indigo-600 hover:text-indigo-800"
                >
                  View details
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Results({ data, onBack }) {
  const generatedModel = data.model_info?.model;
  const generatedProvider = data.model_info?.provider;
  const recommendedHotels = data.recommended_hotels || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 to-indigo-100 px-4 py-8">
      <div className="max-w-3xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {data.destination}
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              {data.departure_code} -&gt; {data.arrival_code}
              {data.total_estimated_budget > 0 && (
                <span> - Budget: ${data.total_estimated_budget}</span>
              )}
            </p>
            {generatedModel && (
              <p className="text-xs text-gray-400 mt-1">
                Generated by {generatedProvider ? `${generatedProvider} / ` : ""}{generatedModel}
              </p>
            )}
          </div>
          <button
            onClick={onBack}
            className="text-sm text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer"
          >
            New search
          </button>
        </div>

        {data.locations.length > 0 && (
          <section>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">
              Places to Visit
            </h2>
            <div className="grid gap-3">
              {data.locations.map((loc, i) => (
                <LocationCard key={i} location={loc} index={i} />
              ))}
            </div>
          </section>
        )}

        {data.recommended_flights.length > 0 && (
          <section>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">
              Recommended Flights
            </h2>
            <div className="grid gap-3">
              {data.recommended_flights.map((flight, i) => (
                <FlightCard key={i} flight={flight} index={i} />
              ))}
            </div>
            {data.google_flights_url && (
              <a
                href={data.google_flights_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block mt-3 text-sm text-indigo-600 hover:text-indigo-800 font-medium"
              >
                Browse all flights on Google Flights
              </a>
            )}
          </section>
        )}

        {recommendedHotels.length > 0 && (
          <section>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">
              Recommended Hotels
            </h2>
            <div className="grid gap-3">
              {recommendedHotels.map((hotel, i) => (
                <HotelCard key={i} hotel={hotel} index={i} />
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
