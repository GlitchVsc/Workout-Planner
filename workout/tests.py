from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Exercise, WorkoutLog, WorkoutPlan

User = get_user_model()


class WorkoutAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='alice', password='testpass123')
        cls.other = User.objects.create_user(username='bob', password='testpass123')
        cls.exercise = Exercise.objects.create(name='Bench Press')

    def _token(self, username='alice', password='testpass123'):
        response = self.client.post(
            '/api/auth/token/',
            {'username': username, 'password': password},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access']

    def test_unauthenticated_plans_returns_401(self):
        response = self.client.get('/api/plans/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_obtain_and_list_plans(self):
        own_plan = WorkoutPlan.objects.create(owner=self.user, title='My Plan')
        public_plan = WorkoutPlan.objects.create(
            owner=self.other,
            title='Public Plan',
            is_public=True,
        )
        WorkoutPlan.objects.create(owner=self.other, title='Private Plan')

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self._token()}')
        response = self.client.get('/api/plans/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item['id'] for item in response.data['results']}
        self.assertEqual(ids, {own_plan.id, public_plan.id})

    def test_cannot_update_other_users_public_plan(self):
        public_plan = WorkoutPlan.objects.create(
            owner=self.other,
            title='Public Plan',
            is_public=True,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self._token()}')
        response = self.client.patch(
            f'/api/plans/{public_plan.id}/',
            {'title': 'Hijacked'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        public_plan.refresh_from_db()
        self.assertEqual(public_plan.title, 'Public Plan')

    def test_create_plan_sets_owner_from_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self._token()}')
        response = self.client.post(
            '/api/plans/',
            {
                'title': 'Push Day',
                'is_public': False,
                'plan_exercises': [
                    {
                        'exercise_id': self.exercise.id,
                        'order': 1,
                        'target_sets': 3,
                        'target_reps': 10,
                        'rest_seconds': 90,
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        plan = WorkoutPlan.objects.get(pk=response.data['id'])
        self.assertEqual(plan.owner, self.user)
        self.assertEqual(plan.plan_exercises.count(), 1)

    def test_workout_log_scoped_to_user_and_validates_data(self):
        plan = WorkoutPlan.objects.create(owner=self.user, title='My Plan')
        valid_data = [
            {'exercise_id': self.exercise.id, 'sets': [{'reps': 10, 'weight_kg': 60}]},
        ]

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self._token()}')
        create_response = self.client.post(
            '/api/logs/',
            {'plan': plan.id, 'data': valid_data, 'comments': 'Good session'},
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkoutLog.objects.filter(user=self.user).count(), 1)

        invalid_response = self.client.post(
            '/api/logs/',
            {'data': [{'exercise_id': self.exercise.id, 'sets': []}]},
            format='json',
        )
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self._token()}')
        bob_token = self._token(username='bob', password='testpass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {bob_token}')
        list_response = self.client.get('/api/logs/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 0)
