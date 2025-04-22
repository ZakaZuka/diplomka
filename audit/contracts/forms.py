# contracts/forms.py
# from django import forms

# class ContractUploadForm(forms.Form):
#     contract_file = forms.FileField(
#         label='Загрузите Solidity-файл  (.sol)',
#         required=False,
#         widget=forms.ClearableFileInput(attrs={
#             'id': 'file-upload',
#             'style': 'display: none;'
#         })
#     )

#     contract_code = forms.CharField(
#         label='Или вставьте код контракта',
#         widget=forms.Textarea(attrs={'rows': 15}),
#         required=False
#     )

#     def clean(self):
#         cleaned_data = super().clean()
#         if not cleaned_data.get('contract_file') and not cleaned_data.get('contract_code'):
#             raise forms.ValidationError("Нужно загрузить файл или вставить код.")
#         return cleaned_data

from django import forms

class ContractForm(forms.Form):
    contract_file = forms.FileField(label='Файл контракта (.sol)', required=False)
    contract_code = forms.CharField(
        label='Или вставьте код контракта',
        widget=forms.Textarea(attrs={'rows': 10}),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('contract_file')
        code = cleaned_data.get('contract_code')

        if not file and not code:
            raise forms.ValidationError("Пожалуйста, загрузите файл или вставьте код контракта.")
        return cleaned_data
