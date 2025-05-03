from django.urls import path
from .views import CustomerAddressListView, CustomerAddressUploadView, GenerateRoutePDFView

urlpatterns = [
    path("customer-addresses/", CustomerAddressListView.as_view(), name="customer_addresses"),
    path("generate-pdf/", GenerateRoutePDFView.as_view(), name="generate_pdf"),
    path("upload-customer-addresses/", CustomerAddressUploadView.as_view(), name="upload_customer_addresses"),
]
