import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def assign_workout_plan_owners(apps, schema_editor):
    WorkoutPlan = apps.get_model('workout', 'WorkoutPlan')
    user_model_label = settings.AUTH_USER_MODEL
    app_label, model_name = user_model_label.split('.')
    User = apps.get_model(app_label, model_name)

    plans_without_owner = WorkoutPlan.objects.filter(owner__isnull=True)
    if not plans_without_owner.exists():
        return

    default_owner = (
        User.objects.filter(is_superuser=True).order_by('pk').first()
        or User.objects.order_by('pk').first()
    )
    if default_owner is None:
        raise RuntimeError(
            'Cannot assign WorkoutPlan.owner: existing plans found but no users exist.'
        )

    plans_without_owner.update(owner=default_owner)


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0004_rename_users_workoutlog_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='workoutplan',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='workoutplan',
            name='owner',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='workout_plans',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(
            assign_workout_plan_owners,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='workoutplan',
            name='owner',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='workout_plans',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
