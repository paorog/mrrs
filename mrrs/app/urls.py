from django.conf.urls import url, include
from rest_framework import routers
from . import views
from rest_framework.authtoken.views import ObtainAuthToken
from .views import CustomObtainAuthToken

router = routers.DefaultRouter()
# router.register(r'users', views.ProfileViewSet)
# router.register(r'users', views.UserViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'heroes', views.ProfileViewSet)
router.register(r'list_users', views.HeroManagerViewSet)
router.register(r'list_roles', views.RoleViewSet)
router.register(r'list_departments', views.DepartmentViewSet)
router.register(r'designations', views.DesignationViewSet)
router.register(r'clients', views.ClientViewSet)
router.register(r'list_clients', views.ClientListViewSet)
router.register(r'list_services', views.ServiceViewSet)
router.register(r'list_contents', views.ContentViewSet)
router.register(r'list_kpi', views.KpiViewSet)
router.register(r'list_duration', views.DurationViewSet)
router.register(r'list_industry', views.IndustryViewSet)
router.register(r'list_invoices', views.InvoiceViewSet)
router.register(r'list_nps', views.NpsViewSet)
router.register(r'dashboard_stream', views.DashboardLiveStreamViewSet),
router.register(r'list_dashboard_stream', views.DashboardLiveStreamListViewSet),
router.register(r'list_other_revenue', views.OtherRevenueViewSet),
router.register(r'csmclients', views.CsmClientViewSet),
router.register(r'list_csmclients', views.CsmClientListViewSet),
router.register(r'list_weekscores', views.WeekScoreViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth', CustomObtainAuthToken.as_view()),
    url(r'^list_designations/$', views.DesignationViewSet.load_designations),
    url(r'^list_xero_invoices/$', views.ClientListViewSet.get_invoices),
    url(r'^get_invoice/$', views.ClientListViewSet.get_invoice),
    url(r'^dashboard_metrics/$', views.ClientListViewSet.dashboard_metrics),
    url(r'^dashboard_data/$', views.ClientListViewSet.dashboard_metrics_data),
    url(r'^dashboard_breakdown/$', views.ClientListViewSet.dashboard_breakdown),
    url(r'^get_my_clients/$', views.ClientListViewSet.get_my_clients),
    url(r'^calendar_clients/$', views.ClientListViewSet.get_clients_by_hero),
    url(r'^get_client_by_xero/$', views.ClientListViewSet.get_client_by_xero),
    #url(r'^get_csm_client_nps/$', views.CsmClientViewSet.getClient)
    url(r'^dashboard_metrics_current/$', views.ClientListViewSet.dashboard_metrics_current),
    url(r'^dashboard_metrics_monthly/$', views.ClientListViewSet.dashboard_metrics_monthly),
    url(r'^get_csm_client_data/$', views.CsmClientListViewSet.get_csm_client_data)
]