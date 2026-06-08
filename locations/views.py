from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Country, State, City
from .serializers import CountrySerializer, StateSerializer, CitySerializer

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]

class StateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StateSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = State.objects.all()
        country_id = self.request.query_params.get('country_id')
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        return queryset

class CityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = City.objects.all()
        state_id = self.request.query_params.get('state_id')
        if state_id:
            queryset = queryset.filter(state_id=state_id)
        return queryset