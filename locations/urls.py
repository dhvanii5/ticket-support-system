from django.urls import path
from .views import CountryListView, StateListView, CityListView

urlpatterns = [
    path("countries/", CountryListView.as_view(), name="location-countries"),
    path("states/", StateListView.as_view(), name="location-states"),
    path("cities/", CityListView.as_view(), name="location-cities"),
]