from django.contrib.auth.forms import UserCreationForm as BuiltInUserCreationForm, UsernameField
from django.forms import EmailField

from accounts.models import User


class UserCreationForm(BuiltInUserCreationForm):
    """
    A form that creates a user, with no privileges,
    from the given email, username and password.
    """
    email = EmailField(required=True, label='Email')

    class Meta(BuiltInUserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
        field_classes = {
            'username': UsernameField,
            'email': EmailField
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
