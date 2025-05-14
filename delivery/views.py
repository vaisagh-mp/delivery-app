from rest_framework.views import APIView
import pandas as pd
from datetime import datetime
import io
from django.utils import timezone
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
                df.columns = df.columns.str.strip()

                CustomerAddress.objects.all().delete()

                for _, row in df.iterrows():
                    raw_date = row.get("Unnamed: 1", "")
                    invoice_date = None

                    # Skip if header row
                    if str(raw_date).strip().lower() in ["invoice date", ""]:
                        continue

                    # Parse invoice_date
                    if isinstance(raw_date, datetime):
                        invoice_date = raw_date
                    else:
                        try:
                            invoice_date = timezone.make_aware(datetime.strptime(str(raw_date).strip(), "%d/%m/%Y %H:%M:%S"))
                        except ValueError:
                            try:
                                invoice_date = timezone.make_aware(datetime.strptime(str(raw_date).strip(), "%d/%m/%Y"))
                            except ValueError:
                                return Response(
                                    {"error": f"Invalid date format: {raw_date}"},
                                    status=status.HTTP_400_BAD_REQUEST
                                )

                    invoice_no = str(row.get("Unnamed: 2", "")).strip()
                    ref_no = str(row.get("Unnamed: 3", "")).strip()
                    store_code = str(row.get("Unnamed: 4", "")).strip()
                    sto_no = str(row.get("Unnamed: 9", "")).strip()
                    brand = str(row.get("Unnamed: 6", "")).strip()
                    article = str(row.get("Unnamed: 7", "")).strip()
                    product_name = str(row.get("Unnamed: 8", "")).strip()
                    Qty = str(row.get("Unnamed: 10", "")).strip()
                    customer_name = str(row.get("Unnamed: 12", "")).strip()
                    address = str(row.get("Unnamed: 13", "")).strip()
                    contact_no = str(row.get("Unnamed: 14", "")).strip()
                    alt_contact_no = str(row.get("Unnamed: 15", "")).strip()
                    pincode = str(row.get("Unnamed: 16", "")).strip()

                    # Skip header rows accidentally interpreted as data
                    header_values = ["invoice_no", "ref_no", "store_code", "sto_no", "brand", "article", "item_desc", "Qty", "customer", "address", "contact no.", "alt. contact no.", "pincode"]
                    if any(val.strip().lower() in header_values for val in [invoice_no, ref_no, store_code, sto_no, brand, article, product_name, Qty, customer_name, address, contact_no, alt_contact_no, pincode]):
                        continue

                    # Skip empty rows
                    if not any([invoice_no, ref_no, store_code, sto_no, brand, article, product_name, Qty, customer_name, address, contact_no, pincode]):
                        continue

                    CustomerAddress.objects.create(
                        invoice_date=invoice_date,
                        invoice_no=invoice_no,
                        ref_no=ref_no,
                        store_code=store_code,
                        sto_no=sto_no,
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
