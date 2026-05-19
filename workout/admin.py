from django.contrib import admin
from .models import *
# Register your models here.

# 1. Ορίζεις πώς θα εμφανίζεται η "σχέση" μέσα στην άλλη σελίδα
class PlanExerciseInline(admin.TabularInline):
    model = PlanExercise
    extra = 1
    fields = ('exercise', 'order', 'target_sets', 'target_reps', 'rest_seconds')

# 2. Ορίζεις το κύριο Admin του WorkoutPlan
@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    inlines = [PlanExerciseInline] # Εδώ "κουμπώνεις" τον πίνακα από πάνω
    list_display = ('title', 'owner', 'is_public')
    list_filter = ('is_public', 'owner')

# 3. Απλό registration για τις ασκήσεις
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'exercise_type')
    list_filter = ('category', 'exercise_type')

@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    # Τι θα βλέπεις στη λίστα με όλα τα logs
    list_display = ('user', 'plan', 'date') 
    
    # Φίλτρα στα δεξιά για να βρίσκεις π.χ. μόνο τις προπονήσεις του τελευταίου μήνα
    list_filter = ('date', 'user', 'plan') 
    
    # Δυνατότητα αναζήτησης βάσει username ή τίτλου προγράμματος
    search_fields = ('user__username', 'plan__title') 
    
    # Ταξινόμηση ώστε τα πιο πρόσφατα να είναι πάνω-πάνω
    ordering = ('-date',)
