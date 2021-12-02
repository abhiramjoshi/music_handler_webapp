from django.forms.forms import Form
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

class MergePlaylists(forms.Form):
    #Send api request to get the actual form
    platform = forms.CharField(required=True)
    existing_playlist = forms.BooleanField(initial=False, required=False)
    new_playlist_name = forms.CharField(required=False)
    new_playlist_description = forms.CharField(required=False)
    merge_playlist_id = forms.CharField(required=False)
    playlists_to_merge = forms.CharField()

    def clean(self):
        data = {
            "platform": self.cleaned_data.get("platform"),
            "existing_playlist": self.cleaned_data.get("existing_playlist", False),
            "new_playlist_name": self.cleaned_data.get("new_playlist_name", ''),
            "new_playlist_description": self.cleaned_data.get("new_playlist_description", ''),
            "merge_playlist_id": self.cleaned_data.get("merge_playlist_id", ''),
            "playlists_to_merge": self.cleaned_data.get("playlists_to_merge",  '')
        }
        data["playlists_to_merge"] = data["playlists_to_merge"].split(',')
        print(data)
        try:
            if data["existing_playlist"]:
                if data["merge_playlist_id"] == '':
                    raise forms.ValidationError(
                        _('Playlist to merge needs to be selected'),
                        code='invalid'
                    )
            elif not data["existing_playlist"]:
                print('not existing')
                if data["new_playlist_name"] == '':
                    raise forms.ValidationError(
                        _('New playlist requires a name'),
                        code='invalid'
                    )
            print('returning data: ', data)
            return data
        except Exception as e:
            raise forms.ValidationError(str(e))



    #plalists_to_merge = forms.MultipleChoiceField(required=True, label='playlists_to_merge', choices=playlists)
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