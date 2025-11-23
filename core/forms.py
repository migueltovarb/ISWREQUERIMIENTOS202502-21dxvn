from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Course, Enrollment

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    ROLE_CHOICES = [
        ('student', 'Estudiante'),
        ('professor', 'Profesor'),
    ]
    
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    programa = forms.CharField(max_length=100, required=False)
    semestre = forms.IntegerField(required=False, min_value=1, max_value=10)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
    
        if commit:
         user.save()
            # Asegurarnos de que el profile se creó
        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = self.cleaned_data['role']
        profile.programa = self.cleaned_data['programa']
        if self.cleaned_data['role'] == 'student':
            profile.semestre = self.cleaned_data['semestre']
        else:
                profile.semestre = None  # Limpiar semestre si no es estudiante
        profile.save()
    
        return user

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'credits', 'professor', 'schedule', 'capacity', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course']