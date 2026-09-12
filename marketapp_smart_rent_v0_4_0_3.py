"""
MarketApp Smart Rent for FunPay Cardinal
v0.4.0

Один файл. Каталог 78 лотов встроен внутрь.
Настройки доступны из Telegram-ПУ Cardinal:
Плагины -> MarketApp Smart Rent -> Настройки.
"""
from __future__ import annotations

import asyncio
import html
import importlib.util
import inspect
import json
import logging
import math
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

NAME = "MarketApp Smart Rent"
VERSION = "0.4.0.3"
DESCRIPTION = "Умная аренда Telegram Gifts: lot_id, количество=срок, минимальная итоговая цена, MarketApp."
CREDITS = "OpenAI / custom"
UUID = "a9912d45-31d8-42a1-92aa-b40e01202581"
SETTINGS_PAGE = True

LOGGER = logging.getLogger("FPC.MarketAppSmartRent")
CB = "MSR4"

DATA_DIR = Path("storage/plugins/marketapp_smart_rent")
DATA_PATH = DATA_DIR / "data.json"
VENDOR_DIR = DATA_DIR / "vendor"

CATALOG = [{'funpay_match': 'HAPPY BROWNIES', 'market_name': 'Happy Brownies', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'LOOT BAGS', 'market_name': 'Loot Bags', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'SWAG BAG', 'market_name': 'Swag Bags', 'hours_per_unit': 24, 'aliases': ['Swag Bag']}, {'funpay_match': 'DESK CALENDAR', 'market_name': 'Desk Calendars', 'hours_per_unit': 24, 'aliases': ['Desk Calendar']}, {'funpay_match': 'STELLAR ROCKET', 'market_name': 'Stellar Rockets', 'hours_per_unit': 24, 'aliases': ['Stellar Rocket']}, {'funpay_match': 'LIGHT SWORD', 'market_name': 'Light Swords', 'hours_per_unit': 24, 'aliases': ['Light Sword']}, {'funpay_match': 'LUNAR SNAKE', 'market_name': 'Lunar Snakes', 'hours_per_unit': 24, 'aliases': ['Lunar Snake']}, {'funpay_match': 'INPUT KEYS', 'market_name': 'Input Keys', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'SNOOP CIGARS', 'market_name': 'Snoop Cigars', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'FRESH SOCKS', 'market_name': 'Fresh Socks', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'LUSH BOUQUETS', 'market_name': 'Lush Bouquets', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'TAMA GADGET', 'market_name': 'Tama Gadgets', 'hours_per_unit': 24, 'aliases': ['Tama Gadget']}, {'funpay_match': 'JOLLY CHIMP', 'market_name': 'Jolly Chimps', 'hours_per_unit': 24, 'aliases': ['Jolly Chimp']}, {'funpay_match': 'SPICED WINE', 'market_name': 'Spiced Wines', 'hours_per_unit': 24, 'aliases': ['Spiced Wine']}, {'funpay_match': 'EVIL EYES', 'market_name': 'Evil Eyes', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'EASTER EGG', 'market_name': 'Easter Eggs', 'hours_per_unit': 24, 'aliases': ['Easter Egg']}, {'funpay_match': 'SPY AGARIC', 'market_name': 'Spy Agarics', 'hours_per_unit': 24, 'aliases': ['Spy Agaric']}, {'funpay_match': 'JOYFUL BUNDLE', 'market_name': 'Joyful Bundles', 'hours_per_unit': 24, 'aliases': ['Joyful Bundle']}, {'funpay_match': 'HYPNO LOLLIPOPS', 'market_name': 'Hypno Lollipops', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'WINTER WREATH', 'market_name': 'Winter Wreaths', 'hours_per_unit': 24, 'aliases': ['Winter Wreath']}, {'funpay_match': 'STAR NOTEPAD', 'market_name': 'Star Notepads', 'hours_per_unit': 24, 'aliases': ['Star Notepad']}, {'funpay_match': 'JACK-IN-THE-BOX', 'market_name': 'Jacks-in-the-Box', 'hours_per_unit': 24, 'aliases': ['Jack-in-the-Box', 'Jack In The Box']}, {'funpay_match': 'BIG YEAR', 'market_name': 'Big Years', 'hours_per_unit': 96, 'aliases': ['Big Year']}, {'funpay_match': 'SAKURA FLOWERS', 'market_name': 'Sakura Flowers', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'BUNNY MUFFIN', 'market_name': 'Bunny Muffins', 'hours_per_unit': 24, 'aliases': ['Bunny Muffin']}, {'funpay_match': 'BOW TIE', 'market_name': 'Bow Ties', 'hours_per_unit': 24, 'aliases': ['Bow Tie']}, {'funpay_match': 'WITCH HATS', 'market_name': 'Witch Hats', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'HEX POT', 'market_name': 'Hex Pots', 'hours_per_unit': 24, 'aliases': ['Hex Pot']}, {'funpay_match': 'BERRY BOX', 'market_name': 'Berry Boxes', 'hours_per_unit': 24, 'aliases': ['Berry Box']}, {'funpay_match': 'SANTA HAT', 'market_name': 'Santa Hats', 'hours_per_unit': 24, 'aliases': ['Santa Hat']}, {'funpay_match': 'ETERNAL CANDLES', 'market_name': 'Eternal Candles', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'VALENTINE BOX', 'market_name': 'Valentine Boxes', 'hours_per_unit': 24, 'aliases': ['Valentine Box']}, {'funpay_match': 'JINGLE BELL', 'market_name': 'Jingle Bells', 'hours_per_unit': 24, 'aliases': ['Jingle Bell']}, {'funpay_match': 'SKY STILETTOS', 'market_name': 'Sky Stilettos', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'HANGING STAR', 'market_name': 'Hanging Stars', 'hours_per_unit': 24, 'aliases': ['Hanging Star']}, {'funpay_match': 'LOVE POTIONS', 'market_name': 'Love Potions', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'ETERNAL ROSES', 'market_name': 'Eternal Roses', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'SNOW GLOBE', 'market_name': 'Snow Globes', 'hours_per_unit': 24, 'aliases': ['Snow Globe']}, {'funpay_match': 'CRYSTAL BALLS', 'market_name': 'Crystal Balls', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'DIAMOND RING', 'market_name': 'Diamond Rings', 'hours_per_unit': 24, 'aliases': ['Diamond Ring']}, {'funpay_match': 'TOP HATS', 'market_name': 'Top Hats', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'CUPID CHARMS', 'market_name': 'Cupid Charms', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'TRAPPED HEARTS', 'market_name': 'Trapped Hearts', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'RARE BIRDS', 'market_name': 'Rare Birds', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'SKULL FLOWERS', 'market_name': 'Skull Flowers', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'SNOOP DOGG', 'market_name': 'Snoop Doggs', 'hours_per_unit': 24, 'aliases': ['Snoop Dogg']}, {'funpay_match': 'VINTAGE CIGAR', 'market_name': 'Vintage Cigars', 'hours_per_unit': 24, 'aliases': ['Vintage Cigar']}, {'funpay_match': 'UFC STRIKE', 'market_name': 'UFC Strikes', 'hours_per_unit': 24, 'aliases': ['UFC Strike']}, {'funpay_match': 'SWISS WATCH', 'market_name': 'Swiss Watches', 'hours_per_unit': 24, 'aliases': ['Swiss Watch']}, {'funpay_match': 'MINI OSCAR', 'market_name': 'Mini Oscars', 'hours_per_unit': 24, 'aliases': ['Mini Oscar']}, {'funpay_match': 'VOODOO DOLLS', 'market_name': 'Voodoo Dolls', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'GEM SIGNET', 'market_name': 'Gem Signets', 'hours_per_unit': 24, 'aliases': ['Gem Signet']}, {'funpay_match': 'ION GEMS', 'market_name': 'Ion Gems', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'WESTSIDE SIGNS', 'market_name': 'Westside Signs', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'NAIL BRACELET', 'market_name': 'Nail Bracelets', 'hours_per_unit': 24, 'aliases': ['Nail Bracelet']}, {'funpay_match': 'ASTRAL SHARD', 'market_name': 'Astral Shards', 'hours_per_unit': 24, 'aliases': ['Astral Shard']}, {'funpay_match': 'HEROIC HELMET', 'market_name': 'Heroic Helmets', 'hours_per_unit': 24, 'aliases': ['Heroic Helmet']}, {'funpay_match': 'MIGHTY ARM', 'market_name': 'Mighty Arms', 'hours_per_unit': 24, 'aliases': ['Mighty Arm']}, {'funpay_match': 'HEART LOCKETS', 'market_name': 'Heart Lockets', 'hours_per_unit': 24, 'aliases': ['Heart Locket']}, {'funpay_match': 'SCARED CAT', 'market_name': 'Scared Cats', 'hours_per_unit': 24, 'aliases': ['Scared Cat']}, {'funpay_match': 'PRECIOUS PEACHES', 'market_name': 'Precious Peaches', 'hours_per_unit': 24, 'aliases': ['Precious Peach']}, {'funpay_match': 'DUROV CAPS', 'market_name': "Durov's Caps", 'hours_per_unit': 24, 'aliases': ['Durov Caps', "Durov's Cap", 'Durov Cap']}, {'funpay_match': 'ПАПАХА ХАБИБА', 'market_name': "Khabib's Papakhas", 'hours_per_unit': 24, 'aliases': ['Khabibs Papakhas', 'Khabib Papakhas']}, {'funpay_match': 'ELECTRIC SKULL', 'market_name': 'Electric Skulls', 'hours_per_unit': 24, 'aliases': ['Electric Skull']}, {'funpay_match': 'SHARP TONGUE', 'market_name': 'Sharp Tongues', 'hours_per_unit': 24, 'aliases': ['Sharp Tongue']}, {'funpay_match': 'BONDED RING', 'market_name': 'Bonded Rings', 'hours_per_unit': 24, 'aliases': ['Bonded Ring']}, {'funpay_match': 'MAGIC POTION', 'market_name': 'Magic Potions', 'hours_per_unit': 24, 'aliases': ['Magic Potion']}, {'funpay_match': 'ARTISAN BRICKS', 'market_name': 'Artisan Bricks', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'TOY BEARS', 'market_name': 'Toy Bears', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'SIGNET RING', 'market_name': 'Signet Rings', 'hours_per_unit': 24, 'aliases': ['Signet Ring']}, {'funpay_match': 'MAD PUMPKIN', 'market_name': 'Mad Pumpkins', 'hours_per_unit': 24, 'aliases': ['Mad Pumpkin']}, {'funpay_match': 'NEKO HELMETS', 'market_name': 'Neko Helmets', 'hours_per_unit': 24, 'aliases': ['Neko Helmet']}, {'funpay_match': 'KISSED FROGS', 'market_name': 'Kissed Frogs', 'hours_per_unit': 24, 'aliases': ['Kissed Frog']}, {'funpay_match': 'LOVE CANDLE', 'market_name': 'Love Candles', 'hours_per_unit': 24, 'aliases': ['Love Candle']}, {'funpay_match': 'RECORD PLAYERS', 'market_name': 'Record Players', 'hours_per_unit': 24, 'aliases': ['Record Player']}, {'funpay_match': 'SNOW MITTENS', 'market_name': 'Snow Mittens', 'hours_per_unit': 24, 'aliases': []}, {'funpay_match': 'LOW RIDERS', 'market_name': 'Low Riders', 'hours_per_unit': 24, 'aliases': ['Low Rider']}, {'funpay_match': 'FLYING BROOM', 'market_name': 'Flying Brooms', 'hours_per_unit': 24, 'aliases': ['Flying Broom']}]

DEFAULT_SETTINGS = {
    "enabled": True,
    "auto_rent": False,
    "dry_run": True,
    "reply_to_buyer": False,
    "notify_admin": True,
    "recheck_before_rent": True,
    "auto_bind_lots": True,
    "fallback_name_match": True,
    "allow_longer_if_cheaper": True,

    "max_total_ton": 10.0,
    "max_requested_days": 30,
    "max_extra_days": 365,

    "default_hours_per_unit": 24,
    "big_year_hours_per_unit": 96,

    "history_limit": 50,
}

DEFAULT_DATA = {
    "settings": DEFAULT_SETTINGS,
    "bindings": {},          # lot_id(str) -> funpay_match
    "history": [],
    "stats": {
        "orders_seen": 0,
        "matched": 0,
        "selected": 0,
        "rented": 0,
        "errors": 0,
    },
    "admin_chat_id": None,
}

LOCK = threading.RLock()
DATA: dict = {}
STOP = threading.Event()

STATE_INPUT_PREFIX = f"{CB}_INPUT_"


def _ensure_vendor_path() -> None:
    """
    Подключает приватные зависимости плагина из storage/plugins/.../vendor.
    Это позволяет ставить marketapp-api без записи в системный Python
    и без --break-system-packages (PEP 668).
    """
    try:
        VENDOR_DIR.mkdir(parents=True, exist_ok=True)
        vendor = str(VENDOR_DIR.resolve())
        if vendor not in sys.path:
            sys.path.insert(0, vendor)
        importlib.invalidate_caches()
    except Exception:
        LOGGER.debug("Не удалось подключить vendor-dir.", exc_info=True)


_ensure_vendor_path()



# ------------------------- storage -------------------------

def _deepcopy_json(obj):
    return json.loads(json.dumps(obj, ensure_ascii=False))


def _merge_settings(raw: dict | None) -> dict:
    result = dict(DEFAULT_SETTINGS)
    if isinstance(raw, dict):
        result.update(raw)
    return result


def load_data() -> dict:
    global DATA
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    raw = {}
    if DATA_PATH.exists():
        try:
            raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except Exception:
            LOGGER.exception("Не удалось прочитать data.json, использую значения по умолчанию.")

    data = _deepcopy_json(DEFAULT_DATA)
    if isinstance(raw, dict):
        data.update({k: v for k, v in raw.items() if k not in ("settings", "stats")})
        data["settings"] = _merge_settings(raw.get("settings"))
        if isinstance(raw.get("stats"), dict):
            data["stats"].update(raw["stats"])

    if not isinstance(data.get("bindings"), dict):
        data["bindings"] = {}
    if not isinstance(data.get("history"), list):
        data["history"] = []

    DATA = data
    save_data()
    return DATA


def save_data() -> None:
    with LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmp = DATA_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(DATA, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(DATA_PATH)
        try:
            os.chmod(DATA_PATH, 0o600)
        except OSError:
            pass


def s() -> dict:
    if not DATA:
        load_data()
    return DATA["settings"]


def _stat(key: str, inc: int = 1):
    with LOCK:
        DATA.setdefault("stats", {}).setdefault(key, 0)
        DATA["stats"][key] += inc
        save_data()


def _history(entry: dict):
    with LOCK:
        entry = {"ts": int(time.time()), **entry}
        DATA.setdefault("history", []).insert(0, entry)
        lim = int(s().get("history_limit", 50))
        DATA["history"] = DATA["history"][:max(5, lim)]
        save_data()


# ------------------------- matching -------------------------

def _norm(value: Any) -> str:
    x = str(value or "").lower().strip()
    x = x.replace("ё", "е").replace("’", "'").replace("`", "'")
    x = re.sub(r"[^0-9a-zа-я'\-]+", " ", x, flags=re.I)
    return re.sub(r"\s+", " ", x).strip()


def _plain(value: Any) -> str:
    return re.sub(r"[^0-9a-zа-я]+", "", _norm(value).replace("'", ""))


def _same_collection(found: str, rule: dict) -> bool:
    f = _plain(found)
    variants = [rule["market_name"], *rule.get("aliases", [])]
    return bool(f) and any(f == _plain(v) for v in variants)


def _catalog_by_marker(marker: str) -> dict | None:
    for rule in CATALOG:
        if rule["funpay_match"] == marker:
            return rule
    return None


def _rule_from_description(description: str) -> dict | None:
    desc = _norm(description)
    matches = []
    for rule in CATALOG:
        marker = _norm(rule["funpay_match"])
        if marker and marker in desc:
            matches.append((len(marker), rule))
    return max(matches, key=lambda x: x[0])[1] if matches else None


def _bind_lot(lot_id: Any, rule: dict):
    if lot_id is None:
        return
    with LOCK:
        DATA.setdefault("bindings", {})[str(lot_id)] = rule["funpay_match"]
        save_data()


def _rule_for_event(event) -> dict | None:
    lot_id = getattr(event, "lot_id", None)

    if lot_id is not None:
        marker = DATA.get("bindings", {}).get(str(lot_id))
        if marker:
            rule = _catalog_by_marker(marker)
            if rule:
                return rule

    if not s().get("fallback_name_match", True):
        return None

    rule = _rule_from_description(getattr(event.order, "description", "") or "")
    if rule and s().get("auto_bind_lots", True):
        _bind_lot(lot_id, rule)
    return rule


def _order_amount(order) -> int:
    raw = getattr(order, "amount", None)
    if raw in (None, "", 0, 0.0):
        return 1
    value = float(raw)
    if value < 1 or not value.is_integer():
        raise ValueError(f"Некорректное количество: {raw!r}. Нужное целое число >= 1.")
    return int(value)


def _requested_days(rule: dict, amount: int) -> int:
    if rule["funpay_match"] == "BIG YEAR":
        hours = int(s().get("big_year_hours_per_unit", 96)) * amount
    else:
        hours = int(s().get("default_hours_per_unit", 24)) * amount
    return max(1, int(math.ceil(hours / 24)))


# ------------------------- MarketApp parser -------------------------

@dataclass
class Offer:
    nft_address: str
    collection_name: str
    requested_days: int
    actual_days: int
    total_price: float
    source_price: float
    price_mode: str

    @property
    def extra_days(self) -> int:
        return max(0, self.actual_days - self.requested_days)


def _dump(obj: Any) -> Any:
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="python")
    if hasattr(obj, "dict"):
        try:
            return obj.dict()
        except Exception:
            pass
    if isinstance(obj, dict):
        return {k: _dump(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_dump(v) for v in obj]
    if hasattr(obj, "__dict__"):
        return {k: _dump(v) for k, v in vars(obj).items() if not k.startswith("_")}
    return obj


NAME_KEYS = (
    "collection_name", "gift_name", "nft_name", "name", "title",
    "collection", "model_name", "model"
)
ADDRESS_KEYS = ("nft_address", "address", "contract_address")
FIXED_DAYS_KEYS = ("days", "rent_days", "duration_days", "period_days")
FIXED_HOURS_KEYS = ("hours", "rent_hours", "duration_hours", "period_hours")
FIXED_SECONDS_KEYS = ("seconds", "rent_seconds", "duration_seconds", "period_seconds")
MIN_DAYS_KEYS = ("min_days", "minimum_days", "min_rent_days", "minimum_rent_days")
MAX_DAYS_KEYS = ("max_days", "maximum_days", "max_rent_days", "maximum_rent_days")
TOTAL_PRICE_KEYS = ("total_price", "rent_total", "total_rent_price", "total_cost", "cost")
DAILY_PRICE_KEYS = ("price_per_day", "daily_price", "day_price", "rent_price_per_day")
PRICE_KEYS = ("rent_price", "price", "min_price")


def _num(v: Any) -> float | None:
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        m = re.search(r"-?\d+(?:[.,]\d+)?", v.strip())
        if m:
            try:
                return float(m.group(0).replace(",", "."))
            except ValueError:
                pass
    return None


def _first_num(d: dict, keys) -> float | None:
    for k in keys:
        if k in d:
            n = _num(d.get(k))
            if n is not None:
                return n
    return None


def _first_text(d: dict, keys) -> str | None:
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _walk(node: Any, ctx: dict | None = None):
    ctx = dict(ctx or {})
    if isinstance(node, dict):
        local = dict(ctx)
        nm = _first_text(node, NAME_KEYS)
        if nm:
            local["name"] = nm
        ad = _first_text(node, ADDRESS_KEYS)
        if ad:
            local["address"] = ad
        yield node, local
        for value in node.values():
            if isinstance(value, (dict, list)):
                yield from _walk(value, local)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value, ctx)


def _duration(d: dict):
    days = _first_num(d, FIXED_DAYS_KEYS)
    if days is None:
        hours = _first_num(d, FIXED_HOURS_KEYS)
        if hours is not None:
            days = hours / 24
    if days is None:
        sec = _first_num(d, FIXED_SECONDS_KEYS)
        if sec is not None:
            days = sec / 86400

    mn = _first_num(d, MIN_DAYS_KEYS)
    mx = _first_num(d, MAX_DAYS_KEYS)

    fixed = max(1, int(math.ceil(days))) if days is not None else None
    mn = max(1, int(math.ceil(mn))) if mn is not None else None
    mx = max(1, int(math.floor(mx))) if mx is not None else None
    return fixed, mn, mx


def _offers_from_price_map(node: dict, ctx: dict, rule: dict, requested_days: int) -> list[Offer]:
    """
    Поддержка схемы вида:
      prices: {"1": 0.02, "2": 0.01}
    или
      rent_prices: {"1": 0.02, "2": 0.01}
    """
    out = []
    address = ctx.get("address")
    name = ctx.get("name", "")
    if not address or not _same_collection(name, rule):
        return out

    for key in ("prices", "rent_prices", "duration_prices"):
        mp = node.get(key)
        if not isinstance(mp, dict):
            continue
        for day_key, price_value in mp.items():
            days = _num(day_key)
            price = _num(price_value)
            if days is None or price is None:
                continue
            days = int(math.ceil(days))
            if days < requested_days:
                continue
            out.append(Offer(address, name, requested_days, days, float(price), float(price), "price_map_total"))
    return out


def _offer_from_node(node: dict, ctx: dict, rule: dict, requested_days: int) -> Offer | None:
    name = ctx.get("name", "")
    address = ctx.get("address")
    if not address or not _same_collection(name, rule):
        return None

    fixed, mn, mx = _duration(node)
    total = _first_num(node, TOTAL_PRICE_KEYS)
    daily = _first_num(node, DAILY_PRICE_KEYS)
    generic = _first_num(node, PRICE_KEYS)

    if fixed is not None:
        if fixed < requested_days:
            return None
        if total is not None:
            cost, src, mode = total, total, "explicit_total"
        elif daily is not None:
            cost, src, mode = daily * fixed, daily, "daily_x_fixed"
        elif generic is not None:
            # Если API вернул отдельную запись "2 дня / 0.01", price является ценой этого варианта.
            cost, src, mode = generic, generic, "fixed_option_total"
        else:
            return None
        return Offer(address, name, requested_days, fixed, float(cost), float(src), mode)

    actual = max(requested_days, mn or 1)
    if mx is not None and actual > mx:
        return None

    if daily is not None:
        return Offer(address, name, requested_days, actual, float(daily * actual), float(daily), "daily_x_days")

    if generic is not None and (mn is not None or mx is not None):
        return Offer(address, name, requested_days, actual, float(generic * actual), float(generic), "generic_daily_x_days")

    # Без длительности нельзя безопасно считать цену.
    return None


def extract_offers(raw: Any, rule: dict, requested_days: int) -> list[Offer]:
    obj = _dump(raw)
    offers = []
    seen = set()

    for node, ctx in _walk(obj):
        for off in _offers_from_price_map(node, ctx, rule, requested_days):
            key = (off.nft_address, off.actual_days, round(off.total_price, 12))
            if key not in seen:
                seen.add(key)
                offers.append(off)

        off = _offer_from_node(node, ctx, rule, requested_days)
        if off:
            key = (off.nft_address, off.actual_days, round(off.total_price, 12))
            if key not in seen:
                seen.add(key)
                offers.append(off)

    if not s().get("allow_longer_if_cheaper", True):
        offers = [x for x in offers if x.actual_days == requested_days]
    else:
        max_extra = int(s().get("max_extra_days", 365))
        offers = [x for x in offers if x.extra_days <= max_extra]

    # Главное правило пользователя: минимальная ИТОГОВАЯ цена, а не минимальная цена/сутки.
    offers.sort(key=lambda x: (x.total_price, x.actual_days, x.nft_address))
    return offers


# ------------------------- MarketApp client -------------------------

def sdk_installed() -> bool:
    _ensure_vendor_path()
    return importlib.util.find_spec("MarketappAPI") is not None


def api_token_present() -> bool:
    return bool(os.getenv("MARKETAPP_API_TOKEN", "").strip())


def wallet_seed_present() -> bool:
    return bool(os.getenv("MARKETAPP_WALLET_SEED", "").strip())


def ton_api_key_present() -> bool:
    return bool(os.getenv("MARKETAPP_TON_API_KEY", "").strip())


def _client(auto_pay: bool = False):
    if not sdk_installed():
        raise RuntimeError("Не установлен marketapp-api.")

    _ensure_vendor_path()
    from MarketappAPI import MarketappClient

    token = os.getenv("MARKETAPP_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Не задан MARKETAPP_API_TOKEN.")

    kwargs = {"api_token": token}

    if auto_pay:
        seed = os.getenv("MARKETAPP_WALLET_SEED", "").strip()
        api_key = os.getenv("MARKETAPP_TON_API_KEY", "").strip()
        if not seed:
            raise RuntimeError("Не задан MARKETAPP_WALLET_SEED.")
        if not api_key:
            raise RuntimeError("Не задан MARKETAPP_TON_API_KEY.")
        kwargs.update({
            "seed": seed,
            "api_key": api_key,
            "wallet_version": os.getenv("MARKETAPP_WALLET_VERSION", "V5R1").strip() or "V5R1",
        })

    return MarketappClient(**kwargs)


async def fetch_rent_gifts():
    async with _client(False) as client:
        fn = client.get_gifts_available_for_rent
        sig = inspect.signature(fn)
        params = sig.parameters
        kwargs = {}
        if "limit" in params:
            kwargs["limit"] = 1000
        return await fn(**kwargs)


async def select_best(rule: dict, requested_days: int) -> tuple[Offer, list[Offer]]:
    raw = await fetch_rent_gifts()
    offers = extract_offers(raw, rule, requested_days)
    if not offers:
        raise RuntimeError(
            f"Не нашёл конкретных предложений {rule['market_name']} на срок >= {requested_days} дн. "
            f"Проверьте API через «Диагностика»."
        )
    return offers[0], offers


def _build_rent_body(offer: Offer):
    from MarketappAPI.types.models import RentNFTBody

    fields = getattr(RentNFTBody, "model_fields", {}) or {}
    kwargs = {}

    for name in fields:
        lname = name.lower()
        if lname in ("days", "rent_days", "duration_days", "period_days", "duration"):
            kwargs[name] = offer.actual_days
        elif lname in ("hours", "rent_hours", "duration_hours"):
            kwargs[name] = offer.actual_days * 24
        elif lname in ("price", "total_price", "rent_price", "amount"):
            kwargs[name] = offer.total_price
        elif lname in ("nft_address", "address"):
            kwargs[name] = offer.nft_address

    return RentNFTBody(**kwargs)


async def rent_offer(offer: Offer):
    async with _client(True) as client:
        fn = client.rent_nft
        sig = inspect.signature(fn)
        params = sig.parameters
        kwargs = {}

        if "nft_address" in params:
            kwargs["nft_address"] = offer.nft_address
        elif "address" in params:
            kwargs["address"] = offer.nft_address

        if "days" in params:
            kwargs["days"] = offer.actual_days
        elif "rent_days" in params:
            kwargs["rent_days"] = offer.actual_days
        elif "duration_days" in params:
            kwargs["duration_days"] = offer.actual_days

        if "price" in params:
            kwargs["price"] = offer.total_price

        if "auto_pay" in params:
            kwargs["auto_pay"] = True

        body_name = next((x for x in ("body", "data", "payload", "rent_body") if x in params), None)
        if body_name:
            kwargs[body_name] = _build_rent_body(offer)

        try:
            return await fn(**kwargs)
        except TypeError as exc:
            raise RuntimeError(
                f"Не подошла сигнатура rent_nft {sig}. Автооплата остановлена до адаптации SDK."
            ) from exc


# ------------------------- FunPay lots -------------------------

def auto_bind_lots(cardinal) -> tuple[int, list[str]]:
    """
    Привязывает уже существующие лоты FunPay.
    Никаких ID в описание добавлять не надо.
    """
    try:
        cardinal.update_lots_and_categories()
    except Exception:
        LOGGER.debug("Не удалось обновить tg_profile перед привязкой.", exc_info=True)

    profile = getattr(cardinal, "tg_profile", None) or getattr(cardinal, "profile", None) or getattr(cardinal, "curr_profile", None)
    if not profile:
        raise RuntimeError("Профиль FunPay ещё не загружен.")

    if hasattr(profile, "get_common_lots"):
        lots = list(profile.get_common_lots())
    else:
        lots = list(profile.get_lots())

    bound = 0
    found_markers = set()

    for lot in lots:
        desc = getattr(lot, "description", "") or ""
        rule = _rule_from_description(desc)
        if not rule:
            continue
        lot_id = getattr(lot, "id", None) or getattr(lot, "offer_id", None)
        if lot_id is None:
            continue
        DATA["bindings"][str(lot_id)] = rule["funpay_match"]
        found_markers.add(rule["funpay_match"])
        bound += 1

    save_data()
    missing = [r["funpay_match"] for r in CATALOG if r["funpay_match"] not in found_markers]
    return bound, missing


# ------------------------- order processing -------------------------

def _admin(text: str):
    if not s().get("notify_admin", True):
        return
    cardinal = _CARDINAL
    if not cardinal or not getattr(cardinal, "telegram", None):
        return
    chat_id = DATA.get("admin_chat_id")
    if not chat_id:
        return
    try:
        cardinal.telegram.bot.send_message(chat_id, text)
    except Exception:
        LOGGER.debug("Не удалось отправить админ-уведомление.", exc_info=True)


def _buyer(cardinal, order, text: str):
    chat = cardinal.account.get_chat_by_name(order.buyer_username)
    chat_id = chat.id if chat else order.chat_id
    cardinal.send_message(chat_id, text, order.buyer_username)


def _already_processing(order_id: str) -> bool:
    for row in DATA.get("history", []):
        if str(row.get("order_id")) == str(order_id) and row.get("status") in ("processing", "rented"):
            return True
    return False


async def process_order_async(cardinal, event):
    order = event.order
    order_id = str(order.id)

    if _already_processing(order_id):
        LOGGER.info("Заказ #%s уже обрабатывался, пропуск.", order_id)
        return

    _stat("orders_seen")

    rule = _rule_for_event(event)
    if not rule:
        LOGGER.info("Заказ #%s не относится к встроенным 78 лотам.", order_id)
        return

    _stat("matched")
    amount = _order_amount(order)
    days = _requested_days(rule, amount)

    if days > int(s().get("max_requested_days", 30)):
        raise RuntimeError(f"Срок {days} дн. превышает лимит плагина.")

    _history({
        "order_id": order_id,
        "status": "processing",
        "market_name": rule["market_name"],
        "amount": amount,
        "requested_days": days,
        "lot_id": getattr(event, "lot_id", None),
    })

    best, offers = await select_best(rule, days)
    _stat("selected")

    if best.total_price > float(s().get("max_total_ton", 10.0)):
        raise RuntimeError(
            f"Минимальная итоговая цена {best.total_price:g} TON выше лимита "
            f"{float(s().get('max_total_ton', 10.0)):g} TON."
        )

    LOGGER.info(
        "Заказ #%s: %s, нужно %s дн., выбрано %s дн. за %s TON, nft=%s, вариантов=%s",
        order_id, rule["market_name"], days, best.actual_days, best.total_price,
        best.nft_address, len(offers)
    )

    _history({
        "order_id": order_id,
        "status": "selected",
        "market_name": rule["market_name"],
        "requested_days": days,
        "selected": asdict(best),
        "candidates": len(offers),
    })

    if s().get("reply_to_buyer", False):
        extra = f"\n🎁 Срок выдачи: {best.actual_days} дн." if best.actual_days > days else ""
        _buyer(cardinal, order,
               f"✅ Найден {rule['market_name']}.\n"
               f"Оплаченный срок: {days} дн.{extra}")

    _admin(
        f"🎁 <b>Заказ #{html.escape(order_id)}</b>\n"
        f"{html.escape(rule['market_name'])}\n"
        f"Нужно: <b>{days} дн.</b>\n"
        f"Выбрано: <b>{best.actual_days} дн.</b>\n"
        f"Цена: <b>{best.total_price:g} TON</b>\n"
        f"Режим: {'DRY RUN' if s().get('dry_run', True) else 'AUTO'}"
    )

    if not s().get("auto_rent", False) or s().get("dry_run", True):
        return

    # Свежий запрос прямо перед оплатой.
    if s().get("recheck_before_rent", True):
        best, _ = await select_best(rule, days)
        if best.total_price > float(s().get("max_total_ton", 10.0)):
            raise RuntimeError("После перепроверки цена превысила лимит.")

    await rent_offer(best)
    _stat("rented")

    _history({
        "order_id": order_id,
        "status": "rented",
        "market_name": rule["market_name"],
        "requested_days": days,
        "selected": asdict(best),
    })

    _admin(
        f"✅ <b>Аренда оплачена</b>\n"
        f"Заказ #{html.escape(order_id)}\n"
        f"{html.escape(rule['market_name'])}\n"
        f"{best.actual_days} дн. / {best.total_price:g} TON"
    )


def process_order(cardinal, event):
    try:
        asyncio.run(process_order_async(cardinal, event))
    except Exception as exc:
        _stat("errors")
        LOGGER.exception("Ошибка заказа #%s: %s", getattr(event.order, "id", "?"), exc)
        _history({
            "order_id": str(getattr(event.order, "id", "?")),
            "status": "error",
            "error": str(exc),
        })
        _admin(f"❌ <b>MarketApp Smart Rent</b>\nЗаказ #{html.escape(str(getattr(event.order, 'id', '?')))}\n{html.escape(str(exc))}")


def on_new_order(cardinal, event, *args):
    if STOP.is_set() or not s().get("enabled", True):
        return
    Thread = threading.Thread
    Thread(target=process_order, args=(cardinal, event), daemon=True,
           name=f"MSR-{getattr(event.order, 'id', 'order')}").start()


# ------------------------- Telegram settings UI -------------------------

_CARDINAL = None


def _dot(v: bool) -> str:
    return "🟢" if v else "🔴"


def _remember_admin(chat_id: int):
    DATA["admin_chat_id"] = chat_id
    save_data()


def _settings_text() -> str:
    st = DATA.get("stats", {})
    return (
        f"<b>⚙️ MarketApp Smart Rent v{VERSION}</b>\n\n"
        f"Плагин: {_dot(s()['enabled'])}\n"
        f"Автоаренда: {_dot(s()['auto_rent'])}\n"
        f"Dry-run: {_dot(s()['dry_run'])}\n"
        f"Длиннее, если дешевле: {_dot(s()['allow_longer_if_cheaper'])}\n"
        f"Перепроверка перед оплатой: {_dot(s()['recheck_before_rent'])}\n\n"
        f"🔗 Привязано lot_id: <b>{len(DATA.get('bindings', {}))}</b>\n"
        f"📦 Каталог: <b>{len(CATALOG)}</b> лотов встроен\n"
        f"💰 Лимит одной аренды: <b>{s()['max_total_ton']:g} TON</b>\n"
        f"📅 Макс. срок заказа: <b>{s()['max_requested_days']} дн.</b>\n\n"
        f"📊 Заказов: {st.get('orders_seen', 0)} | "
        f"выбрано: {st.get('selected', 0)} | "
        f"арендовано: {st.get('rented', 0)} | "
        f"ошибок: {st.get('errors', 0)}"
    )


def _main_kb():
    from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
    from tg_bot import CBT
    kb = K()
    kb.row(
        B(f"{_dot(s()['enabled'])} Работа", callback_data=f"{CB}:toggle:enabled"),
        B(f"{_dot(s()['auto_rent'])} Автоаренда", callback_data=f"{CB}:toggle:auto_rent"),
    )
    kb.row(
        B(f"{_dot(s()['dry_run'])} Dry-run", callback_data=f"{CB}:toggle:dry_run"),
        B(f"{_dot(s()['recheck_before_rent'])} Перепроверка", callback_data=f"{CB}:toggle:recheck_before_rent"),
    )
    kb.row(
        B(f"{_dot(s()['allow_longer_if_cheaper'])} Дешевле > срок", callback_data=f"{CB}:toggle:allow_longer_if_cheaper"),
        B(f"{_dot(s()['reply_to_buyer'])} Писать клиенту", callback_data=f"{CB}:toggle:reply_to_buyer"),
    )
    kb.row(
        B("💰 Лимиты", callback_data=f"{CB}:limits"),
        B("🔗 Лоты / lot_id", callback_data=f"{CB}:lots"),
    )
    kb.row(
        B("🩺 Диагностика", callback_data=f"{CB}:diag"),
        B("📊 История", callback_data=f"{CB}:history"),
    )
    kb.row(
        B("🔄 Обновить", callback_data=f"{CB}:main"),
        B("◀️ Назад", callback_data=f"{CBT.EDIT_PLUGIN}:{UUID}:0"),
    )
    return kb


def _limits_text() -> str:
    return (
        "<b>💰 Лимиты и сроки</b>\n\n"
        f"Макс. стоимость одной аренды: <b>{s()['max_total_ton']:g} TON</b>\n"
        f"Макс. оплаченный срок: <b>{s()['max_requested_days']} дн.</b>\n"
        f"Макс. бонус сверх срока: <b>{s()['max_extra_days']} дн.</b>\n"
        f"Обычные лоты, 1 шт.: <b>{s()['default_hours_per_unit']} ч.</b>\n"
        f"BIG YEAR, 1 шт.: <b>{s()['big_year_hours_per_unit']} ч.</b>\n\n"
        "Пример: клиент купил 1 сутки. Если 2 суток стоят дешевле 1 суток, "
        "будут выбраны 2 суток — если включено «Дешевле > срок»."
    )


def _limits_kb():
    from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
    kb = K()
    kb.add(B("✏️ Макс. TON", callback_data=f"{CB}:set:max_total_ton"))
    kb.add(B("✏️ Макс. дней заказа", callback_data=f"{CB}:set:max_requested_days"))
    kb.add(B("✏️ Макс. бонусных дней", callback_data=f"{CB}:set:max_extra_days"))
    kb.add(B("✏️ Часов за 1 шт.", callback_data=f"{CB}:set:default_hours_per_unit"))
    kb.add(B("✏️ BIG YEAR: часов за 1 шт.", callback_data=f"{CB}:set:big_year_hours_per_unit"))
    kb.add(B("◀️ Назад", callback_data=f"{CB}:main"))
    return kb


def _lots_text(missing: list[str] | None = None) -> str:
    text = (
        "<b>🔗 Лоты FunPay</b>\n\n"
        f"Встроенный каталог: <b>{len(CATALOG)}</b>\n"
        f"Привязано lot_id: <b>{len(DATA.get('bindings', {}))}</b>\n\n"
        "Никакие ID в описание FunPay добавлять не нужно. "
        "Кнопка ниже сама просканирует ваши уже выставленные лоты и запомнит их lot_id."
    )
    if missing is not None:
        text += f"\n\nПосле сканирования не найдено: <b>{len(missing)}</b>."
        if missing:
            text += "\n" + "\n".join(f"• {html.escape(x)}" for x in missing[:15])
            if len(missing) > 15:
                text += f"\n… ещё {len(missing)-15}"
    return text


def _lots_kb():
    from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
    kb = K()
    kb.add(B("🔗 Автопривязать мои лоты", callback_data=f"{CB}:bind"))
    kb.add(B(f"{_dot(s()['auto_bind_lots'])} Автопривязка новых", callback_data=f"{CB}:toggle:auto_bind_lots"))
    kb.add(B(f"{_dot(s()['fallback_name_match'])} Резерв по названию", callback_data=f"{CB}:toggle:fallback_name_match"))
    kb.add(B("🗑 Сбросить привязки", callback_data=f"{CB}:reset_bindings"))
    kb.add(B("◀️ Назад", callback_data=f"{CB}:main"))
    return kb


def _diag_text(extra: str = "") -> str:
    return (
        "<b>🩺 Диагностика</b>\n\n"
        f"marketapp-api: {'✅ установлен' if sdk_installed() else '❌ не установлен'}\n"
        f"MARKETAPP_API_TOKEN: {'✅ найден' if api_token_present() else '❌ не задан'}\n"
        f"TON wallet seed: {'✅ найден' if wallet_seed_present() else '❌ не задан'}\n"
        f"TON API key: {'✅ найден' if ton_api_key_present() else '❌ не задан'}\n\n"
        "Seed-фраза и токены здесь никогда не показываются."
        + (f"\n\n{extra}" if extra else "")
    )


def _diag_kb():
    from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
    kb = K()
    kb.add(B("🧪 Проверить MarketApp API", callback_data=f"{CB}:test_api"))
    if not sdk_installed():
        kb.add(B("📦 Установить marketapp-api", callback_data=f"{CB}:install_sdk_ask"))
    kb.add(B("🔍 Сигнатуры SDK", callback_data=f"{CB}:sdk_info"))
    kb.add(B("◀️ Назад", callback_data=f"{CB}:main"))
    return kb


def _history_text() -> str:
    rows = DATA.get("history", [])[:10]
    if not rows:
        body = "История пока пуста."
    else:
        lines = []
        for x in rows:
            t = time.strftime("%d.%m %H:%M", time.localtime(x.get("ts", 0)))
            status = x.get("status", "?")
            oid = x.get("order_id", "?")
            name = x.get("market_name", "")
            price = ""
            sel = x.get("selected")
            if isinstance(sel, dict) and sel.get("total_price") is not None:
                price = f" / {sel['total_price']:g} TON"
            lines.append(f"{t} — #{html.escape(str(oid))} — {html.escape(status)} — {html.escape(str(name))}{price}")
        body = "\n".join(lines)
    return "<b>📊 Последние операции</b>\n\n" + body


def _history_kb():
    from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
    kb = K()
    kb.add(B("🗑 Очистить историю", callback_data=f"{CB}:clear_history"))
    kb.add(B("◀️ Назад", callback_data=f"{CB}:main"))
    return kb


def init_telegram(cardinal, *args):
    global _CARDINAL
    _CARDINAL = cardinal
    load_data()

    if not getattr(cardinal, "telegram", None):
        LOGGER.info("Telegram-ПУ отключено; бизнес-логика плагина остаётся доступной.")
        return

    tg = cardinal.telegram
    bot = tg.bot

    from tg_bot import CBT
    from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B

    def enabled_now():
        pl = cardinal.plugins.get(UUID)
        return bool(pl and pl.enabled)

    def edit(call, text, kb):
        _remember_admin(call.message.chat.id)
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=kb)
        bot.answer_callback_query(call.id)

    def open_settings(call):
        edit(call, _settings_text(), _main_kb())

    def open_main(call):
        edit(call, _settings_text(), _main_kb())

    def toggle(call):
        key = call.data.split(":", 2)[2]
        if key not in s() or not isinstance(s()[key], bool):
            bot.answer_callback_query(call.id, "Неизвестная настройка", show_alert=True)
            return
        s()[key] = not s()[key]
        save_data()
        edit(call, _settings_text(), _main_kb())

    def limits(call):
        edit(call, _limits_text(), _limits_kb())

    def lots(call):
        edit(call, _lots_text(), _lots_kb())

    def diag(call):
        edit(call, _diag_text(), _diag_kb())

    def history(call):
        edit(call, _history_text(), _history_kb())

    def bind(call):
        bot.answer_callback_query(call.id, "Сканирую лоты…")
        try:
            count, missing = auto_bind_lots(cardinal)
            bot.edit_message_text(
                _lots_text(missing) + f"\n\n✅ Привязано: <b>{count}</b>",
                call.message.chat.id, call.message.id, reply_markup=_lots_kb()
            )
        except Exception as exc:
            bot.edit_message_text(
                _lots_text() + f"\n\n❌ {html.escape(str(exc))}",
                call.message.chat.id, call.message.id, reply_markup=_lots_kb()
            )

    def reset_bindings(call):
        DATA["bindings"] = {}
        save_data()
        edit(call, _lots_text() + "\n\n✅ Привязки сброшены.", _lots_kb())

    def clear_history(call):
        DATA["history"] = []
        save_data()
        edit(call, _history_text(), _history_kb())

    def ask_set(call):
        key = call.data.split(":", 2)[2]
        labels = {
            "max_total_ton": "Введите максимальную стоимость одной аренды в TON, например 2.5",
            "max_requested_days": "Введите максимальный срок заказа в днях, например 30",
            "max_extra_days": "Введите максимум бонусных дней сверх оплаченного срока, например 30",
            "default_hours_per_unit": "Введите, сколько часов даёт 1 шт. обычного лота, например 24",
            "big_year_hours_per_unit": "Введите, сколько часов даёт 1 шт. BIG YEAR, например 96",
        }
        if key not in labels:
            bot.answer_callback_query(call.id, "Неизвестный параметр", show_alert=True)
            return
        msg = bot.send_message(call.message.chat.id, labels[key])
        tg.set_state(call.message.chat.id, msg.id, call.from_user.id, STATE_INPUT_PREFIX + key)
        bot.answer_callback_query(call.id)

    def input_handler(message):
        state = tg.get_state(message.chat.id, message.from_user.id)
        if not state or not str(state.get("state", "")).startswith(STATE_INPUT_PREFIX):
            return
        key = state["state"][len(STATE_INPUT_PREFIX):]
        raw = (message.text or "").strip().replace(",", ".")
        try:
            if key == "max_total_ton":
                val = float(raw)
                if val <= 0 or val > 10000:
                    raise ValueError
            else:
                val = int(float(raw))
                if val <= 0 or val > 10000:
                    raise ValueError
            s()[key] = val
            save_data()
            tg.clear_state(message.chat.id, message.from_user.id, True)
            bot.reply_to(message, f"✅ Сохранено: <b>{html.escape(str(val))}</b>",
                         reply_markup=K().add(B("◀️ К лимитам", callback_data=f"{CB}:limits")))
        except Exception:
            bot.reply_to(message, "❌ Неверное значение. Попробуйте ещё раз.")

    def test_api(call):
        _remember_admin(call.message.chat.id)
        bot.answer_callback_query(call.id, "Проверяю API…")

        def worker():
            try:
                raw = asyncio.run(fetch_rent_gifts())
                dumped = _dump(raw)
                if isinstance(dumped, dict):
                    hint = ", ".join(list(dumped.keys())[:10])
                    summary = f"Тип: dict; поля: {html.escape(hint)}"
                elif isinstance(dumped, list):
                    summary = f"Тип: list; элементов: {len(dumped)}"
                else:
                    summary = f"Тип ответа: {html.escape(type(dumped).__name__)}"
                bot.send_message(call.message.chat.id, "✅ MarketApp API отвечает.\n" + summary)
            except Exception as exc:
                bot.send_message(call.message.chat.id, "❌ MarketApp API: " + html.escape(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def sdk_info(call):
        if not sdk_installed():
            edit(call, _diag_text("SDK не установлен."), _diag_kb())
            return
        try:
            _ensure_vendor_path()
            from MarketappAPI import MarketappClient
            client = MarketappClient(api_token="x")
            sig1 = inspect.signature(client.get_gifts_available_for_rent)
            sig2 = inspect.signature(client.rent_nft)
            extra = (
                f"<code>get_gifts_available_for_rent{html.escape(str(sig1))}</code>\n"
                f"<code>rent_nft{html.escape(str(sig2))}</code>"
            )
        except Exception as exc:
            extra = "Ошибка чтения SDK: " + html.escape(str(exc))
        edit(call, _diag_text(extra), _diag_kb())

    def install_sdk_ask(call):
        kb = K()
        kb.row(
            B("✅ Установить", callback_data=f"{CB}:install_sdk"),
            B("❌ Отмена", callback_data=f"{CB}:diag"),
        )
        edit(call,
             "<b>📦 Установка marketapp-api</b>\n\n"
             "SDK будет установлен в приватную папку самого плагина, а не в системный Python. "
             "Это совместимо с PEP 668 / externally-managed-environment. "
             "После установки лучше перезапустить Cardinal.",
             kb)

    def install_sdk(call):
        bot.answer_callback_query(call.id, "Устанавливаю…")

        def worker():
            try:
                # Constraints защищает старый стек FPC от urllib3 2.x.
                with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as f:
                    f.write("urllib3<2\n")
                    constraints = f.name
                VENDOR_DIR.mkdir(parents=True, exist_ok=True)
                cmd = [
                    sys.executable, "-m", "pip", "install", "-U",
                    "--prefer-binary",
                    "--timeout", "120",
                    "--retries", "8",
                    "--target", str(VENDOR_DIR.resolve()),
                    "marketapp-api", "-c", constraints
                ]
                # На медленных VPS установка pytoniq/curl_cffi и других wheel-зависимостей
                # может занимать заметно больше трёх минут. 15 минут — это общий
                # предохранитель процесса, а сетевой timeout/retries задаются pip выше.
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
                try:
                    os.unlink(constraints)
                except OSError:
                    pass
                if proc.returncode == 0:
                    _ensure_vendor_path()
                    ok = sdk_installed()
                    bot.send_message(
                        call.message.chat.id,
                        ("✅ marketapp-api установлен в приватную папку плагина. "
                         "Перезапустите Cardinal." if ok else
                         "⚠️ pip завершился успешно, но SDK пока не обнаружен. Перезапустите Cardinal.")
                    )
                else:
                    tail = (proc.stderr or proc.stdout or "")[-1600:]
                    hint = ""
                    if "externally-managed-environment" in tail.lower():
                        hint = ("\n\nПлагин уже использует --target и не должен писать в системный Python. "
                                "Если эта ошибка осталась, пришлите полный вывод диагностики.")
                    bot.send_message(
                        call.message.chat.id,
                        "❌ pip завершился с ошибкой:\n<code>" + html.escape(tail) + "</code>" + hint
                    )
            except Exception as exc:
                bot.send_message(call.message.chat.id, "❌ " + html.escape(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def cmd_status(message):
        _remember_admin(message.chat.id)
        bot.send_message(message.chat.id, _settings_text(), reply_markup=_main_kb())

    def cmd_bind(message):
        _remember_admin(message.chat.id)
        try:
            count, missing = auto_bind_lots(cardinal)
            bot.send_message(message.chat.id,
                             f"✅ Привязано lot_id: <b>{count}</b>\nНе найдено: <b>{len(missing)}</b>",
                             reply_markup=_lots_kb())
        except Exception as exc:
            bot.send_message(message.chat.id, "❌ " + html.escape(str(exc)))

    tg.cbq_handler(open_settings, lambda c: c.data.startswith(f"{CBT.PLUGIN_SETTINGS}:{UUID}"))
    tg.cbq_handler(open_main, lambda c: c.data == f"{CB}:main")
    tg.cbq_handler(toggle, lambda c: c.data.startswith(f"{CB}:toggle:"))
    tg.cbq_handler(limits, lambda c: c.data == f"{CB}:limits")
    tg.cbq_handler(lots, lambda c: c.data == f"{CB}:lots")
    tg.cbq_handler(diag, lambda c: c.data == f"{CB}:diag")
    tg.cbq_handler(history, lambda c: c.data == f"{CB}:history")
    tg.cbq_handler(bind, lambda c: c.data == f"{CB}:bind")
    tg.cbq_handler(reset_bindings, lambda c: c.data == f"{CB}:reset_bindings")
    tg.cbq_handler(clear_history, lambda c: c.data == f"{CB}:clear_history")
    tg.cbq_handler(ask_set, lambda c: c.data.startswith(f"{CB}:set:"))
    tg.cbq_handler(test_api, lambda c: c.data == f"{CB}:test_api")
    tg.cbq_handler(sdk_info, lambda c: c.data == f"{CB}:sdk_info")
    tg.cbq_handler(install_sdk_ask, lambda c: c.data == f"{CB}:install_sdk_ask")
    tg.cbq_handler(install_sdk, lambda c: c.data == f"{CB}:install_sdk")

    tg.msg_handler(input_handler, func=lambda m: (
        (st := tg.get_state(m.chat.id, m.from_user.id)) is not None
        and str(st.get("state", "")).startswith(STATE_INPUT_PREFIX)
    ))
    tg.msg_handler(cmd_status, commands=["msr", "msr_status"])
    tg.msg_handler(cmd_bind, commands=["msr_bind"])

    cardinal.add_telegram_commands(UUID, [
        ("msr", "настройки MarketApp Smart Rent", True),
        ("msr_status", "статус MarketApp Smart Rent", False),
        ("msr_bind", "автопривязать лоты FunPay", False),
    ])

    LOGGER.info("MarketApp Smart Rent v%s: Telegram-настройки зарегистрированы.", VERSION)


def post_init(cardinal, *args):
    global _CARDINAL
    _CARDINAL = cardinal
    if not DATA:
        load_data()

    if s().get("auto_bind_lots", True):
        try:
            count, missing = auto_bind_lots(cardinal)
            LOGGER.info("Автопривязка FunPay: %s лотов, не найдено %s.", count, len(missing))
        except Exception:
            LOGGER.debug("Автопривязка при старте не удалась.", exc_info=True)


def on_delete(cardinal, call):
    STOP.set()
    # Данные намеренно не удаляем: при переустановке настройки и lot_id сохранятся.
    LOGGER.info("Плагин удаляется. Данные оставлены в %s.", DATA_DIR)


BIND_TO_DELETE = on_delete
BIND_TO_PRE_INIT = [init_telegram]
BIND_TO_POST_INIT = [post_init]
BIND_TO_NEW_ORDER = [on_new_order]
