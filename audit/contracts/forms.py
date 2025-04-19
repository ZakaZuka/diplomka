# contracts/forms.py
from django import forms

class ContractUploadForm(forms.Form):
    contract_file = forms.FileField(label='Загрузите контракт (.sol)', required=False)
    contract_code = forms.CharField(
        label='Или вставьте код контракта',
        widget=forms.Textarea(attrs={'rows': 15}),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('contract_file') and not cleaned_data.get('contract_code'):
            raise forms.ValidationError("Нужно загрузить файл или вставить код.")
        return cleaned_data
