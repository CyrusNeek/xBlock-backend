from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from web.serializers import BrandImageSerializer
from web.serializers.brand_serializer import BrandInitSerializer
from web.models import Brand, BrandOwner, Unit


class BrandInitViewset(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, brand_id, *args, **kwargs):
        brand = Brand.objects.get(id=brand_id)
        serializer = BrandImageSerializer(brand, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        try:
            serializer = BrandInitSerializer(data=request.data, context={'request': request})
            user = request.user
            brand_owner = BrandOwner.objects.get(id=user.affiliation.id)
            if not brand_owner:
                return Response({"error": "Brand owner not found"}, status=404)
                
            brand_owner.workspace_type = request.data["workspace_type"]
            brand_owner.save()

            primary_brand = Brand.objects.filter(affiliation=None, owner=brand_owner).first()
            if primary_brand:
                primary_brand.name = request.data["primary_brand_name"]
                primary_brand.save()

                unit = Unit.objects.filter(brand=primary_brand).first()
                if unit:
                    unit.name = request.data["unit_name"]
                    unit.address = request.data["address"]
                    unit.website = request.data["website"]
                    unit.location = request.data["location"]
                    unit.save()

                sub_brand = Brand.objects.filter(affiliation=primary_brand).first()
                if sub_brand:
                    sub_brand.name = request.data["sub_brand_name"]
                    sub_brand.save()

                    sub_brand_unit = Unit.objects.filter(brand=sub_brand).first()
                    if sub_brand_unit:
                        sub_brand_unit.name = request.data["unit_name"]
                        sub_brand_unit.address = request.data["address"]
                        sub_brand_unit.website = request.data["website"]
                        sub_brand_unit.location = request.data["location"]
                        sub_brand_unit.save()

            return Response({"message": "Brand initialized successfully"}, status=200)
        except BrandOwner.DoesNotExist:
            return Response({"error": "Brand owner not found"}, status=404)
        except KeyError as e:
            return Response({"error": f"Missing required field: {str(e)}"}, status=400)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

        