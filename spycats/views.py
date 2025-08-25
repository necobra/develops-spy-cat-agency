from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Breed, SpyCat, Mission, Target, CompleteChoices
from .serializers import BreedSerializer, SpyCatSerializer, MissionSerializer, TargetSerializer
from django.db import transaction


class SpyCatViewSet(viewsets.ModelViewSet):
    queryset = SpyCat.objects.all()
    serializer_class = SpyCatSerializer

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        instance = self.get_object()
        if 'salary' not in request.data:
            return Response({'detail': 'Only salary can be updated.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data={'salary': request.data['salary']}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            targets_data = request.data.pop('targets', [])
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            mission = serializer.save()
            if not (1 <= len(targets_data) <= 3):
                return Response({'detail': 'A mission must have 1-3 targets.'}, status=status.HTTP_400_BAD_REQUEST)
            for target in targets_data:
                Target.objects.create(mission=mission, **target)
            out = self.get_serializer(mission)
            return Response(out.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        mission = self.get_object()
        if mission.spy_cat:
            return Response({'detail': 'Cannot delete a mission assigned to a cat.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['patch'])
    def assign_cat(self, request, pk=None):
        mission = self.get_object()
        cat_id = request.data.get('spy_cat')
        if not cat_id:
            return Response({'detail': 'spy_cat id required.'}, status=status.HTTP_400_BAD_REQUEST)
        mission.spy_cat_id = cat_id
        mission.save()
        return Response(self.get_serializer(mission).data)

class TargetViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        mission = instance.mission
        if mission.complete_state == CompleteChoices.COMPLETED:
            if 'notes' in request.data:
                return Response({'detail': 'Notes cannot be updated for a completed mission.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

class BreedViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
