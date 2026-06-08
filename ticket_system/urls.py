from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import TemplateView

schema_view = get_schema_view(
    openapi.Info(
        title="Support Ticket API",
        default_version='v1',
        description="Support Ticket System API",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/locations/', include('locations.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/tickets/', include('tickets.urls')),
    path('api/audit/', include('audit.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('city-selector/', TemplateView.as_view(template_name='city_selector.html')),
]