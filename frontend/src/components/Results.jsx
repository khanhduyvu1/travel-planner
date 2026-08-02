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
                  className="inline-flex items-center gap-1.5 text-indigo-600 hover:text-indigo-800"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  View on Google Maps
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ItineraryCard({ location, flight, hotel, index }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="bg-gradient-to-r from-indigo-50 to-sky-50 px-4 py-3 border-b border-gray-100">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <span className="text-xs font-bold bg-indigo-600 text-white px-2 py-0.5 rounded-full">
            {index + 1}
          </span>
          {location?.name || "Day Plan"}
        </h3>
        {location?.suggested_days && (
          <p className="text-xs text-gray-500 mt-1 ml-7">
            {location.suggested_days} {location.suggested_days === 1 ? "day" : "days"}
          </p>
        )}
      </div>

      <div className="p-4 space-y-3">
        {location?.details && (
          <p className="text-sm text-gray-700 leading-relaxed">{location.details}</p>
        )}

        {location?.why && (
          <div className="bg-emerald-50 rounded-lg p-3">
            <p className="text-xs font-medium text-emerald-800 mb-1">Why visit:</p>
            <p className="text-sm text-emerald-700">{location.why}</p>
          </div>
        )}

        {location?.things_to_do?.length > 0 && (
          <div>
            <p className="text-xs font-medium text-gray-700 mb-2">Things to do:</p>
            <ul className="space-y-1.5">
              {location.things_to_do.map((thing, i) => (
                <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                  <span className="text-indigo-500 mt-1 shrink-0">•</span>
                  {thing}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Restaurants Section */}
        {(location?.lunch || location?.dinner) && (
          <div className="border-t border-gray-100 pt-3 mt-3">
            <p className="text-xs font-medium text-gray-700 mb-3 flex items-center gap-1.5">
              <svg className="w-4 h-4 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Where to Eat
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {location.lunch && (
                <div className="bg-orange-50 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold bg-orange-200 text-orange-800 px-2 py-0.5 rounded-full">Lunch</span>
                    <span className="text-xs text-orange-600">{location.lunch.cuisine}</span>
                  </div>
                  <p className="text-sm font-medium text-gray-800">{location.lunch.name}</p>
                  {location.lunch.map_url && (
                    <a
                      href={location.lunch.map_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 mt-2 text-xs font-medium text-orange-600 hover:text-orange-800"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Directions
                    </a>
                  )}
                </div>
              )}
              {location.dinner && (
                <div className="bg-red-50 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold bg-red-200 text-red-800 px-2 py-0.5 rounded-full">Dinner</span>
                    <span className="text-xs text-red-600">{location.dinner.cuisine}</span>
                  </div>
                  <p className="text-sm font-medium text-gray-800">{location.dinner.name}</p>
                  {location.dinner.map_url && (
                    <a
                      href={location.dinner.map_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 mt-2 text-xs font-medium text-red-600 hover:text-red-800"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Directions
                    </a>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {location?.map_url && (
          <a
            href={location.map_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-800 pt-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            View on Google Maps
          </a>
        )}
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

        {/* Recommended Flights */}
        {data.recommended_flights?.length > 0 && (
          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
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
                className="inline-flex items-center gap-1.5 mt-3 text-sm font-medium text-indigo-600 hover:text-indigo-800"
              >
                Browse all flights on Google Flights
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            )}
          </section>
        )}

        {/* Places to Visit */}
        {data.locations?.length > 0 && (
          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Places to Visit
            </h2>
            <div className="grid gap-3">
              {data.locations.map((loc, i) => (
                <LocationCard key={i} location={loc} index={i} />
              ))}
            </div>
          </section>
        )}

        {/* Recommended Hotels */}
        {recommendedHotels.length > 0 && (
          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              Recommended Hotels
            </h2>
            <div className="grid gap-3">
              {recommendedHotels.map((hotel, i) => (
                <HotelCard key={i} hotel={hotel} index={i} />
              ))}
            </div>
          </section>
        )}

        {/* Day-by-Day Itinerary */}
        {data.locations?.length > 0 && (
          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              Your Itinerary
            </h2>
            <div className="grid gap-4">
              {data.locations.map((location, i) => (
                <ItineraryCard key={i} location={location} index={i} />
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
