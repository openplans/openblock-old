#   Copyright 2007,2008,2009,2011 Everyblock LLC, OpenPlans, and contributors
#
#   This file is part of ebpub
#
#   ebpub is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ebpub is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with ebpub.  If not, see <http://www.gnu.org/licenses/>.
#

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from ebpub.accounts.models import User

class UniqueEmailField(forms.EmailField):
    """
    Validates that the given value is an e-mail address and hasn't already
    been registered.
    """
    def clean(self, value):
        value = forms.EmailField.clean(self, value).lower() # Normalize to lowercase.
        if User.objects.filter(email=value).count():
            raise forms.ValidationError('This e-mail address is already registered.')
        return value

class EmailRegistrationForm(forms.Form):
    email = UniqueEmailField(label='Your e-mail address', widget=forms.TextInput(attrs={'size': 50}))

class BasePasswordForm(forms.Form):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password (again)', widget=forms.PasswordInput)

    def clean_password2(self):
        p1 = self.cleaned_data['password1']
        p2 = self.cleaned_data['password2']
        if p1 != p2:
            raise forms.ValidationError("The passwords didn't match! Try entering them again.")
        return p2

class PasswordRegistrationForm(BasePasswordForm):
    e = UniqueEmailField(widget=forms.HiddenInput)
    h = forms.CharField(widget=forms.HiddenInput)

class PasswordResetForm(BasePasswordForm):
    e = forms.EmailField(widget=forms.HiddenInput)
    h = forms.CharField(widget=forms.HiddenInput)

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not User.objects.filter(email=email).count():
            raise forms.ValidationError("This e-mail address isn't registered yet.")
        return email

class LoginForm(AuthenticationForm):
    """Login form that uses email instead of username.
    """

    email = forms.EmailField()

    def clean(self):
        # Note that because this is the form-wide clean() method, any
        # validation errors raised here will not be tied to a particular field.
        # Instead, use form.non_field_errors() in the template.
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        # Check that both email and password were valid. If they're not valid,
        # there's no need to run the following bit of validation.
        if email and password:
            nonesuch = forms.ValidationError("That e-mail and password combo isn't valid. Note that the password is case-sensitive.") 
            user = User.objects.user_by_password(email.lower(), password)
            if user is None:
                raise nonesuch
            # Calling authenticate() queries the db again, but we call
            # it anyway because it has at least one important side
            # effect that we shouldn't have to duplicate.
            self.user_cache = authenticate(username=user.username, password=password)
            if self.user_cache is None:
                raise nonesuch
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")
            if not self.cleaned_data.get('username'):
                self.cleaned_data['username'] = self.user_cache.username
                self._errors.pop('username', None)

        self.check_for_test_cookie()
        return self.cleaned_data


class AdminLoginForm(LoginForm):
    """
    Login form that uses email instead of username, for accessing the admin site.
    """

    def clean(self):
        super(AdminLoginForm, self).clean()
        if not self.user_cache.is_active or not self.user_cache.is_staff:
            raise forms.ValidationError("Please enter a correct email address and password.")
        return self.cleaned_data

