from rest_framework import serializers

from .models import Exercise, PlanExercise, WorkoutLog, WorkoutPlan


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'category', 'exercise_type']


class PlanExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        source='exercise',
        write_only=True,
    )

    class Meta:
        model = PlanExercise
        fields = [
            'id',
            'exercise',
            'exercise_id',
            'order',
            'target_sets',
            'target_reps',
            'rest_seconds',
        ]


class WorkoutPlanSerializer(serializers.ModelSerializer):
    plan_exercises = PlanExerciseSerializer(many=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WorkoutPlan
        fields = ['id', 'title', 'is_public', 'owner', 'plan_exercises']

    def create(self, validated_data):
        plan_exercises_data = validated_data.pop('plan_exercises')
        plan = WorkoutPlan.objects.create(
            owner=self.context['request'].user,
            **validated_data,
        )
        for plan_exercise_data in plan_exercises_data:
            PlanExercise.objects.create(plan=plan, **plan_exercise_data)
        return plan

    def update(self, instance, validated_data):
        plan_exercises_data = validated_data.pop('plan_exercises', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if plan_exercises_data is not None:
            instance.plan_exercises.all().delete()
            for plan_exercise_data in plan_exercises_data:
                PlanExercise.objects.create(plan=instance, **plan_exercise_data)

        return instance


class WorkoutLogSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WorkoutLog
        fields = ['id', 'plan', 'date', 'data', 'comments', 'user']
