from django.db import models
from .utils import get_lat_lon  # Import your geocoding utility

class CustomerAddress(models.Model):
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=20, blank=True, null=True)
    alt_contact_no = models.CharField(max_length=20, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.latitude is None or self.longitude is None:
            lat, lng = get_lat_lon(self.address)
            self.latitude = lat
            self.longitude = lng
        super().save(*args, **kwargs)

    def __str__(self):
        return self.address


class OptimizedRoute(models.Model):
    office_address = models.CharField(max_length=255)
    delivery_addresses = models.ManyToManyField(CustomerAddress)
    route_data = models.JSONField()  # Stores the full response from Google Directions API
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Route from {self.office_address} covering {self.delivery_addresses.count()} stops"
