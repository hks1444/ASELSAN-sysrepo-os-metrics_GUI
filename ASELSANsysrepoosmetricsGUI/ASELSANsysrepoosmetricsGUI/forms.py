from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit,Layout, Field
from dotenv import load_dotenv
import os

class ConnectForm(forms.Form):
    load_dotenv()
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    username = os.getenv('USERNAME')
    host = forms.CharField(label='Host', max_length=100, initial=host)
    port = forms.IntegerField(label='Port', initial=port)
    username = forms.CharField(label='Username', max_length=100, initial=username)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Connect'))

class ConfigTypeForm(forms.Form):
    # Assuming config_methods is a list of tuples like [('method1', 'Method 1'), ('method2', 'Method 2'), ...]
    # You would dynamically populate the choices in the view before rendering the form
    method = forms.ChoiceField(choices=[], label="Select Configuration Method")

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', [])
        super(ConfigTypeForm, self).__init__(*args, **kwargs)
        self.fields['method'].choices = choices
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
                