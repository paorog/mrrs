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
from mrrs.app.models import UserProfile, Role, Department, Designation, Client, ContentCreated, ServiceCreated, Service,\
    Content, Kpi, Duration, Industry, OtherRevenue, OtherRevenueCreated, Invoice, Nps, NpsCreated, WeekScore, WeekScoreCreated, CsmClient, \
    DashboardLiveStream
from rest_framework import status
from rest_framework import generics
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from rest_framework.decorators import detail_route,api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from xero import Xero
from xero.auth import PrivateCredentials
from django.db.models import Q
from django.db.models import Sum
import datetime

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

    def dashboard_metrics(request):
        today = datetime.date.today()
        date = request.GET.get('date')
        month_firstday = date[0:7]+'-01 00:31:04.09677+08'
        services = Client.objects.filter(Q(start_date=date) | Q(start_date__day=date[8:10])).values_list('services',
                                                                                                         flat=True)

        other_revenues = Client.objects.filter(Q(start_date=date) | Q(start_date__day=date[8:10])).values_list('other_revenue',
                                                                                                         flat=True)
        other_revenues_this_day = OtherRevenueCreated.objects.filter(id__in=other_revenues).aggregate(Sum('other_revenue_value'))['other_revenue_value__sum']

        ltvs = Client.objects.filter(Q(start_date=date) | Q(start_date__day=date[8:10])).values('id', 'start_date', 'services')

        # mrr_upgrades -> need to pull added services in csm clients to determine mrr upgrades.

        if not services:
            mrr_current_day = 0
            revenue_churn_current = 0
        else:
            mrr_current_day = ServiceCreated.objects.filter(id__in=services).aggregate(Sum('service_fee'))['service_fee__sum']
            mrr_current_day = ServiceCreated.objects.filter(id__in=services).aggregate(Sum('service_fee'))[
                'service_fee__sum']
            mrr_upgrades = ServiceCreated.objects.filter(id__in=services).aggregate(Sum('service_fee_upgrade'))['service_fee_upgrade__sum']
            revenue_churn_current = (mrr_current_day - mrr_upgrades) / mrr_current_day

        dateyear = date[0:4]
        datemonth = date[5:7]
        dateday = date[8:11]
        active_clients_this_month = Client.objects.filter(created_at__gte=month_firstday).count()

        churns_this_day = CsmClient.objects.filter(updated_at__year=dateyear, updated_at__month=datemonth,
                                                updated_at__day=dateday).filter(in_churn=True).count()
        churn_rate_current = churns_this_day / active_clients_this_month

        #other_revenue = same calculation with mrr using other_revenuve values from clients
        #

        # client = Client.objects.get(id=2)
        # services = client.services.all()
        # for service in services:
        #     mrr_current_day = +ServiceCreated.objects.filter.aggregate(Sum('service_fee'))['service_fee__sum']

        metrics = {
            'mrr_current': mrr_current_day,
            'ltv_current': 0,
            'other_revenue': other_revenues_this_day,
            'churn_current': {'churns': churns_this_day, 'churn_rate' :churn_rate_current},
            'churn_revenue_current': revenue_churn_current,
            'reactive_clients_current': 0,
            'reactive_clients_revenue_current': 0,
            'upsells_current': 0,
            'downsells_current': 0
        }
        return JsonResponse({'metrics': metrics})
        return HttpResponse(mrr_current_day)
        #return JsonResponse({'services': client.services.all().values('service_fee')})
        #client = Client.objects.all().values('client_name', 'services')
        return JsonResponse({'clients': list(client)})

    def dashboard_metrics_data(request):
        date = request.GET.get('date')
        today = datetime.date.today()
        month_firstday = date[0:7] + '-01 00:31:04.09677+08'

        active_clients_this_month = CsmClient.objects.filter(created_at__gte=month_firstday).filter(in_churn=False).count()

        churns_this_month = CsmClient.objects.filter(created_at__month=today.month).filter(in_churn=True).count()
        churn_rate = churns_this_month / active_clients_this_month

        active_client_ids = CsmClient.objects.filter(in_churn=False).values('client_id')
        current_mrr = ServiceCreated.objects.filter(id__in=active_client_ids).aggregate(Sum('service_fee'))[
            'service_fee__sum']
        #mrr_upgrades -> need to pull added services in csm clients to determine mrr upgrades.
        mrr_upgrades = 0
        revenue_churn = (current_mrr - mrr_upgrades) / current_mrr

        #reactive_clients -> number of reactivated clients in the month
        #reactive_clients_revenue -> sum of services fee of clients re-activated
        #upsells -> sum of upsells
        #downsells -> sum of downsells

        dashboard_metrics_data = {
            'churn_rate': churn_rate,
            'revenue_churn_rate': revenue_churn
        }

        return JsonResponse({'data': dashboard_metrics_data})

    def dashboard_breakdown(request):
        today = datetime.date.today()

        new_clients = Client.objects.filter(created_at__month=today.month).count()
        client_churns = CsmClient.objects.filter(updated_at__year=today.year, updated_at__month=today.month,
                                                updated_at__day=today.day).filter(in_churn=True).count()
        client_churns_id = CsmClient.objects.filter(updated_at__year=today.year, updated_at__month=today.month,
                                                updated_at__day=today.day).filter(in_churn=True).values('client_id')
        client_churns_sum_value = ServiceCreated.objects.filter(id__in=client_churns_id).aggregate(Sum('service_fee'))['service_fee__sum']

        total_changes = client_churns_sum_value

        breakdowns = {
            'new_clients_count': new_clients,
            'clients_churn_count': client_churns,
            'clients_churn_value': client_churns_sum_value,
            'total_changes': total_changes
        }

        return JsonResponse({'breakdowns': breakdowns})

    def dashboard_metrics_current(request):
        today = datetime.date.today()

        active_clients = CsmClient.objects.filter(in_churn=False).values('client_id')
        clients_running = Client.objects.filter(start_date__gte=today).values('id')
        active_clients_this_month = CsmClient.objects.filter(created_at__year=today.year, created_at__month=today.month,
                                                             created_at__day=today.day).filter(in_churn=False).count()
        mrr_services = Client.objects.filter(id__in=clients_running).filter(Q(start_date__gte=today) | Q(Q(
            start_date__gte=today, start_date__day=today.day))).values_list('services', flat=True)
        ltv_services = Client.objects.filter(Q(start_date__year=today.year, start_date__month=today.month) | Q(
            Q(start_date__year=today.year, start_date__month__lte=today.month))).values_list('services', flat=True)
        churns_this_month = CsmClient.objects.filter(created_at__month=today.month).filter(in_churn=True).count()
        mrr_upgrades = ServiceCreated.objects.filter(id__in=mrr_services).aggregate(Sum('service_fee_upgrade'))[
            'service_fee_upgrade__sum']
        mrr_downgrades = ServiceCreated.objects.filter(id__in=mrr_services).aggregate(Sum('service_fee_downgrade'))[
            'service_fee_downgrade__sum']
        new_mrr = ServiceCreated.objects.filter(id__in=mrr_services, service_fee_upgrade__gt=0).aggregate(Sum('service_fee_upgrade'))[
            'service_fee_upgrade__sum']
        contraction_mrr = ServiceCreated.objects.filter(id__in=mrr_services, service_fee_downgrade__gt=0).aggregate(Sum('service_fee_downgrade'))[
            'service_fee_downgrade__sum']
        other_revenues = Client.objects.filter(Q(start_date=today) | Q(start_date__day=today.day)).values_list(
            'other_revenue', flat=True)
        mrr_current = ServiceCreated.objects.filter(service_id__in=(1, 2, 3, 4)).filter(id__in=mrr_services).aggregate(
            Sum('service_fee'))['service_fee__sum']
        ltv_current = ServiceCreated.objects.filter(service_id__in=(1, 2, 3, 4)).filter(id__in=ltv_services).aggregate(
            Sum('service_fee'))['service_fee__sum']
        churn_current = active_clients_this_month and churns_this_month / active_clients_this_month or 0
        revenue_churn_current = mrr_current and ((mrr_current - mrr_upgrades) / mrr_current) or 0
        other_revenue_current = OtherRevenueCreated.objects.filter(id__in=other_revenues).aggregate(Sum('other_revenue_value'))[
            'other_revenue_value__sum']
        web_current = ServiceCreated.objects.filter(service_id__in=(5, 6, 7)).filter(id__in=ltv_services).aggregate(
            Sum('service_fee'))['service_fee__sum']

        has_mrr_current = mrr_current and mrr_current or 0
        has_ltv_current = ltv_current and ltv_current or 0
        has_churn_current = churn_current
        has_revenue_churn_current = revenue_churn_current
        has_other_revenue_current = other_revenue_current and other_revenue_current or 0
        has_mrr_upgrades_current = mrr_upgrades and mrr_upgrades or 0
        has_mrr_downgrades_current = mrr_downgrades and mrr_downgrades or 0
        has_new_mrr_current = new_mrr and new_mrr or 0
        has_contraction_mrr_current = contraction_mrr and contraction_mrr or 0
        has_quick_ratio = (has_contraction_mrr_current + has_revenue_churn_current) and (has_new_mrr_current + has_mrr_upgrades_current) / (has_contraction_mrr_current + has_revenue_churn_current) or 0
        has_web_current = web_current and web_current or 0

        metrics_current = {
            'mrr_current': has_mrr_current,
            'ltv_current': has_ltv_current,
            'churn_current': has_churn_current,
            'revenue_churn_current': has_revenue_churn_current,
            'other_revenue_current': has_other_revenue_current,
            'mrr_downgrades_current': has_mrr_downgrades_current,
            'mrr_upgrades_current': has_mrr_upgrades_current,
            'quick_ratio_current': has_quick_ratio,
            'web_current': has_web_current
        }

        return JsonResponse({'metrics_current': metrics_current})

    def dashboard_metrics_monthly(request):
        date = request.GET.get('date')
        dateyear = date[0:4]
        datemonth = date[5:7]

        today = datetime.date.today()

        ltv_services = Client.objects.filter(Q(start_date__year=dateyear, start_date__month=datemonth) | Q(
            Q(start_date__year=dateyear, start_date__month__lte=datemonth))).values_list('services', flat=True)


        ltv_month = ServiceCreated.objects.filter(service_id__in=(1, 2, 3, 4)).filter(id__in=ltv_services).aggregate(Sum('service_fee'))[
                'service_fee__sum']

        web_month = ServiceCreated.objects.filter(service_id__in=(5, 6, 7)).filter(id__in=ltv_services).aggregate(Sum('service_fee'))[
                'service_fee__sum']

        has_ltv_month = ltv_month and ltv_month or 0
        has_web_month = web_month and web_month or 0

        metrics_monthly = {
            'ltv_month': has_ltv_month,
            'web_month': has_web_month
        }

        return JsonResponse({'metrics_monthly': metrics_monthly})

    def get_my_clients(request):
        userid = request.GET.get('createdby')
        clients = Client.objects.filter(created=userid).values('id', 'client_name', 'management_fee', 'end_date').order_by('id')
        return JsonResponse({'clients': list(clients)})

    def get_clients_by_hero(request):
        heroid = request.GET.get('hero_id')
        dept = request.GET.get('dept')

        if dept == 4:
            clients = Client.objects.filter(created=heroid).values('id', 'client_name', 'start_date', 'end_date')
        else:
            clients = Client.objects.filter(pm=heroid).values('id', 'client_name', 'start_date', 'end_date')

        return JsonResponse({'clients': list(clients)})

    def get_client_by_xero(request):
        xeroid = request.GET.get('xero_id')
        client = Client.objects.filter(xero_id=xeroid).values("id","xero_id", "created","client_name",
                                                              "management_fee", "other_revenue", "media_fees",
                                                              "contract", "industry", "company_size", "pm", "writer",
                                                              "start_date", "end_date", "duration")

        return JsonResponse({'client': list(client)})


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


class OtherRevenueViewSet(viewsets.ModelViewSet):

    queryset = OtherRevenue.objects.all()
    serializer_class = serializers.OtherRevenueSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # def post(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     serializer = self.get_serializer(data=request.data)
    #     exists = Invoice.objects.get_or_create(client_id=self.client_id)
    #
    #     if exists:
    #         Invoice.objects.filter(client._id=self.client_id).update(status=self.status)


class NpsViewSet(viewsets.ModelViewSet):

    queryset = Nps.objects.all()
    serializer_class = serializers.NpsSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class NpsCreatedViewSet(viewsets.ModelViewSet):

    queryset = NpsCreated.objects.all()
    serializer_class = serializers.NpsCreatedSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class WeekScoreViewSet(viewsets.ModelViewSet):

    queryset = WeekScore.objects.all()
    serializer_class = serializers.WeekScoreSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class WeekScoreCreatedViewSet(viewsets.ModelViewSet):

    queryset = WeekScoreCreated.objects.all()
    serializer_class = serializers.WeekScoreCreatedSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class CsmClientListViewSet(viewsets.ModelViewSet):

    queryset = CsmClient.objects.all()
    serializer_class = serializers.CsmClientListManagerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_csm_client_data(request):
        client = request.GET.get('client_id')
        check_exist = CsmClient.objects.filter(client_id=client).values('id')
        csmclient = check_exist and CsmClient.objects.get(client=client) or []
        csmclient_weeks = csmclient and csmclient.week.all().values('id', 'week', 'score', 'met') or []
        csmclient_nps = csmclient and csmclient.nps.all().values('id', 'nps', 'quantity', 'service') or []
        #return HttpResponse(csmclient_weeks.week.all())
        return JsonResponse({'csmclient_weeks': list(csmclient_weeks), 'csmclient_nps': list(csmclient_nps)})


class CsmClientViewSet(viewsets.ModelViewSet):

    queryset = CsmClient.objects.all()
    serializer_class = serializers.CsmClientManagerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # def getClient(request):
    #     client_id = request.GET.get('client_id')
    #     csmclient_id = CsmClient.objects.filter(client_id=client_id).values_list('nps', flat=True)
    #     csmclient_nps = NpsCreated.objects.filter(id=csmclient_id).values('id')
    #     return HttpResponse(csmclient_nps)


class DashboardLiveStreamViewSet(viewsets.ModelViewSet):

    queryset = DashboardLiveStream.objects.all()
    serializer_class = serializers.DashboardLiveStreamSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)


class DashboardLiveStreamListViewSet(viewsets.ModelViewSet):

    queryset = DashboardLiveStream.objects.all()
    serializer_class = serializers.DashboardLiveStreamListSerializer
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
