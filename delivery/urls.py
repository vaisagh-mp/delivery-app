from django.urls import path
from .views import CustomerAddressListView, CustomerAddressUploadView

urlpatterns = [
    path("customer-addresses/", CustomerAddressListView.as_view(), name="customer_addresses"),
    path("upload-customer-addresses/", CustomerAddressUploadView.as_view(), name="upload_customer_addresses"),
]
