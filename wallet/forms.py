from django import forms
class walletAddMoneyForm(forms.Form):
    amount = forms.DecimalField(max_digits=7,decimal_places=2,min_value=1.00,label="Amount to Add",
                                widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'Enter amount'}),)