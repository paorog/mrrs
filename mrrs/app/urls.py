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

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth', CustomObtainAuthToken.as_view()),
    url(r'^list_designations/$', views.DesignationViewSet.load_designations),
    url(r'^list_invoices/$', views.ClientListViewSet.get_invoices),
    url(r'^get_invoice/$', views.ClientListViewSet.get_invoice)
]