import threading
import os
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from rest_framework import viewsets,filters,status
from rest_framework .decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv
from datetime import datetime, timedelta


from .. models import TleData
from .serializers import TleDataSerializer,TleDataPostSerializer
from ..utils import ecef2lla # given function 





class SatelliteViewset(viewsets.ModelViewSet):
    """
    Satellite details
    """
    queryset=TleData.objects.all()
    serializer_class=TleDataSerializer
    filterset_fields = [
        'name'
    ]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    http_method_names=['get','post']
    @action(detail=False, methods=['post'],serializer_class=TleDataPostSerializer)
    def satinfo_from_txt_file(self,request):
        """
        To save the satellite data to database from given files,Two option 1 a file 30 sat, 2 file of 3000 sat
        used threading and bulkupload to reduce the time complexity
    
        """
        try:
            file = request.data['filename']
            allowed_filenames = ['30sats', '30000sats']
            if file is None  or file not in allowed_filenames:
                return Response({'message': 'provide the file name'},status=status.HTTP_404_NOT_FOUND)
            base_dir = settings.BASE_DIR
            file_path = os.path.join(base_dir,)
            filename = f'{file_path}/app/sat_details/{file}.txt'
            def parse_tle_file(filename):
                tle_data = []
                with open(filename, 'r') as file:
                    lines = file.read().splitlines()
                    for i in range(0, len(lines), 3):
                        name = lines[i]
                        line1 = lines[i + 1]
                        line2 = lines[i + 2]
                        tle = TleData(name=name, line1=line1, line2=line2)
                        tle_data.append(tle)    
                return tle_data
            def bulk_create(filename):
                tle_data = parse_tle_file(filename)# Parse the TLE data from the file
                TleData.objects.bulk_create(tle_data) 
            # bulk create of TLE data using threading so it will work in backgroud
            background_thread = threading.Thread(target=bulk_create)
            background_thread.start()
            return Response({'message': 'Satellite infomation saved succusfuly'},status=status.HTTP_200_OK)
        except Exception as e:
        # Handle any unexpected errors here
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
            name='top_left',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_ARRAY,
            items={'type': openapi.TYPE_NUMBER, 'format': openapi.FORMAT_FLOAT},
            maxItems=2,
            minItems=2, # Limit to two values
            required=True,
            description="Coordinates in the format (latitude, longitude)",
            ),
            openapi.Parameter(
            name='top_right',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_ARRAY,
            items={'type': openapi.TYPE_NUMBER, 'format': openapi.FORMAT_FLOAT},
            maxItems=2,
            minItems=2,  # Limit to two values
            required=True,
            description="Coordinates in the format (latitude, longitude)",
            ),
            openapi.Parameter(
            name='bottom_left',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_ARRAY,
            items={'type': openapi.TYPE_NUMBER, 'format': openapi.FORMAT_FLOAT},
            maxItems=2,
            minItems=2,  # Limit to two values
            required=True,
            description="Coordinates in the format (latitude, longitude)",
            ),
            openapi.Parameter(
            name='bottom_right',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_ARRAY,
            items={'type': openapi.TYPE_NUMBER, 'format': openapi.FORMAT_FLOAT},
            maxItems=2,
            minItems=2,  # Limit to two values
            required=True,
            description="Coordinates in the format (latitude, longitude)",
            ),
            
           
        ],
    )    
    @action(detail=True, methods=['get'],serializer_class=None,)
    def time_from_position_of_satelite(self,request,pk):
        """
        Take a satellite id , and give four coordinates as a input, 
        use TleData list api to get the input 
        Returns: the time when it reaches inside the given cordinates
    
        """
        top_left = tuple(request.query_params.get('top_left'))# four rectangular lat,long input 
        top_right = tuple(request.query_params.get('top_right'))
        bottom_left = tuple(request.query_params.get('bottom_left'))
        bottom_right = tuple(request.query_params.get('bottom_right'))
        obj = get_object_or_404(TleData, pk=pk) # taking details of selected satelite
    
        def calculate_position_velocity_over_day(tle_line1, tle_line2, duration_in_days=1):
            satellite = twoline2rv(tle_line1, tle_line2, wgs84)
            current_time = datetime.utcnow()  # Start from the current time
            end_time = current_time + timedelta(days=duration_in_days)
            results = []
            while current_time <= end_time:
                position_eci, velocity_eci = satellite.propagate(
                    current_time.year, current_time.month, current_time.day,
                    current_time.hour, current_time.minute, current_time.second)
                results.append((current_time, position_eci, velocity_eci))
                current_time += timedelta(minutes=1)
            return results
        
        sat_line1 = obj.line1
        sat_line2 = obj.line2
        results = calculate_position_velocity_over_day(sat_line1, sat_line2, duration_in_days=1)
        for  timestamp, position_eci, velocity_eci in results:
            x, y, z = position_eci
            out = ecef2lla( x, y, z) # function to generate the lat,long,alt with tle data of input satelite
            pos_long, pos_lat,pos_alt = out
            # checking the rectangular four input with input satelite lat, long
            if ((pos_lat >= float(bottom_left[0]) and pos_lat <= float(top_left[0])) and (pos_lat >= float(bottom_right[0]) and pos_lat <= float(top_right[0])) and (pos_long >= float(top_left[1]) and pos_long <= float(top_right[1])) and (pos_long >= float(bottom_left[1]) and pos_long <= float(bottom_right[1]))):
                return Response({"time of satellite on this position":timestamp},status=status.HTTP_200_OK)
            return Response({'message': 'satellite details does not exists in our library'},status=status.HTTP_404_NOT_FOUND)

            
        
           
          
 
            
    
    
        
      

    
  

