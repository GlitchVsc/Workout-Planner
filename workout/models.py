from django.db import models
from django.conf import settings

# Create your models here.
class Exercise(models.Model):
    name = models.CharField(max_length = 30)
    category = models.CharField(max_length= 30)
    type = models.CharField(max_length= 30)

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
    plan = models.ForeignKey(WorkoutPlan, on_delete = models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete= models.CASCADE)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

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