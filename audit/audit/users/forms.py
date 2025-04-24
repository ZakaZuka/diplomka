from django import forms

class MetaMaskAuthForm(forms.Form):
    address = forms.CharField(max_length=42)
    signature = forms.CharField()
    message = forms.CharField()