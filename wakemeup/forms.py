from django import forms

class SchoolForm(forms.Form):

    schoolid = forms.IntegerField(
        label='School Id', 
        required=False, 
        widget=forms.HiddenInput()
    )
    schooldisplayname = forms.CharField(
        label='Display name',
        max_length=100
    )
    address = forms.CharField(
        label='Address',
        max_length=100
    )
    city = forms.CharField(
        label='City',
        max_length=100
    )
    department = forms.CharField(
        label='Department',
        max_length=100
    )