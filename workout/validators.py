from django.core.exceptions import ValidationError


def validate_workout_log_data(value):
    """Validate WorkoutLog.data against the React PWA JSON contract.

    Expected shape::

        [
            {"exercise_id": 1, "sets": [{"reps": 10, "weight_kg": 60}]}
        ]
    """
    if not isinstance(value, list):
        raise ValidationError('Workout log data must be a list of exercise entries.')

    for index, entry in enumerate(value):
        prefix = f'Entry {index}:'

        if not isinstance(entry, dict):
            raise ValidationError(f'{prefix} each entry must be an object.')

        if 'exercise_id' not in entry:
            raise ValidationError(f'{prefix} missing "exercise_id".')

        exercise_id = entry['exercise_id']
        if not isinstance(exercise_id, int) or isinstance(exercise_id, bool):
            raise ValidationError(f'{prefix} "exercise_id" must be an integer.')

        if exercise_id < 1:
            raise ValidationError(f'{prefix} "exercise_id" must be a positive integer.')

        if 'sets' not in entry:
            raise ValidationError(f'{prefix} missing "sets".')

        sets = entry['sets']
        if not isinstance(sets, list):
            raise ValidationError(f'{prefix} "sets" must be a list.')

        if not sets:
            raise ValidationError(f'{prefix} "sets" must contain at least one set.')

        for set_index, workout_set in enumerate(sets):
            set_prefix = f'{prefix} set {set_index}:'

            if not isinstance(workout_set, dict):
                raise ValidationError(f'{set_prefix} each set must be an object.')

            if 'reps' not in workout_set:
                raise ValidationError(f'{set_prefix} missing "reps".')

            reps = workout_set['reps']
            if not isinstance(reps, int) or isinstance(reps, bool):
                raise ValidationError(f'{set_prefix} "reps" must be an integer.')

            if reps < 0:
                raise ValidationError(f'{set_prefix} "reps" must be zero or greater.')

            if 'weight_kg' in workout_set:
                weight_kg = workout_set['weight_kg']
                if not isinstance(weight_kg, (int, float)) or isinstance(weight_kg, bool):
                    raise ValidationError(f'{set_prefix} "weight_kg" must be a number.')

                if weight_kg < 0:
                    raise ValidationError(f'{set_prefix} "weight_kg" must be zero or greater.')
