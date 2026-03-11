from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import LeadCreateSerializer, LeadSerializer
from .models import Lead

@api_view(['POST'])
def test_create_lead(request):
    """Test view for creating leads without authentication."""
    serializer = LeadCreateSerializer(data=request.data)
    if serializer.is_valid():
        lead = serializer.save()
        return Response({
            'success': True,
            'data': LeadSerializer(lead).data,
            'message': 'Lead created successfully'
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
