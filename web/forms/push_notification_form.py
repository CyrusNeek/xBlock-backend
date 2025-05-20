from django import forms
from web.models import User

class NotificationForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )
    body = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
            }
        )
    )
    data = forms.CharField(
        required=False,
        # widget=forms.Textarea(
        #     attrs={
        #         "class": "form-control",
        #         "rows": 5,
        #     }
        # )
    )
    send_to_all = forms.BooleanField(
        required=False,
        label="Send to all users",
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input"
            }
        )
    )
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-control",
                "size": "5"
            }
        )
    )
