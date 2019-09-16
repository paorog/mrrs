from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, mixins
from . import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.core import serializers as serializer
from mrrs.app.models import UserProfile, Role, Department, Designation, Client, ContentCreated, ServiceCreated, Service, \
    Content, Kpi, Duration, Industry
from rest_framework import status
from rest_framework import generics
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from rest_framework.decorators import detail_route,api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from xero import Xero
from xero.auth import PrivateCredentials


class UserViewSet(viewsets.ModelViewSet):
    """
    Provides basic CRUD functions for the User model
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @detail_route(methods=['put'], serializer_class=serializers.ChangePasswordSerializer)
    def change_password(self,request, pk=None):
        user = self.get_object()
        password_serialized = serializers.ChangePasswordSerializer(data=request.data)

        if password_serialized.is_valid():
            if not user.check_password(password_serialized.data.get('old_password')):
                return Response({'old_password': ['Wrong password.']}, 
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            user.set_password(password_serialized.data.get('password'))
            user.save()
            return Response({'status': 'password set'}, status=status.HTTP_200_OK)

        return Response(password_serialized.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = serializers.ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response("Success.", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ProfileViewSet(mixins.ListModelMixin,
#                      mixins.RetrieveModelMixin,
#                      mixins.UpdateModelMixin,
#                      viewsets.GenericViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """


class ProfileViewSet(viewsets.ModelViewSet):

    queryset = UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)


class HeroManagerViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):

    queryset = UserProfile.objects.all()
    serializer_class = serializers.HeroManagerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class RoleViewSet(viewsets.ModelViewSet):

    queryset = Role.objects.all()
    serializer_class = serializers.RoleSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class DepartmentViewSet(viewsets.ModelViewSet):

    queryset = Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class DesignationViewSet(viewsets.ModelViewSet):

    queryset = Designation.objects.all()
    serializer_class = serializers.DesignationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def load_designations(request):
        department = request.GET.get('department')
        designations = Designation.objects.filter(department_id=department).values('id', 'designation')
        return JsonResponse({'designations': list(designations)})

    def desi_val(request):
        desi_code = request.GET.get('desi_code')
        designation = Designation.objects.filter(desi_code=desi_code).values('designation')
        return HttpResponse(designation)


class ClientListViewSet(viewsets.ModelViewSet):

    queryset = Client.objects.all()
    serializer_class = serializers.ClientListManagerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_invoices(request):
        with open(r'C:\Program Files\OpenSSL-Win64\bin\privatekey.pem') as keyfile:
            rsa_key = keyfile.read()

        credentials = PrivateCredentials('R5P0XUAGIBH2ARAHEUEPVFOEHRSOX7', rsa_key)
        xero = Xero(credentials)
        xero_id = request.GET.get('xero_id')
        xero_data = xero.invoices.filter(Contact_ContactID=xero_id, order='DueDateString DESC', page=1)

        return JsonResponse({'xero_data': list(xero_data)})
        #return HttpResponse(xero_id)

    def get_invoice(request):
        with open(r'C:\Program Files\OpenSSL-Win64\bin\privatekey.pem') as keyfile:
            rsa_key = keyfile.read()

        credentials = PrivateCredentials('R5P0XUAGIBH2ARAHEUEPVFOEHRSOX7', rsa_key)
        xero = Xero(credentials)
        invoice_id = request.GET.get('invoice_id')
        xero_data = xero.invoices.filter(InvoiceID=invoice_id)

        return HttpResponse(xero_data)

    def list_invoices(request):
        with open(r'C:\Program Files\OpenSSL-Win64\bin\privatekey.pem') as keyfile:
            rsa_key = keyfile.read()

        credentials = PrivateCredentials('R5P0XUAGIBH2ARAHEUEPVFOEHRSOX7', rsa_key)
        xero = Xero(credentials)
        #invoice_id = request.GET.get('invoice_id')
        # xero_data = xero.invoices.filter(InvoiceID=invoice_id)
        #
        # return JsonResponse({'xero_data': list(xero_data)})

        client_ids = Client.objects.all().values_list('xero_id', flat=True)
        #xero_data = xero.invoices.filter(Contact_ContactID__in=client_ids)
        xero_data = xero.invoices.filter(Contact_ContactID='78a16a55-7dd6-46e5-926c-7e99a017b3ae')

        return JsonResponse({'data': list(xero_data)})


class ClientViewSet(viewsets.ModelViewSet):

    queryset = Client.objects.all()
    serializer_class = serializers.ClientManagerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class ContentCreatedViewSet(viewsets.ModelViewSet):

    queryset = ContentCreated.objects.all()
    serializer_class = serializers.ContentCreatedSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class ServiceCreatedViewSet(viewsets.ModelViewSet):

    queryset = ServiceCreated.objects.all()
    serializer_class = serializers.ServiceCreatedSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class ServiceViewSet(viewsets.ModelViewSet):

    queryset = Service.objects.all()
    serializer_class = serializers.ServiceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class ContentViewSet(viewsets.ModelViewSet):

    queryset = Content.objects.all()
    serializer_class = serializers.ContentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class KpiViewSet(viewsets.ModelViewSet):

    queryset = Kpi.objects.all()
    serializer_class = serializers.KpiSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class DurationViewSet(viewsets.ModelViewSet):

    queryset = Duration.objects.all()
    serializer_class = serializers.DurationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class IndustryViewSet(viewsets.ModelViewSet):

    queryset = Industry.objects.all()
    serializer_class = serializers.IndustrySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        try:
            user_id = token.user_id
            user = User.objects.get(id=user_id)
            return Response({
                             'token': token.key,
                             'user_email': user.email,
                             'user_name': user.first_name+' '+user.last_name,
                             'user_drf': user.id
                            })
        except User.DoesNotExist:
            return Response({'message': 'user does not exist'})
