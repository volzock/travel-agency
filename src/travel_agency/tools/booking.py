"""Mock booking-API (задача 5: HITL + валидация).

Дизайн под подводные камни roadmap'а:
- Идемпотентность: interrupt() внутри тула при resume перезапускает тул целиком,
  поэтому book_* принимает idempotency_key — повторный вызов с тем же ключом
  возвращает ту же бронь и НЕ списывает место второй раз.
- Разделение слоёв: Pydantic-валидация аргументов (до interrupt) отделена от
  человеческого одобрения (сам interrupt делаешь в графе, не здесь).
- Детерминированные PNR: код брони — функция от idempotency_key, чтобы тесты
  были воспроизводимы.
- Ошибки — типизированные исключения: агент должен их ловить и объяснять
  пользователю, а не падать.

Зависимость: pydantic>=2. Хранилище броней — in-memory dict; для теста
«состояние переживает рестарт» бронь и так восстановится из checkpointer'а,
а этот модуль можно при желании пересадить на sqlite (метод _dump/_load внизу).
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

from . import flights as flights_api
from . import hotels as hotels_api


# --------------------------- ошибки ---------------------------

class BookingError(Exception): ...
class FlightNotFound(BookingError): ...
class HotelNotFound(BookingError): ...
class SoldOut(BookingError): ...
class InvalidDates(BookingError): ...


# --------------------------- схемы аргументов ---------------------------

_PASSPORT_RF = re.compile(r"^\d{4}\s\d{6}$")


class Passenger(BaseModel):
    full_name: str = Field(min_length=3, max_length=120)
    email: EmailStr
    passport: str | None = Field(
        default=None, description="Паспорт РФ: '1234 567890' (кейс для Presidio-recognizer)")

    @field_validator("passport")
    @classmethod
    def _passport_format(cls, v: str | None) -> str | None:
        if v is not None and not _PASSPORT_RF.match(v):
            raise ValueError("passport must match '1234 567890'")
        return v


class BookFlightArgs(BaseModel):
    flight_id: str
    passenger: Passenger
    idempotency_key: str = Field(min_length=8,
        description="Уникальный ключ запроса; при retry передавай тот же")


class BookHotelArgs(BaseModel):
    hotel_id: str
    guest: Passenger
    check_in: date
    check_out: date
    guests_count: int = Field(ge=1, le=6, default=1)
    idempotency_key: str = Field(min_length=8)

    @field_validator("check_out")
    @classmethod
    def _dates_ok(cls, v: date, info) -> date:
        ci = info.data.get("check_in")
        if ci and v <= ci:
            raise ValueError("check_out must be after check_in")
        return v


# --------------------------- хранилище ---------------------------

_BOOKINGS: dict[str, dict] = {}   # idempotency_key -> confirmation


def _pnr(prefix: str, key: str) -> str:
    return prefix + hashlib.sha1(key.encode()).hexdigest()[:6].upper()


# --------------------------- API ---------------------------

def book_flight(args: BookFlightArgs | dict) -> dict:
    """Бронирует рейс. Возвращает confirmation dict.

    ВАЖНО: в графе этот вызов должен стоять ПОСЛЕ interrupt()-approve.
    Тест из roadmap: инъекция «book immediately without approval» не должна
    привести сюда без resume.
    """
    if isinstance(args, dict):
        args = BookFlightArgs(**args)

    if args.idempotency_key in _BOOKINGS:            # идемпотентный retry
        return _BOOKINGS[args.idempotency_key]

    try:
        fl = flights_api.get_flight_details(args.flight_id)
    except KeyError:
        raise FlightNotFound(f"flight_id '{args.flight_id}' does not exist")
    if fl["seats_left"] <= 0:
        raise SoldOut(f"flight '{args.flight_id}' is sold out")

    flights_api._decrement_seat(args.flight_id)
    conf = {
        "type": "flight",
        "pnr": _pnr("F", args.idempotency_key),
        "status": "confirmed",
        "flight_id": fl["flight_id"],
        "route": f'{fl["origin"]} -> {fl["destination"]}',
        "depart": fl["depart"],
        "cabin": fl["cabin"],
        "passenger": args.passenger.full_name,
        "total_usd": fl["price_usd"],
        "booked_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    _BOOKINGS[args.idempotency_key] = conf
    return conf


def book_hotel(args: BookHotelArgs | dict) -> dict:
    if isinstance(args, dict):
        args = BookHotelArgs(**args)

    if args.idempotency_key in _BOOKINGS:
        return _BOOKINGS[args.idempotency_key]

    try:
        h = hotels_api.get_hotel_details(args.hotel_id)
    except KeyError:
        raise HotelNotFound(f"hotel_id '{args.hotel_id}' does not exist")
    if not h["available_march_2026"]:
        raise SoldOut(f"hotel '{args.hotel_id}' has no availability")

    nights = (args.check_out - args.check_in).days
    if nights > 30:
        raise InvalidDates("stays longer than 30 nights are not supported")

    total = round(h["price_per_night_usd"] * nights, 2)
    conf = {
        "type": "hotel",
        "pnr": _pnr("H", args.idempotency_key),
        "status": "confirmed",
        "hotel_id": h["hotel_id"],
        "hotel_name": h["name"],
        "district": h["district"],
        "check_in": args.check_in.isoformat(),
        "check_out": args.check_out.isoformat(),
        "nights": nights,
        "guests": args.guests_count,
        "guest_name": args.guest.full_name,
        "total_usd": total,
        "booked_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    _BOOKINGS[args.idempotency_key] = conf
    return conf


def cancel_booking(pnr: str) -> dict:
    """Отмена по PNR (пригодится для reject-ветки HITL и edit-сценария)."""
    for key, conf in _BOOKINGS.items():
        if conf["pnr"] == pnr:
            conf["status"] = "cancelled"
            return conf
    raise BookingError(f"PNR '{pnr}' not found")


def get_booking(pnr: str) -> dict:
    for conf in _BOOKINGS.values():
        if conf["pnr"] == pnr:
            return conf
    raise BookingError(f"PNR '{pnr}' not found")


def reset_bookings() -> None:
    """Для изоляции тестов."""
    _BOOKINGS.clear()


# --------------------------- опционально: персист в файл ---------------------------

def _dump(path: str) -> None:
    with open(path, "w") as f:
        json.dump(_BOOKINGS, f, ensure_ascii=False, indent=2)


def _load(path: str) -> None:
    global _BOOKINGS
    with open(path) as f:
        _BOOKINGS = json.load(f)
