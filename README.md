# Workout Planner

Προσωπική εφαρμογή για καταγραφή προπονήσεων — **mobile-first PWA** (React) με Django REST API backend. Στόχος: δημιουργία **workout plans**, ημερήσια **logs** ανά session, παρακολούθηση **progress** και **σημειώσεις**. Η εφαρμογή εξελίσσεται iteratively καθώς χρησιμοποιείται· όχι fixed enterprise spec.

## Αρχιτεκτονική

| Μέρος | Τεχνολογία | Repo |
|--------|------------|------|
| **Backend (αυτό το repo)** | Django 5.2, DRF, SQLite, JWT | `workoutplanner/` |
| **Frontend (ξεχωριστό)** | React PWA (Vite), `VITE_API_URL` → backend | Δεν είναι ακόμα εδώ |

- Auth: **JWT** (`djangorestframework-simplejwt`)
- CORS dev: `http://localhost:5173`, `http://127.0.0.1:5173`
- Όλα τα API endpoints απαιτούν authentication (εκτός admin)

## Κύριες έννοιες

1. **Exercise** — κατάλογος ασκήσεων (category, type). Read-only API για χρήστες.
2. **WorkoutPlan** — πρόγραμμα προπόνησης: τίτλος, ασκήσεις με σειρά, optional targets (sets/reps/rest). `owner` + optional `is_public`.
3. **WorkoutLog** — μία προπόνηση ανά ημέρα: σύνδεση με plan (optional), JSON `data` (sets/reps/weight), `comments` για σημειώσεις.

Ο χρήστης βλέπει **δικά του plans** + **public plans** άλλων. Μπορεί να **επεξεργάζεται/διαγράφει μόνο δικά του** plans.

## Δομή project

```
workoutplanner/     # Django project (settings, urls)
workout/            # Models, serializers, views, API, validators, tests
users/              # Custom user app (προς το παρόν default User)
manage.py
requirements.txt
db.sqlite3          # local DB (gitignore αν προστεθεί)
```

## Εγκατάσταση & dev

```powershell
cd "path\to\workoutplanner"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional, για admin
python manage.py runserver 127.0.0.1:8000
```

Tests:

```powershell
python manage.py test workout
```

## API

Base: `http://127.0.0.1:8000`

| Method | Path | Περιγραφή |
|--------|------|-----------|
| POST | `/api/auth/token/` | Login → `access`, `refresh` |
| POST | `/api/auth/token/refresh/` | Ανανέωση access token |
| GET | `/api/exercises/` | Λίστα ασκήσεων (read-only) |
| GET/POST | `/api/plans/` | Λίστα / δημιουργία plan |
| GET/PATCH/DELETE | `/api/plans/{id}/` | Λεπτομέρειες / επεξεργασία (μόνο owner) |
| GET/POST | `/api/logs/` | Logs του τρέχοντος user |
| GET/PATCH/DELETE | `/api/logs/{id}/` | Λεπτομέρειες log |
| — | `/api/logs/?plan={id}` | Φίλτρο logs ανά plan |

Headers για protected routes:

```
Authorization: Bearer <access_token>
```

Pagination: page size 20 (`results`, `count`, …).

### Nested plan create (παράδειγμα)

```json
POST /api/plans/
{
  "title": "Push Day",
  "is_public": false,
  "plan_exercises": [
    {
      "exercise_id": 1,
      "order": 1,
      "target_sets": 3,
      "target_reps": 10,
      "rest_seconds": 90
    }
  ]
}
```

`owner` και `user` **δεν** στέλνονται από client — ορίζονται από server (`request.user`).

### Workout log JSON (`data`)

Σύμβαση για το React PWA (validated στο `workout/validators.py`):

```json
[
  {
    "exercise_id": 1,
    "sets": [
      { "reps": 10, "weight_kg": 60 },
      { "reps": 8, "weight_kg": 62.5 }
    ]
  }
]
```

- `exercise_id`: positive integer
- `sets`: τουλάχιστον ένα set
- `reps`: integer ≥ 0
- `weight_kg`: optional, number ≥ 0

Παράδειγμα create log:

```json
POST /api/logs/
{
  "plan": 1,
  "date": "2026-05-20",
  "data": [{ "exercise_id": 1, "sets": [{ "reps": 10, "weight_kg": 60 }] }],
  "comments": "Καλή προπόνηση, λίγη κούραση στο τέλος"
}
```

`plan` μπορεί να είναι `null` για custom session χωρίς plan.

## Permissions (σύνοψη)

- **Plans**: queryset = `owner = me OR is_public`. Mutations (PATCH/DELETE) μόνο αν `owner == request.user` (`IsPlanOwner`).
- **Logs**: μόνο δικά του user (filter στο queryset + `perform_create`).

## Κατάσταση & roadmap

### Έτοιμο (backend)

- [x] Models: Exercise, WorkoutPlan, PlanExercise, WorkoutLog
- [x] Migrations, admin
- [x] Serializers (nested `plan_exercises`)
- [x] ViewSets + router (`/api/exercises|plans|logs/`)
- [x] JWT + CORS για Vite dev
- [x] Validator για log `data`
- [x] API tests (`workout/tests.py`)

### Επόμενο (frontend — ξεχωριστό repo)

- [ ] React PWA: login, token refresh
- [ ] Οθόνες: plans, log session, ιστορικό logs, progress
- [ ] Mobile UX (offline/cache αν χρειαστεί αργότερα)

### Μελλοντικά (όταν προκύψουν από χρήση)

- Progress charts / PRs
- Offline sync
- Production deploy (Postgres, env vars, `ALLOWED_HOSTS`, secret key)

## Οδηγίες για agents / contributors

1. **Προσωπικό project** — αποφεύγουμε over-engineering· μικρές, στοχευμένες αλλαγές.
2. **Mobile-first PWA** — UI/UX για κινητό, όχι desktop admin panel.
3. **Iterative** — features προστίθενται όταν ο χρήστης τα χρειάζεται στην πράξη.
4. **Μην αλλάζουμε** το JSON contract του `data` χωρίς συντονισμό με frontend.
5. **Backend-only σε αυτό το repo** — React ζει αλλού μέχρι να προστεθεί monorepo (αν ποτέ).

## Stack

- Django ≥5.2
- djangorestframework
- djangorestframework-simplejwt
- django-cors-headers
