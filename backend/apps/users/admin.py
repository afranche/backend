from django import forms
from django.contrib import admin

from apps.users.models import Client, Address, MagicLink
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

# Register your models here.
class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ("client", "expires_at")
    list_filter = ("expires_at",)
    search_fields = ("client__email",)

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["name", "address1", "address2", "zip_code", "region", "city", "country"]

class ClientCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required fields, plus a
    repeated password. This form is used for user registration.
    """

    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Password confirmation"), widget=forms.PasswordInput
    )
    address_form = AddressForm()

    class Meta:
        model = Client
        fields = ["email"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        address = self.address_form.save()
        user.address = address

        if commit:
            user.save()
        return user

class ClientChangeForm(forms.ModelForm):
    """
    A form for updating user details, including associated address.
    """

    address_form = AddressForm()

    class Meta:
        model = Client
        fields = ["email"]

    def save(self, commit=True):
        user = super().save(commit=False)

        # Save the associated Address instance
        address = self.address_form.save()
        user.address = address

        if commit:
            user.save()

        return user

class UserAdmin(BaseUserAdmin):
    form = ClientChangeForm  # Use your UserChangeForm for editing users
    add_form = ClientCreationForm  # Use your UserCreationForm for adding users

    list_display = ["email", "is_staff",]
    list_filter = ["is_staff"]
    search_fields = ["email"]
    ordering = ["email"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name",)}),
        ("Permissions", {"fields": ("is_staff", )}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ["wide"],
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ("password",)

    raw_id_fields = ()

admin.site.register(MagicLink, MagicLinkAdmin)
admin.site.register(Client, UserAdmin)

admin.site.unregister(Group)