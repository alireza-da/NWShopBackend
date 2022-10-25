from django.urls import include, path
from rest_framework import routers
from backend.api import views
from backend.api import urls
from django.contrib import admin
from django.conf import settings

router = routers.DefaultRouter()
router.register(r'users', views.UserView, basename="users")
router.register(r'offers', views.OfferView, basename="offers")
router.register(r'transactions', views.TransactionView, basename="transactions")
router.register(r'validation', views.GoogleView, basename="validation")
router.register(r'requests', views.RequestView, basename="validation")
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('user/', include(urls)),

]