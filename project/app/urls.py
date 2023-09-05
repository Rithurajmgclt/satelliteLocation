from rest_framework import routers
from django.urls import path,include
from app.api.normal_views import SatelliteViewset


router = routers.DefaultRouter()
router.register('satellite', SatelliteViewset)



urlpatterns = [
  
   path('', include(router.urls)),
]



