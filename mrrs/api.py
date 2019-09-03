from rest_framework import routers
from app import views

router = routers.DefaultRouter()
router.register(r'users', view.UserViewSet)
router.register(r'profile', view.UserProfileViewSet)