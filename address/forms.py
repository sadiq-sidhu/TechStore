from django import forms
from .models import Address
from django.contrib.auth.forms import PasswordChangeForm

class CustomerAddressForm(forms.ModelForm):
    
    class Meta:
        model = Address
        fields = ["name","mobile","type","locality",'city',"state","zip_code"]
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'mobile':forms.NumberInput(attrs={'class':'form-control'}),
            'type':forms.Select(attrs={'class':'form-control'}),
            'locality':forms.TextInput(attrs={'class':'form-control'}),
            'city':forms.TextInput(attrs={'class':'form-control'}),
            'state':forms.Select(attrs={'class':'form-control'}),
            'zip_code':forms.NumberInput(attrs={'class':'form-control'}),
        }
    def clean_mobile(self):
        mobile=self.cleaned_data['mobile']
        mobile_str=str(mobile)
        if not mobile_str.isdigit() or len(mobile_str) !=10:
            raise forms.ValidationError('Enter a valid 10-digits mobile number.')
        return mobile
    def clean_zip_code(self):
        zip_code=self.cleaned_data['zip_code']
        zip_str=str(zip_code)
        if not zip_str.isdigit() or len(zip_str) !=6:
            raise forms.ValidationError("Enter a valid 6-digit ZIP code.")
        return zip_code
    def clean_name(self):
        name=self.cleaned_data['name']
        if not name.replace(" ","").isalpha():
            raise forms.ValidationError("Name should contain only letters and spaces.")
        return name

class MyPasswordChangeForm(PasswordChangeForm):
    old_password=forms.CharField(label='Old Password', widget=forms.PasswordInput(attrs={'autofocus':'Ture','autocomplete':'current-password','class':'form-control'}))
    new_password1=forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'autocomplete':'current-password','class':'form-control'}))
    new_password2=forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'autocomplete':'current-password','class':'form-control'}))