from django import forms
from accounts.models import UserProfile, AppUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

ROLE_CHOICES = [
    ('attendee', 'I want to attend events'),
    ('organizer', 'I want to organize events'),
]


class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='I am a...')

    class Meta(UserCreationForm.Meta):
        model = AppUser
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {'email': 'Email address'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['email'].widget.attrs['placeholder'] = 'example@example.com'
        self.fields['username'].help_text = 'Letters, digits and (@/./+/-/_) only'

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if AppUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already registered')
        return email


class UserEditForm(forms.ModelForm):
    login_name = forms.CharField(label='Username', disabled=True, required=False)
    email = forms.EmailField(label="Email address", disabled=True, required=False)

    class Meta:
        model = UserProfile
        exclude = ['user', 'created_at']
        labels = {'city': 'Home town', 'avatar': 'Profile picture'}
        help_texts = {'phone_number': '+359888123456'}
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'}), 'phone_number': forms.TextInput(attrs={'placeholder': '+359...'}),}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login_name'].initial = self.instance.user.username
        self.fields['email'].initial = self.instance.user.email
        self.order_fields(['login_name', 'email'] + [field for field in self.fields if field not in ['login_name', 'email']])


class FullNameEditForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ('first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['first_name'].widget.attrs['placeholder'] = 'First name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last name'


class AppLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'
        self.error_messages['invalid_login'] = 'Wrong username or password'
