"""Mock-API достопримечательностей.

- 4 города (задача 1: Токио, Амстердам, Париж, Москва).
- Токио — 18 записей с районами, длительностью визита, часами работы и
  координатами (lat/lon нужны folium-карте в задаче 9).
- Теги позволяют фильтровать под профиль из памяти («любит музеи»,
  «вегетарианец» -> vegetarian_food, «с ребёнком» -> kids).
- У Ghibli Museum флаг needs_advance_booking — хороший повод для агента
  предупредить пользователя (проверяется fact-based чек-листом в задаче 8).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Attraction:
    attraction_id: str
    name: str
    city: str
    district: str
    category: str            # temple | museum | viewpoint | market | park | district | experience
    tags: list[str]
    visit_duration_min: int
    open_hours: str          # человекочитаемо; "24/7" для улиц/районов
    price_usd: float
    lat: float
    lon: float
    best_time: str
    note: str = ""
    needs_advance_booking: bool = False


_A = Attraction

_ATTRACTIONS: list[Attraction] = [
    # ---------------- TOKYO (18) ----------------
    _A("AT-SENSOJI", "Senso-ji Temple", "Tokyo", "Asakusa", "temple",
       ["culture", "free", "iconic"], 90, "06:00-17:00 (территория 24/7)", 0.0,
       35.7148, 139.7967, "утро до 08:00 — без толп",
       "Улица Накамисэ с уличной едой ведёт к храму."),
    _A("AT-MEIJI", "Meiji Jingu Shrine", "Tokyo", "Harajuku", "temple",
       ["culture", "park", "free"], 90, "рассвет-закат", 0.0,
       35.6764, 139.6993, "утро", "Лесной парк в центре города, гигантские тории."),
    _A("AT-SHIBUYA-X", "Shibuya Crossing & Hachiko", "Tokyo", "Shibuya", "viewpoint",
       ["iconic", "free", "night"], 45, "24/7", 0.0,
       35.6595, 139.7005, "вечер, когда включается неон",
       "Вид сверху — из Shibuya Sky или Mag's Park."),
    _A("AT-SHIBUYASKY", "Shibuya Sky", "Tokyo", "Shibuya", "viewpoint",
       ["view", "sunset"], 75, "10:00-22:30", 17.0,
       35.6590, 139.7022, "за час до заката", needs_advance_booking=True),
    _A("AT-TEAMLAB", "teamLab Planets", "Tokyo", "Toyosu", "experience",
       ["art", "kids", "rain_ok"], 150, "09:00-22:00", 25.0,
       35.6494, 139.7898, "будни утром",
       "Ходишь босиком по воде; слоты выкупают за недели.",
       needs_advance_booking=True),
    _A("AT-TSUKIJI", "Tsukiji Outer Market", "Tokyo", "Tsukiji", "market",
       ["food", "vegetarian_food", "morning"], 120, "05:00-14:00", 0.0,
       35.6654, 139.7707, "07:00-10:00",
       "Рыбный рынок; есть овощные и тамагояки-лавки для вегетарианцев."),
    _A("AT-SKYTREE", "Tokyo Skytree", "Tokyo", "Sumida", "viewpoint",
       ["view", "kids"], 120, "10:00-21:00", 21.0,
       35.7101, 139.8107, "ясный день, слот на закат"),
    _A("AT-UENO", "Ueno Park", "Tokyo", "Ueno", "park",
       ["park", "free", "kids", "sakura"], 120, "05:00-23:00", 0.0,
       35.7156, 139.7745, "конец марта — цветение сакуры",
       "Вокруг парка — кластер музеев и зоопарк."),
    _A("AT-TNM", "Tokyo National Museum", "Tokyo", "Ueno", "museum",
       ["museum", "culture", "rain_ok"], 180, "09:30-17:00, пн закрыт", 7.0,
       35.7188, 139.7765, "будни",
       "Крупнейшая коллекция японского искусства; самурайские мечи и доспехи."),
    _A("AT-MORI", "Mori Art Museum + Tokyo City View", "Tokyo", "Roppongi", "museum",
       ["museum", "art", "view", "night"], 150, "10:00-22:00", 14.0,
       35.6605, 139.7292, "вечер: музей + ночной вид разом"),
    _A("AT-GHIBLI", "Ghibli Museum", "Tokyo", "Mitaka", "museum",
       ["museum", "kids", "anime"], 150, "10:00-18:00, вт закрыт", 8.0,
       35.6962, 139.5704, "по купленному слоту",
       "Билеты только заранее на конкретную дату, на месте не продают.",
       needs_advance_booking=True),
    _A("AT-SHINJUKUGY", "Shinjuku Gyoen Garden", "Tokyo", "Shinjuku", "park",
       ["park", "sakura", "quiet"], 120, "09:00-17:30, пн закрыт", 3.5,
       35.6852, 139.7100, "март — ранняя сакура"),
    _A("AT-AKIBA", "Akihabara Electric Town", "Tokyo", "Akihabara", "district",
       ["anime", "shopping", "night"], 150, "магазины ~10:00-20:00", 0.0,
       35.6984, 139.7731, "после обеда"),
    _A("AT-TAKESHITA", "Takeshita Street", "Tokyo", "Harajuku", "district",
       ["shopping", "food", "youth"], 90, "~10:00-20:00", 0.0,
       35.6716, 139.7031, "будний день — меньше давки",
       "Рядом с Meiji Jingu — логично объединять в один день."),
    _A("AT-GOLDENGAI", "Shinjuku Golden Gai", "Tokyo", "Shinjuku", "district",
       ["nightlife", "food"], 120, "19:00-02:00", 0.0,
       35.6938, 139.7049, "после 20:00",
       "200+ баров на 6 переулках; во многих cover charge 500-1000¥."),
    _A("AT-IMPERIAL", "Imperial Palace East Gardens", "Tokyo", "Chiyoda", "park",
       ["park", "history", "free", "quiet"], 90, "09:00-16:30, пн/пт закрыт", 0.0,
       35.6858, 139.7570, "утро"),
    _A("AT-YANAKA", "Yanaka Ginza & Old Town", "Tokyo", "Yanaka", "district",
       ["food", "history", "quiet", "vegetarian_food"], 120, "лавки ~10:00-18:00", 0.0,
       35.7278, 139.7669, "день",
       "Уцелевший довоенный Токио; сэнбэй, якитори, кошачьи сувениры."),
    _A("AT-ODAIBA", "Odaiba & Rainbow Bridge", "Tokyo", "Odaiba", "district",
       ["view", "kids", "night"], 180, "24/7", 0.0,
       35.6300, 139.7770, "закат с пляжа Odaiba Beach"),

    # ---------------- AMSTERDAM (5) ----------------
    _A("AT-RIJKS", "Rijksmuseum", "Amsterdam", "Museumkwartier", "museum",
       ["museum", "art", "rain_ok"], 180, "09:00-17:00", 25.0,
       52.3600, 4.8852, "утро", needs_advance_booking=True),
    _A("AT-VANGOGH", "Van Gogh Museum", "Amsterdam", "Museumkwartier", "museum",
       ["museum", "art"], 150, "09:00-18:00", 24.0,
       52.3584, 4.8811, "по слоту", needs_advance_booking=True),
    _A("AT-JORDAAN", "Jordaan & каналы", "Amsterdam", "Jordaan", "district",
       ["walk", "free", "food"], 150, "24/7", 0.0,
       52.3739, 4.8809, "вечер"),
    _A("AT-VONDEL", "Vondelpark", "Amsterdam", "Oud-Zuid", "park",
       ["park", "free", "kids"], 90, "24/7", 0.0,
       52.3579, 4.8686, "день"),
    _A("AT-ANNEFRANK", "Anne Frank House", "Amsterdam", "Centrum", "museum",
       ["museum", "history"], 90, "09:00-22:00", 17.0,
       52.3752, 4.8840, "только по онлайн-слоту", needs_advance_booking=True),

    # ---------------- PARIS (4) ----------------
    _A("AT-LOUVRE", "Louvre", "Paris", "1er", "museum",
       ["museum", "art", "iconic"], 240, "09:00-18:00, вт закрыт", 24.0,
       48.8606, 2.3376, "среда/пятница вечером", needs_advance_booking=True),
    _A("AT-EIFFEL", "Tour Eiffel", "Paris", "7e", "viewpoint",
       ["iconic", "view", "night"], 120, "09:30-23:00", 30.0,
       48.8584, 2.2945, "закат", needs_advance_booking=True),
    _A("AT-ORSAY", "Musée d'Orsay", "Paris", "7e", "museum",
       ["museum", "art"], 180, "09:30-18:00, пн закрыт", 16.0,
       48.8600, 2.3266, "четверг вечером"),
    _A("AT-MONTMARTRE", "Montmartre & Sacré-Cœur", "Paris", "18e", "district",
       ["walk", "view", "free"], 150, "24/7", 0.0,
       48.8867, 2.3431, "утро"),

    # ---------------- MOSCOW (4) ----------------
    _A("AT-REDSQ", "Красная площадь и Кремль", "Moscow", "Тверской", "district",
       ["iconic", "history"], 180, "площадь 24/7; Кремль 09:30-18:00", 9.0,
       55.7539, 37.6208, "утро"),
    _A("AT-TRETYAKOV", "Третьяковская галерея", "Moscow", "Замоскворечье", "museum",
       ["museum", "art", "rain_ok"], 180, "10:00-18:00, пн закрыт", 8.0,
       55.7415, 37.6208, "будни"),
    _A("AT-GORKY", "Парк Горького", "Moscow", "Якиманка", "park",
       ["park", "free", "kids"], 150, "24/7", 0.0,
       55.7298, 37.6019, "день"),
    _A("AT-VDNH", "ВДНХ", "Moscow", "Останкинский", "park",
       ["park", "history", "kids"], 240, "24/7, павильоны 10:00-22:00", 0.0,
       55.8304, 37.6325, "день"),
]


def search_attractions(
    city: str,
    tags: list[str] | None = None,      # AND-фильтр: ["museum"], ["kids","rain_ok"]
    category: str | None = None,
    district: str | None = None,
    max_price_usd: float | None = None,
    free_only: bool = False,
) -> list[dict]:
    """Поиск достопримечательностей. Неизвестный город -> []."""
    key = city.strip().lower()
    city_map = {"tokyo": "Tokyo", "токио": "Tokyo",
                "amsterdam": "Amsterdam", "амстердам": "Amsterdam",
                "paris": "Paris", "париж": "Paris",
                "moscow": "Moscow", "москва": "Moscow"}
    if key not in city_map:
        return []
    out = []
    for a in _ATTRACTIONS:
        if a.city != city_map[key]:
            continue
        if category and a.category != category:
            continue
        if district and a.district.lower() != district.strip().lower():
            continue
        if tags and not all(t in a.tags for t in tags):
            continue
        if free_only and a.price_usd > 0:
            continue
        if max_price_usd is not None and a.price_usd > max_price_usd:
            continue
        out.append(asdict(a))
    return out


def get_attraction_details(attraction_id: str) -> dict:
    for a in _ATTRACTIONS:
        if a.attraction_id == attraction_id:
            return asdict(a)
    raise KeyError(f"Attraction '{attraction_id}' not found")
