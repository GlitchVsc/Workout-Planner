from django.db import models
from django.conf import settings


class ExerciseCategory(models.TextChoices):
    CHEST = 'chest', 'Chest'
    BACK = 'back', 'Back'
    LEGS = 'legs', 'Legs'
    SHOULDERS = 'shoulders', 'Shoulders'
    ARMS = 'arms', 'Arms'
    CORE = 'core', 'Core'
    CARDIO = 'cardio', 'Cardio'


class ExerciseType(models.TextChoices):
    COMPOUND = 'compound', 'Compound'
    ISOLATION = 'isolation', 'Isolation'
    BODYWEIGHT = 'bodyweight', 'Bodyweight'
    CARDIO = 'cardio', 'Cardio'


class Exercise(models.Model):
    name = models.CharField(max_length=30)
    category = models.CharField(
        max_length=30,
        choices=ExerciseCategory.choices,
        default=ExerciseCategory.CHEST,
    )
    exercise_type = models.CharField(
        max_length=30,
        choices=ExerciseType.choices,
        default=ExerciseType.COMPOUND,
    )

    def __str__(self):
        return self.name
class WorkoutPlan(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workout_plans',
    )
    title = models.CharField(max_length=30)
    is_public = models.BooleanField(default=False)
    exercises = models.ManyToManyField(Exercise, through='PlanExercise')

    def __str__(self):
        return self.title

class PlanExercise(models.Model):
    plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name='plan_exercises',
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='plan_exercises',
    )
    order = models.PositiveIntegerField(default=1)
    target_sets = models.PositiveIntegerField(null=True, blank=True)
    target_reps = models.PositiveIntegerField(null=True, blank=True)
    rest_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['plan', 'exercise'],
                name='unique_plan_exercise',
            ),
        ]

    def __str__(self):
        return f'{self.plan.title} — {self.exercise.name} (#{self.order})'

class WorkoutLog(models.Model):
    # onoma tou User
    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete = models.CASCADE )
    # to plano pou tha katagrafei sto log 
    plan = models.ForeignKey(WorkoutPlan,  on_delete = models.SET_NULL , null = True)
    # to date
    date = models.DateField(auto_now_add = True)
    # ti data stelnw
    data = models.JSONField()
    # kapoio sxolio
    comments = models.TextField (null= True , blank = True)

    def __str__(self):
        
        return f"{self.user.username} - {self.plan.title if self.plan else 'Custom'} - {self.date.strftime('%d/%m/%Y')}"