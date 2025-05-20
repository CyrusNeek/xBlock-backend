from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from report.models import ToastAuth, TockAuth, ResyAuth
from report.serializers import ToastAuthSerializer, TockAuthSerializer, ResyAuthSerializer
from roles.constants import UNLIMITED_BLOCK_ACCESS, LIMITED_BLOCK_ACCESS
from roles.permissions import UserPermission
from web.models import URLBlock, FileBlock, UserBrand
from web.models.quickbooks import QuickBooksCredentials
from web.models.unit import Unit
from web.serializers import URLBlockSerializer, FileBlockSerializer, QuickBooksCredentialsSerializer
from collections import defaultdict


class BlockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Initialize a dictionary to hold all block data grouped by type
        blocks_data = defaultdict(list)

        user_brands = UserBrand.objects.filter(user=user).values_list('brand', flat=True)
        all_units = Unit.objects.filter(brand__in=user_brands).values_list("pk", flat=True).distinct()
        
        # Determine which types of credentials the user has access to
        credential_types = [
            ('quickbooks', QuickBooksCredentials, QuickBooksCredentialsSerializer),
            ('toast', ToastAuth, ToastAuthSerializer),
            ('tock', TockAuth, TockAuthSerializer),
            ('resy', ResyAuth, ResyAuthSerializer)
        ]

        for cred_type, Model, Serializer in credential_types:

            if UserPermission.check_user_permission(user, UNLIMITED_BLOCK_ACCESS):
                credentials = Model.objects.filter(unit__in=all_units)
            elif UserPermission.check_user_permission(user, LIMITED_BLOCK_ACCESS):
                credentials = Model.objects.filter(unit__in=user.all_units)
            else:
                credentials = []

            for credential in credentials:
                credential_data = Serializer(credential).data
                credential_data["type"] = cred_type
                credential_data["name"] = cred_type.capitalize()
                blocks_data[cred_type].append(credential_data)

        # Retrieve URL blocks and append to blocks_data
        url_blocks = URLBlock.objects.filter(unit__in=all_units)
        for block in URLBlockSerializer(url_blocks, many=True).data:
            block['type'] = 'url'
            blocks_data['url'].append(block)

        # Retrieve File blocks and append to blocks_data
        file_blocks = FileBlock.objects.filter(unit__in=all_units)
        for block in FileBlockSerializer(file_blocks, many=True).data:
            block['type'] = 'file'
            blocks_data['file'].append(block)

        # Flatten blocks_data to a list for response
        response_data = [block for blocks in blocks_data.values() for block in blocks]

        return Response(response_data, status=status.HTTP_200_OK)
