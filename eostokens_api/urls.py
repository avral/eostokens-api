from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, serializers, viewsets

from gateway.views import EOSAccountViewSet, EOSAccountCreationView
from history_api.views import MarketViewSet, PriceHistoryViewSet, ChatrsView


router = routers.DefaultRouter()
router.register('users', EOSAccountViewSet)
router.register('markets', MarketViewSet)
router.register('price-history', PriceHistoryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('api/register_account', EOSAccountCreationView.as_view()),
    path('api/charts', ChatrsView.as_view())

]
