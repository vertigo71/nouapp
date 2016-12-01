from django import forms
from django.utils import timezone

from .models import Person



class SelectorForm(forms.Form):
    name =  forms.ModelChoiceField(queryset=Person.objects.all(), initial = '1', label="Name", help_text="Exactly like in the Excel File")
    datefrom = forms.DateField(label="Initial Date", widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    dateto = forms.DateField(label="End Date", widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    
    def clean(self):
        cleaned_data = super(SelectorForm, self).clean()
        dfrom = cleaned_data.get("datefrom")
        dto = cleaned_data.get("dateto")

        if dfrom and dto:
            # Only do something if both fields are valid so far.
            if dfrom > dto:
                raise forms.ValidationError( 'Initial date is later than Final' )
                
