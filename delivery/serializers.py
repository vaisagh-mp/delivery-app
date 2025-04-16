from rest_framework import serializers
from .models import CustomerAddress

class ExcelUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = '__all__'  # Returns all fields including lat/lng
