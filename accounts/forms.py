from django.contrib.auth.forms import UserCreationForm as BuiltInUserCreationForm, UsernameField
from django.core.exceptions import ValidationError
from django.forms import EmailField

from accounts.models import User


class JayparkUsernameField(UsernameField):
    """Customized UsernameField to prevent to be input special characters."""
    def validate(self, value):
        super().validate(value)
        if len(value) <= 5:
            raise ValidationError('Username should be longer than 5 letters.')
        elif not value.isalnum():
            raise ValidationError('The type of username should consist of alphabets and numbers.')


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
            'username': JayparkUsernameField,
            'email': EmailField
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
