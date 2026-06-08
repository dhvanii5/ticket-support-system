from rest_framework.routers import DefaultRouter
from .views import CountryViewSet, StateViewSet, CityViewSet

router = DefaultRouter()
router.register('countries', CountryViewSet)
router.register('states', StateViewSet, basename='state')
router.register('cities', CityViewSet, basename='city')

urlpatterns = router.urls