# Forms
from django import newforms as forms

class PatternForm(forms.Form):
    length = forms.IntegerField(maxlength=100)
