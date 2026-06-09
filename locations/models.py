from django.db import models

# Location data is now served dynamically via the CountriesNow API.
# See locations/services.py for the proxy + caching implementation.
# There are no local Country, State, or City database tables.