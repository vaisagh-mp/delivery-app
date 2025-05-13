from rest_framework.views import APIView
import pandas as pd
from datetime import datetime
import io
from weasyprint import HTML
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status, generics
from .models import CustomerAddress
from .serializers import CustomerAddressSerializer, ExcelUploadSerializer



class CustomerAddressListView(generics.ListAPIView):
    queryset = CustomerAddress.objects.all()
    serializer_class = CustomerAddressSerializer


class CustomerAddressUploadView(APIView):
    def post(self, request):
        serializer = ExcelUploadSerializer(data=request.data)
        if serializer.is_valid():
            excel_file = request.FILES['file']
            try:
                df = pd.read_excel(excel_file)
                df.columns = df.columns.str.strip()  # Clean column names

                # Delete all existing data before inserting new rows
                CustomerAddress.objects.all().delete()

                for _, row in df.iterrows():
                    brand = str(row.get("Unnamed: 6", "")).strip()
                    article = str(row.get("Unnamed: 7", "")).strip()
                    product_name = str(row.get("Unnamed: 8", "")).strip()
                    Qty = str(row.get("Unnamed: 10", "")).strip()
                    customer_name = str(row.get("Unnamed: 12", "")).strip()
                    address = str(row.get("Unnamed: 13", "")).strip()
                    contact_no = str(row.get("Unnamed: 14", "")).strip()
                    alt_contact_no = str(row.get("Unnamed: 15", "")).strip()
                    pincode = str(row.get("Unnamed: 16", "")).strip()

                    # Skip header rows
                    header_values = ["brand", "article", "item_desc", "Qty", "customer", "address", "contact no.", "alt. contact no.", "pincode"]
                    if any(val.strip().lower() in header_values for val in [brand, article, product_name, Qty, customer_name, address, contact_no, alt_contact_no, pincode]):
                        continue
                    
                    # Skip empty rows
                    if not any([brand, article, product_name, Qty, customer_name, address, contact_no, pincode]):
                        continue
                    
                    CustomerAddress.objects.create(
                        brand=brand,
                        article=article,
                        Qty=Qty,
                        product_name=product_name,
                        customer_name=customer_name,
                        address=address,
                        contact_no=contact_no,
                        alt_contact_no=alt_contact_no,
                        pincode=pincode
                    )

                return Response({"message": "Addresses replaced successfully."}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
         

class GenerateRoutePDFView(APIView):
    def post(self, request):
        data = request.data

        context = {
            "manifest_number": f"M6-{datetime.now().strftime('%H%M%S')}",
            "driver_name": data.get("driver_name", "N/A"),
            "route": data.get("route_name", "N/A"),
            "total_km": data.get("total_km", 0),
            "contact_number": data.get("contact_number", "N/A"),
            "invoice_count": data.get("invoice_count", 0),
            "vehicle_no": data.get("vehicle_no", "N/A"),
            "items_count": data.get("items_count", 0),
            "truck_number": data.get("truck_number", "N/A"),
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "delivery_date": data.get("delivery_date", datetime.now().strftime('%d-%m-%Y')),
            "items": data.get("stops", []),
        }

        html_string = render_to_string("route_manifest.html", context)
        pdf_file = io.BytesIO()

        HTML(string=html_string).write_pdf(target=pdf_file)

        pdf_file.seek(0)
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="manifest.pdf"'
        return response
