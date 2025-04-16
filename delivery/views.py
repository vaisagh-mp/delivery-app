from rest_framework.views import APIView
import pandas as pd
from rest_framework.response import Response
from rest_framework import status, generics
from .models import CustomerAddress, OptimizedRoute
from .serializers import CustomerAddressSerializer, ExcelUploadSerializer
from .utils import get_lat_lon, get_optimized_route
from geopy.distance import geodesic

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

