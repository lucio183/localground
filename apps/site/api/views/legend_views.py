from rest_framework import generics, status
from localground.apps.site.api import serializers, filters
from localground.apps.site.api.views.abstract_views import \
    AuditCreate, AuditUpdate, QueryableListCreateAPIView
from localground.apps.site import models
from localground.apps.site.api.permissions import CheckProjectPermissions
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.http import HttpResponse

class LegendList(QueryableListCreateAPIView, AuditCreate):
    error_messages = {}
    warnings = []
    serializer_class = serializers.LegendSerializer
    filter_backends = (filters.SQLFilterBackend,)
    model = models.Legend
    paginate_by = 100

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return self.model.objects.get_objects(self.request.user)
        else:
            return self.model.objects.get_objects_public(
                access_key=self.request.GET.get('access_key')
            )

    def pre_save(self, obj):
        AuditCreate.pre_save(self, obj)
        obj.access_authority = models.ObjectAuthority.objects.get(id=1)

    def create(self, request, *args, **kwargs):
        response = super(LegendList, self).create(request, *args, **kwargs)
        if len(self.warnings) > 0:
            response.data.update({'warnings': self.warnings})
        if self.error_messages:
            response.data = self.error_messages
            response.status = status.HTTP_400_BAD_REQUEST
        return response


class LegendInstance(
        generics.RetrieveUpdateDestroyAPIView,
        AuditUpdate):
    error_messages = {}
    warnings = []
    queryset = models.Legend.objects.select_related('owner').all()
    serializer_class = serializers.LegendDetailSerializer
    model = models.Legend

    def pre_save(self, obj):
        AuditUpdate.pre_save(self, obj)

    def update(self, request, *args, **kwargs):
        response = super(LegendInstance, self).update(request, *args, **kwargs)
        if len(self.warnings) > 0:
            response.data.update({'warnings': self.warnings})
        if self.error_messages:
            response.data = self.error_messages
            response.status = status.HTTP_400_BAD_REQUEST
        return response
