"""
Location service — proxies CountriesNow API with Django file-based caching.

Data flow:
  CountriesNow → (cache 24h) → get_countries / get_states / get_cities
  Views call these helpers; no local Country/State/City DB tables exist.

ID convention (important — matches what city_selector.html and tickets use):
  country id  = country name string  e.g. "India"
  state   id  = state name string    e.g. "Gujarat"
  city    id  = city name string     e.g. "Surat"

When states for a country are fetched, we also cache a reverse mapping
(state_name → country_name) so the cities endpoint can look up the
country without requiring the frontend to pass it explicitly.
"""

import requests
from django.core.cache import cache
from django.conf import settings

API_BASE = getattr(settings, "LOCATION_API_BASE", "https://countriesnow.space/api/v0.1")
CACHE_TTL = getattr(settings, "LOCATION_CACHE_TTL", 86400)
_TIMEOUT = 10  # seconds per HTTP request


class LocationAPIError(Exception):
    """Raised when the CountriesNow API returns an error or is unreachable."""


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_countries():
    """
    Return a list of dicts: [{id, name, code}, ...].
    Results are cached for CACHE_TTL seconds.
    """
    cache_key = "location:countries"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = requests.get(f"{API_BASE}/countries/iso", timeout=_TIMEOUT)
        resp.raise_for_status()
        raw = resp.json().get("data", [])
    except requests.RequestException as exc:
        raise LocationAPIError(f"Failed to fetch countries: {exc}") from exc

    countries = [
        {
            "id": item["name"],
            "name": item["name"],
            "code": item.get("Iso2", ""),
        }
        for item in raw
        if item.get("name") and item.get("Iso2")
    ]

    cache.set(cache_key, countries, CACHE_TTL)
    return countries


def get_states(country_name: str):
    """
    Return a list of dicts: [{id, name, country}, ...] for the given country.

    Side-effect: caches a reverse mapping  location:state_country:{state_name}
    so that get_cities() can discover the parent country for a state without
    the caller having to pass it explicitly.
    """
    if not country_name:
        return []

    cache_key = f"location:states:{country_name}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = requests.post(
            f"{API_BASE}/countries/states",
            json={"country": country_name},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        raw_states = resp.json().get("data", {}).get("states", [])
    except requests.RequestException as exc:
        raise LocationAPIError(f"Failed to fetch states for '{country_name}': {exc}") from exc

    states = []
    for item in raw_states:
        name = (item.get("name") or "").strip()
        if not name:
            continue
        states.append({"id": name, "name": name, "country": country_name})
        # Reverse map: state name → country name (used by get_cities)
        cache.set(f"location:state_country:{name}", country_name, CACHE_TTL)

    cache.set(cache_key, states, CACHE_TTL)
    return states


def get_cities(state_name: str, country_name: str = None):
    """
    Return a list of dicts: [{id, name, state}, ...] for the given state.

    country_name is optional — if not supplied, it is looked up from the
    reverse-map cache that was populated when get_states() was called for
    the parent country.  Returns [] if country cannot be resolved.
    """
    if not state_name:
        return []

    if not country_name:
        country_name = cache.get(f"location:state_country:{state_name}")

    if not country_name:
        # Cannot query CountriesNow without knowing the parent country.
        return []

    cache_key = f"location:cities:{country_name}:{state_name}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = requests.post(
            f"{API_BASE}/countries/state/cities",
            json={"country": country_name, "state": state_name},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        raw_cities = resp.json().get("data", [])
    except requests.RequestException as exc:
        raise LocationAPIError(
            f"Failed to fetch cities for '{state_name}', '{country_name}': {exc}"
        ) from exc

    cities = [
        {"id": city, "name": city, "state": state_name}
        for city in raw_cities
        if isinstance(city, str) and city.strip()
    ]

    cache.set(cache_key, cities, CACHE_TTL)
    return cities
