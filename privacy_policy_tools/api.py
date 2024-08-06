from rest_framework import viewsets
from rest_framework import permissions
from .models import PrivacyPolicy
from .serializers import PrivacyPolicySerializer

class PrivacyPolicyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PrivacyPolicy.objects.filter(active=True)
    serializer_class = PrivacyPolicySerializer
    permission_classes = [permissions.IsAuthenticated]