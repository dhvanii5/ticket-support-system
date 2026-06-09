from rest_framework import serializers

# Serializers are no longer needed for the location app.
# The views in locations/views.py return plain Python dicts directly from
# the LocationService, which are serialized by DRF's Response automatically.