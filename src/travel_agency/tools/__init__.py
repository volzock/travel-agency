"""src/travel_agency/tools — mock-API турагентства.

Слои:
- flights / hotels / attractions / booking — чистый Python (тестируется без LLM).
- langchain_tools() — фабрика LangChain-тулов поверх этих функций; импорт
  langchain ленивый, чтобы юнит-тесты данных не тянули тяжёлые зависимости.

Раскладка тулов по агентам (задачи 6-10):
    flight_agent      : search_flights, get_flight_details
    hotel_agent       : search_hotels, get_hotel_details
    destination_agent : search_attractions, get_attraction_details
    booking (за HITL) : book_flight, book_hotel, cancel_booking
"""

from . import flights, hotels, attractions  # noqa: F401


def __getattr__(name):
    # ленивый импорт: booking тянет pydantic, он не нужен для чистых data-модулей.
    # ВАЖНО: не использовать здесь `from . import booking` — это рекурсивно
    # вызывает этот же __getattr__ (importlib проверяет атрибут пакета до
    # завершения импорта подмодуля) -> RecursionError.
    if name == "booking":
        import importlib
        mod = importlib.import_module(".booking", __name__)
        globals()["booking"] = mod   # кэшируем: следующий доступ минует __getattr__
        return mod
    raise AttributeError(name)


def langchain_tools() -> dict:
    """Возвращает {имя: BaseTool}. Разбирай по агентам сам —
    супервизор НЕ должен получать прямой доступ к тулам воркеров (задача 10).
    """
    from langchain_core.tools import tool
    import importlib
    booking = importlib.import_module(".booking", __name__)

    @tool
    def search_flights(origin: str, destination: str, date: str | None = None,
                       cabin: str | None = None, max_price_usd: float | None = None,
                       direct_only: bool = False) -> list[dict]:
        """Search flights by city/IATA, optional date (YYYY-MM-DD), cabin
        (economy|premium_economy|business), price cap and direct_only flag."""
        return flights.search_flights(origin, destination, date, cabin,
                                      max_price_usd, direct_only)

    @tool
    def get_flight_details(flight_id: str) -> dict:
        """Full fare card for a flight_id returned by search_flights."""
        return flights.get_flight_details(flight_id)

    @tool
    def search_hotels(city: str = "Tokyo", district: str | None = None,
                      min_stars: int | None = None,
                      max_price_per_night_usd: float | None = None,
                      breakfast_required: bool = False,
                      family_friendly: bool = False) -> list[dict]:
        """Search hotels; filters: district, stars, nightly price cap,
        breakfast, family friendliness."""
        return hotels.search_hotels(city, district, min_stars,
                                    max_price_per_night_usd,
                                    breakfast_required, family_friendly)

    @tool
    def get_hotel_details(hotel_id: str) -> dict:
        """Full hotel card by hotel_id."""
        return hotels.get_hotel_details(hotel_id)

    @tool
    def search_attractions(city: str, tags: list[str] | None = None,
                           category: str | None = None,
                           district: str | None = None,
                           free_only: bool = False) -> list[dict]:
        """Search attractions in Tokyo/Amsterdam/Paris/Moscow. Tags are ANDed,
        e.g. ["museum"], ["kids","rain_ok"], ["vegetarian_food"]."""
        return attractions.search_attractions(city, tags, category,
                                              district, free_only=free_only)

    @tool
    def get_attraction_details(attraction_id: str) -> dict:
        """Full attraction card by attraction_id."""
        return attractions.get_attraction_details(attraction_id)

    @tool
    def book_flight(flight_id: str, full_name: str, email: str,
                    idempotency_key: str, passport: str | None = None) -> dict:
        """Book a flight. IRREVERSIBLE: must be called only after human
        approval (interrupt/resume). Same idempotency_key => same booking."""
        return booking.book_flight({
            "flight_id": flight_id, "idempotency_key": idempotency_key,
            "passenger": {"full_name": full_name, "email": email,
                          "passport": passport},
        })

    @tool
    def book_hotel(hotel_id: str, full_name: str, email: str, check_in: str,
                   check_out: str, idempotency_key: str,
                   guests_count: int = 1) -> dict:
        """Book a hotel stay (dates YYYY-MM-DD). IRREVERSIBLE: human approval
        required first. Idempotent by idempotency_key."""
        return booking.book_hotel({
            "hotel_id": hotel_id, "idempotency_key": idempotency_key,
            "check_in": check_in, "check_out": check_out,
            "guests_count": guests_count,
            "guest": {"full_name": full_name, "email": email},
        })

    @tool
    def cancel_booking(pnr: str) -> dict:
        """Cancel an existing booking by PNR."""
        return booking.cancel_booking(pnr)

    local = dict(locals())
    return {name: t for name, t in local.items()
            if hasattr(t, "invoke") and hasattr(t, "name")}
