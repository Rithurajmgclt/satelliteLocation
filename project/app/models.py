from django.db import models
from django.contrib.gis.db import models as gis_models

# Create your models here.

class TleData(models.Model):
    name = models.CharField(max_length=255)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255)



