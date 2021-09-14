from . import utils
from django import forms
from django.db.models import fields
from ytmusicapi import setup
from .models import Profile

class YTHeadersForm(forms.Form):
    cookie = forms.CharField(empty_value='')
    x_goog_authuser = forms.CharField()
    x_goog_visitor_id = forms.CharField()

    def clean(self):
        headers = {
            "cookie": self.cleaned_data.get("cookie"),
            "x-goog-authuser": self.cleaned_data.get("x_goog_authuser"),
            "x-goog-visitor-id": self.cleaned_data.get("x_goog_visitor_id")
        } 
        #print('Header \n', headers)
        try:
            if headers is None:
                headers = 'Empty'
            utils.verify_ytheaders(headers)
            validated_headers = setup.setup(headers_raw='\n'.join([f'{key}: {headers[key]}' for key in headers]))
            #print('Validated Headers \n', validated_headers)
            # Add specific verification for header fields.
            return {'YTHeaders': str(validated_headers)}
        except Exception as e:
            #print(str(e))
            raise forms.ValidationError(str(e))

# class YTHeadersForm(forms.ModelForm):
#     # cookie = forms.CharField()
#     # x_goog_authuser = forms.CharField()
#     # x_goog_visitor_id = forms.CharField()
#     class Meta:
#         model = Profile
#         fields = ['YTHeaders']

#     def clean(self):
#         headers = self.cleaned_data.get("YTHeaders")
#         print('Header \n', headers)
#         try:
#             if headers is None:
#                 headers = 'Empty'
#             validated_headers = setup.setup(headers_raw=headers)
#             print('Validated Headers \n', validated_headers)
#             return {'YTHeaders': str(validated_headers)}
#         except Exception:
#             raise forms.ValidationError("Issue validating headers, incorrect header format")