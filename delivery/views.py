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

                for _, row in df.iterrows():
                    customer_name = str(row.get("Unnamed: 12", "")).strip()
                    address = str(row.get("Unnamed: 13", "")).strip()
                    contact_no = str(row.get("Unnamed: 14", "")).strip()
                    alt_contact_no = str(row.get("Unnamed: 15", "")).strip()
                    pincode = str(row.get("Unnamed: 16", "")).strip()

                    # Skip row if it's a placeholder or header
                    if (
                        customer_name.lower() == "customer" and
                        address.lower() == "address" and
                        contact_no.lower() == "contact no." and
                        alt_contact_no.lower() == "alt. contact no." and
                        pincode.lower() == "pincode"
                    ):
                        continue

                    # You can also skip empty rows if needed
                    if not any([customer_name, address, contact_no, pincode]):
                        continue

                    CustomerAddress.objects.create(
                        customer_name=customer_name,
                        address=address,
                        contact_no=contact_no,
                        alt_contact_no=alt_contact_no,
                        pincode=pincode
                    )

                return Response({"message": "Addresses uploaded successfully."}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class GenerateRoutePDFView(APIView):
#     def post(self, request):
#         data = request.data

#         context = {
#             "manifest_number": f"M6-{datetime.now().strftime('%H%M%S')}",
#             "priority": data.get("priority", 0),
#             "route": data.get("route_name", "N/A"),
#             "total_ride": data.get("total_km", 0),
#             "invoice_count": data.get("invoice_count", 0),
#             "items_count": data.get("items_count", 0),
#             "status": data.get("status", "Scheduled"),
#             "stage": data.get("stage", "Order"),
#             "driver_name": data.get("driver_name", "N/A"),
#             "contact_number": data.get("contact_number", "N/A"),
#             "vehicle_no": data.get("vehicle_no", "N/A"),
#             "vehicle_type": data.get("vehicle_type", "N/A"),
#             "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "delivery_date": data.get("delivery_date", datetime.now().strftime('%d-%m-%Y')),
#             "items": data.get("stops", []),
#         }

#         html = render_to_string("route_manifest.html", context)
#         result = io.BytesIO()
#         pisa_status = pisa.CreatePDF(html, dest=result)

#         if pisa_status.err:
#             return Response({"error": "Error generating PDF"}, status=500)

#         result.seek(0)
#         response = HttpResponse(result, content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="manifest.pdf"'
#         return response
         

class GenerateRoutePDFView(APIView):
    def post(self, request):
        data = request.data

        context = {
            "manifest_number": f"M6-{datetime.now().strftime('%H%M%S')}",
            "priority": data.get("priority", 0),
            "route": data.get("route_name", "N/A"),
            "total_ride": data.get("total_km", 0),
            "invoice_count": data.get("invoice_count", 0),
            "items_count": data.get("items_count", 0),
            "status": data.get("status", "Scheduled"),
            "stage": data.get("stage", "Order"),
            "driver_name": data.get("driver_name", "N/A"),
            "contact_number": data.get("contact_number", "N/A"),
            "vehicle_no": data.get("vehicle_no", "N/A"),
            "vehicle_type": data.get("vehicle_type", "N/A"),
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
