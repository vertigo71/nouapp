from django import forms

from .models import Person


my_default_errors = {
    'required': 'This field is required',
    'invalid': 'Enter a valid value',
}

class SelectorForm(forms.Form):
    name =  forms.ModelChoiceField(queryset=Person.objects.all(), initial = '1', label="Name")
    datefrom = forms.DateField(label="Initial Date", widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    dateto = forms.DateField(label="End Date", widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    
    def clean(self):
        cleaned_data = super(SelectorForm, self).clean()
        dfrom = cleaned_data.get("datefrom")
        dto = cleaned_data.get("dateto")

        if dfrom and dto:
            # Only do something if both fields are valid so far.
            if dfrom > dto:
                raise forms.ValidationError( 'The start date is after the end date' )
                    
