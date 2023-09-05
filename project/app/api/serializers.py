from rest_framework import serializers 
from ..models import TleData

class TleDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TleData
        fields = '__all__'
class TleDataPostSerializer(serializers.Serializer):
    FILE_CHOICES = (('30sats', '30sats'), ('30000sats', '30000sats'),)
    filename = serializers.ChoiceField(choices=FILE_CHOICES)
    
class GetCordinatesSerializer(serializers.Serializer):
    x_top_left = serializers.FloatField()
    y = serializers.FloatField()
