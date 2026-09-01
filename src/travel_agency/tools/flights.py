"""Mock-API рейсов: Москва / Амстердам -> Токио, март 2026.

Реалистичность:
- Из Москвы в 2026 прямых рейсов в Токио нет -> только стыковки (DXB, IST, PEK, AUH).
- Из Амстердама есть прямые (KLM) и стыковочные варианты.
- Цены/время в пути откалиброваны под реальные порядки величин.
- Один рейс намеренно sold-out (FL-EK0132) — для тестов ошибок бронирования.

Все функции — чистый Python без LLM, чтобы их можно было мокать в pytest.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field, asdict


@dataclass(frozen=True)
class Layover:
    airport: str          # IATA
    city: str
    duration_min: int


@dataclass(frozen=True)
class Flight:
    flight_id: str        # внутренний id, его валидирует book_flight
    marketing_carrier: str
    flight_numbers: list[str]
    origin: str           # IATA
    origin_city: str
    destination: str      # IATA (NRT/HND)
    destination_city: str
    depart: str           # ISO datetime, местное время вылета
    arrive: str           # ISO datetime, местное время прилёта
    duration_min: int
    layovers: list[Layover]
    cabin: str            # economy | premium_economy | business
    price_usd: float
    seats_left: int
    baggage_kg: int
    refundable: bool
    aircraft: str

    @property
    def is_direct(self) -> bool:
        return len(self.layovers) == 0


def _f(**kw) -> Flight:
    kw.setdefault("layovers", [])
    kw["layovers"] = [Layover(*l) if isinstance(l, tuple) else l for l in kw["layovers"]]
    return Flight(**kw)


_FLIGHTS: list[Flight] = [
    # ---------- Амстердам (AMS) -> Токио ----------
    _f(flight_id="FL-KL0861", marketing_carrier="KLM", flight_numbers=["KL861"],
       origin="AMS", origin_city="Amsterdam", destination="NRT", destination_city="Tokyo",
       depart="2026-03-14T14:40", arrive="2026-03-15T10:25", duration_min=705,
       cabin="economy", price_usd=812.0, seats_left=9, baggage_kg=23,
       refundable=False, aircraft="Boeing 787-10"),
    _f(flight_id="FL-KL0861B", marketing_carrier="KLM", flight_numbers=["KL861"],
       origin="AMS", origin_city="Amsterdam", destination="NRT", destination_city="Tokyo",
       depart="2026-03-14T14:40", arrive="2026-03-15T10:25", duration_min=705,
       cabin="business", price_usd=3390.0, seats_left=3, baggage_kg=32,
       refundable=True, aircraft="Boeing 787-10"),
    _f(flight_id="FL-KL0867", marketing_carrier="KLM", flight_numbers=["KL867"],
       origin="AMS", origin_city="Amsterdam", destination="HND", destination_city="Tokyo",
       depart="2026-03-17T17:55", arrive="2026-03-18T13:50", duration_min=715,
       cabin="economy", price_usd=768.0, seats_left=14, baggage_kg=23,
       refundable=False, aircraft="Boeing 777-300ER"),
    _f(flight_id="FL-AF1240", marketing_carrier="Air France", flight_numbers=["AF1241", "AF276"],
       origin="AMS", origin_city="Amsterdam", destination="HND", destination_city="Tokyo",
       depart="2026-03-14T07:35", arrive="2026-03-15T09:55", duration_min=940,
       layovers=[("CDG", "Paris", 105)],
       cabin="economy", price_usd=655.0, seats_left=22, baggage_kg=23,
       refundable=False, aircraft="A320 + Boeing 777-300ER"),
    _f(flight_id="FL-LH2303", marketing_carrier="Lufthansa", flight_numbers=["LH2303", "LH716"],
       origin="AMS", origin_city="Amsterdam", destination="HND", destination_city="Tokyo",
       depart="2026-03-14T09:10", arrive="2026-03-15T11:40", duration_min=970,
       layovers=[("MUC", "Munich", 130)],
       cabin="premium_economy", price_usd=1290.0, seats_left=6, baggage_kg=23,
       refundable=True, aircraft="A321neo + A350-900"),
    _f(flight_id="FL-TK1952", marketing_carrier="Turkish Airlines", flight_numbers=["TK1952", "TK198"],
       origin="AMS", origin_city="Amsterdam", destination="HND", destination_city="Tokyo",
       depart="2026-03-14T11:25", arrive="2026-03-15T17:35", duration_min=1210,
       layovers=[("IST", "Istanbul", 220)],
       cabin="economy", price_usd=589.0, seats_left=31, baggage_kg=30,
       refundable=False, aircraft="A321 + Boeing 787-9"),
    _f(flight_id="FL-FI0501", marketing_carrier="Finnair", flight_numbers=["AY1302", "AY73"],
       origin="AMS", origin_city="Amsterdam", destination="HND", destination_city="Tokyo",
       depart="2026-03-15T10:20", arrive="2026-03-16T12:45", duration_min=1000,
       layovers=[("HEL", "Helsinki", 95)],
       cabin="economy", price_usd=702.0, seats_left=11, baggage_kg=23,
       refundable=False, aircraft="A320 + A350-900"),

    # ---------- Москва (SVO/DME) -> Токио ----------
    _f(flight_id="FL-EK0132", marketing_carrier="Emirates", flight_numbers=["EK132", "EK312"],
       origin="DME", origin_city="Moscow", destination="NRT", destination_city="Tokyo",
       depart="2026-03-14T23:59", arrive="2026-03-16T17:35", duration_min=1470,
       layovers=[("DXB", "Dubai", 340)],
       cabin="economy", price_usd=1105.0, seats_left=0,   # sold out — тест-кейс
       baggage_kg=25, refundable=False, aircraft="Boeing 777-300ER x2"),
    _f(flight_id="FL-EK0134", marketing_carrier="Emirates", flight_numbers=["EK134", "EK318"],
       origin="DME", origin_city="Moscow", destination="HND", destination_city="Tokyo",
       depart="2026-03-14T16:40", arrive="2026-03-15T22:50", duration_min=1330,
       layovers=[("DXB", "Dubai", 210)],
       cabin="economy", price_usd=1180.0, seats_left=17, baggage_kg=25,
       refundable=False, aircraft="A380 + Boeing 777-300ER"),
    _f(flight_id="FL-EK0134B", marketing_carrier="Emirates", flight_numbers=["EK134", "EK318"],
       origin="DME", origin_city="Moscow", destination="HND", destination_city="Tokyo",
       depart="2026-03-14T16:40", arrive="2026-03-15T22:50", duration_min=1330,
       layovers=[("DXB", "Dubai", 210)],
       cabin="business", price_usd=4470.0, seats_left=2, baggage_kg=40,
       refundable=True, aircraft="A380 + Boeing 777-300ER"),
    _f(flight_id="FL-TK0414", marketing_carrier="Turkish Airlines", flight_numbers=["TK414", "TK198"],
       origin="VKO", origin_city="Moscow", destination="HND", destination_city="Tokyo",
       depart="2026-03-14T05:20", arrive="2026-03-15T17:35", duration_min=1520,
       layovers=[("IST", "Istanbul", 465)],
       cabin="economy", price_usd=845.0, seats_left=42, baggage_kg=30,
       refundable=False, aircraft="A321neo + Boeing 787-9"),
    _f(flight_id="FL-CA0910", marketing_carrier="Air China", flight_numbers=["CA910", "CA167"],
       origin="SVO", origin_city="Moscow", destination="NRT", destination_city="Tokyo",
       depart="2026-03-14T13:10", arrive="2026-03-15T14:05", duration_min=1075,
       layovers=[("PEK", "Beijing", 160)],
       cabin="economy", price_usd=698.0, seats_left=26, baggage_kg=23,
       refundable=False, aircraft="A330-300 + Boeing 737 MAX 8"),
    _f(flight_id="FL-CZ0656", marketing_carrier="China Southern", flight_numbers=["CZ656", "CZ385"],
       origin="SVO", origin_city="Moscow", destination="NRT", destination_city="Tokyo",
       depart="2026-03-14T18:55", arrive="2026-03-16T08:40", duration_min=1545,
       layovers=[("CAN", "Guangzhou", 380)],
       cabin="economy", price_usd=612.0, seats_left=38, baggage_kg=23,
       refundable=False, aircraft="A350-900 + A321"),
    _f(flight_id="FL-EY0068", marketing_carrier="Etihad", flight_numbers=["EY68", "EY871"],
       origin="DME", origin_city="Moscow", destination="NRT", destination_city="Tokyo",
       depart="2026-03-15T00:55", arrive="2026-03-16T13:20", duration_min=1405,
       layovers=[("AUH", "Abu Dhabi", 290)],
       cabin="economy", price_usd=934.0, seats_left=13, baggage_kg=23,
       refundable=False, aircraft="Boeing 787-9 x2"),
    _f(flight_id="FL-EY0068B", marketing_carrier="Etihad", flight_numbers=["EY68", "EY871"],
       origin="DME", origin_city="Moscow", destination="NRT", destination_city="Tokyo",
       depart="2026-03-15T00:55", arrive="2026-03-16T13:20", duration_min=1405,
       layovers=[("AUH", "Abu Dhabi", 290)],
       cabin="business", price_usd=3980.0, seats_left=4, baggage_kg=40,
       refundable=True, aircraft="Boeing 787-9 x2"),
    # Рейс, прилетающий ПОСЛЕ типового check-in 16 марта — «хитрый» кейс для задачи 8
    _f(flight_id="FL-CZ0658", marketing_carrier="China Southern", flight_numbers=["CZ658", "CZ8391"],
       origin="SVO", origin_city="Moscow", destination="NRT", destination_city="Tokyo",
       depart="2026-03-16T21:30", arrive="2026-03-18T11:15", duration_min=1610,
       layovers=[("CAN", "Guangzhou", 540)],
       cabin="economy", price_usd=488.0, seats_left=51, baggage_kg=23,
       refundable=False, aircraft="A330-300 + A321"),
]

_CITY_ALIASES = {
    "moscow": {"SVO", "DME", "VKO"}, "москва": {"SVO", "DME", "VKO"},
    "amsterdam": {"AMS"}, "амстердам": {"AMS"},
    "tokyo": {"NRT", "HND"}, "токио": {"NRT", "HND"},
}


def _resolve(code_or_city: str) -> set[str]:
    key = code_or_city.strip().lower()
    if key in _CITY_ALIASES:
        return _CITY_ALIASES[key]
    return {code_or_city.strip().upper()}


def search_flights(
    origin: str,
    destination: str,
    date: str | None = None,          # "2026-03-14"; None = все даты
    cabin: str | None = None,         # economy | premium_economy | business
    max_price_usd: float | None = None,
    direct_only: bool = False,
    max_layovers: int | None = None,
) -> list[dict]:
    """Поиск рейсов. origin/destination — город или IATA-код.

    Возвращает список dict (сериализуемо для tool output), отсортированный по цене.
    Рейсы с seats_left == 0 не возвращаются поиском (как в реальных GDS),
    но остаются в базе — get_flight_details их видит.
    """
    origins, dests = _resolve(origin), _resolve(destination)
    out = []
    for fl in _FLIGHTS:
        if fl.origin not in origins or fl.destination not in dests:
            continue
        if date and not fl.depart.startswith(date):
            continue
        if cabin and fl.cabin != cabin:
            continue
        if max_price_usd is not None and fl.price_usd > max_price_usd:
            continue
        if direct_only and not fl.is_direct:
            continue
        if max_layovers is not None and len(fl.layovers) > max_layovers:
            continue
        if fl.seats_left == 0:
            continue
        d = asdict(fl)
        d["is_direct"] = fl.is_direct
        out.append(d)
    return sorted(out, key=lambda x: x["price_usd"])


def get_flight_details(flight_id: str) -> dict:
    """Полная карточка рейса по id. Бросает KeyError для несуществующего id —
    агент должен уметь обработать такую ошибку тула."""
    for fl in _FLIGHTS:
        if fl.flight_id == flight_id:
            d = asdict(fl)
            d["is_direct"] = fl.is_direct
            d["fare_rules"] = (
                "Refundable minus $150 fee" if fl.refundable
                else "Non-refundable; date change $95 + fare difference"
            )
            return d
    raise KeyError(f"Flight '{flight_id}' not found")


def _decrement_seat(flight_id: str) -> None:
    """Внутренний хук для booking.py: имитируем уменьшение мест."""
    for i, fl in enumerate(_FLIGHTS):
        if fl.flight_id == flight_id:
            if fl.seats_left <= 0:
                raise ValueError(f"Flight '{flight_id}' is sold out")
            object.__setattr__(fl, "seats_left", fl.seats_left - 1)
            return
    raise KeyError(f"Flight '{flight_id}' not found")
