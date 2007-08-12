"""
widgets.py

Custom widgets for base_case forms.
"""
from django import newforms as forms

class TextHiddenInput(forms.widgets.HiddenInput):
    """
    A widget that allows split date and time inputs to have separate attributes
    """
    is_hidden = False
    
    def __init__(self, attrs=None):
        if attrs is None or not attrs.has_key('display'):
            self.display = "Unknown instrument"
        else:
            self.display = attrs['display']
            del attrs['display']
        super(TextHiddenInput, self).__init__(attrs)
    
    def render(self, name, value, attrs=None):
        output = super(TextHiddenInput, self).render(name, value, attrs)
        return u'%s%s' % (output, self.display)
