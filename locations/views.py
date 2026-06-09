from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from . import services
from .services import LocationAPIError


class CountryListView(APIView):
    """
    GET /api/locations/countries/
    Returns all countries from CountriesNow (cached 24 h).
    Response: [{id, name, code}, ...]
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            countries = services.get_countries()
        except LocationAPIError as exc:
            return Response({"error": str(exc)}, status=503)
        return Response(countries)


class StateListView(APIView):
    """
    GET /api/locations/states/?country_id=<country_name>
    Returns states for the given country (cached 24 h).
    Response: [{id, name, country}, ...]
    """
    permission_classes = [AllowAny]

    def get(self, request):
        country_id = request.query_params.get("country_id", "").strip()
        if not country_id:
            return Response(
                {"error": "country_id query parameter is required."},
                status=400,
            )
        try:
            states = services.get_states(country_id)
        except LocationAPIError as exc:
            return Response({"error": str(exc)}, status=503)
        return Response(states)


class CityListView(APIView):
    """
    GET /api/locations/cities/?state_id=<state_name>[&country_id=<country_name>]
    Returns cities for the given state (cached 24 h).

    country_id is optional — if omitted, the service resolves the parent country
    from its internal reverse-map cache (populated when states were last fetched).
    Response: [{id, name, state}, ...]
    """
    permission_classes = [AllowAny]

    def get(self, request):
        state_id = request.query_params.get("state_id", "").strip()
        country_id = request.query_params.get("country_id", "").strip() or None
        if not state_id:
            return Response(
                {"error": "state_id query parameter is required."},
                status=400,
            )
        try:
            cities = services.get_cities(state_id, country_id)
        except LocationAPIError as exc:
            return Response({"error": str(exc)}, status=503)
        return Response(cities)