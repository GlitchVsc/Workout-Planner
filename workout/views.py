from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Exercise, WorkoutLog, WorkoutPlan
from .permissions import IsPlanOwner
from .serializers import (
    ExerciseSerializer,
    WorkoutLogSerializer,
    WorkoutPlanSerializer,
)


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exercise.objects.all().order_by('name')
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]


class WorkoutPlanViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutPlanSerializer
    permission_classes = [IsAuthenticated, IsPlanOwner]

    def get_queryset(self):
        return (
            WorkoutPlan.objects.filter(
                Q(owner=self.request.user) | Q(is_public=True),
            )
            .prefetch_related('plan_exercises__exercise')
            .order_by('title')
        )


class WorkoutLogViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = WorkoutLog.objects.filter(user=self.request.user).select_related('plan')
        plan_id = self.request.query_params.get('plan')
        if plan_id is not None:
            qs = qs.filter(plan_id=plan_id)
        return qs.order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
