from rest_framework.routers import DefaultRouter

from .views import ExerciseViewSet, WorkoutLogViewSet, WorkoutPlanViewSet

router = DefaultRouter()
router.register('exercises', ExerciseViewSet, basename='exercise')
router.register('plans', WorkoutPlanViewSet, basename='workoutplan')
router.register('logs', WorkoutLogViewSet, basename='workoutlog')

urlpatterns = router.urls
