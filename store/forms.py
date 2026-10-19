from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Nome', max_length=80)
    email = forms.EmailField(label='E-mail')
    class Meta:
        model = get_user_model()
        fields = ['first_name','email','username','password1','password2']
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit: user.save()
        return user
