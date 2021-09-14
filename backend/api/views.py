from os import error
from django.views.generic import TemplateView
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .spotifyhandler.spotify_auth import *
from .spotifyhandler.spotifyhandler import *
from .ytmusichandler.ytmusichandler import *
from .utils import *
from .forms import YTHeadersForm
import datetime


def home(request:HttpRequest):
    context = {}
    return render(request, 'home.html', context=context)

def test(request: HttpRequest):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def callback(request: HttpRequest):
    code = request.GET.get('code')
    count = request.session.get('redirect_count', 0)
    request.session['redirect_count'] = count + 1
    return HttpResponse(code, count)

class SpotifyRequests(TemplateView, LoginRequiredMixin):
    
    def get(self, request, *args, **kwargs):
        user = self.request.user
        print(user)
        if user.SpotifyAPIKey is not None:
            return render(request, 'playlist_grid.html', context={'platform': 'spotify'})
        else:
            return redirect("spotify_authorization")

@login_required
def spotify_playlists(request:HttpRequest):
    user = request.user
    try:
        handler = SpotifyHandler(user.SpotifyAPIKey)
        playlists = handler.get_playlists()
        playlists = standardPlaylistJSON(playlists)
        return JsonResponse(playlists, safe=False, json_dumps_params={'indent': 4})
    except RefreshRequired:
        try:
            response = refresh_token(user.SpotifyRefreshToken)
            user.SpotifyAPIKey = response['access_token']
            user.save()
        except NoTokenException:
            user.SpotifyAPIKey = None
            user.SpotifyRefreshToken = None
            user.save()
            return redirect('spotify_authorization')
        except:
            pass
        return redirect('spotify_landing')

@login_required
def spotify_auth(request: HttpRequest):
    """Handles the initial request to authorize spotify"""
    response, params = send_auth_request()
    return HttpResponseRedirect(response.url)

def spotify_callback(request: HttpRequest):
    """Handles the spotify call back"""
    user = request.user
    code = request.GET.get('code')
    if code == None:
        try:
            resonse = request.GET.get('error')
            resp_context = {
                'error':resonse
            }
            return render(request, 'error.html', context=resp_context)
        except KeyError:
            return render(request, 'error.html', context={'error': 'There was an unknown error authorizing Sotify'})
    access_code, refresh = exchange_code_for_token(code)
    if user.is_authenticated:
        user.SpotifyAPIKey = access_code
        user.SpotifyRefreshToken = refresh
        user.save()
        return render(request, 'success.html', context={'success_message': 'Spotify has been authenticated'})
    else:
        return render(request, 'error.html', context={'error': 'User not logged in'})

def apple_auth(request: HttpRequest, *args, **kwargs):
    pass

def apple_callback(request: HttpRequest, *args, **kwargs):
    pass

@login_required()
def YT_get_headers(request: HttpRequest, *args, **kwargs):
    user = request.user
    next_url = request.POST.get('next') or None
    print('next_url', request.POST)
    form = YTHeadersForm(request.POST or None)
    #form = YTHeadersForm(request.POST or None, instance=user)
    #print('Cleaned data  \n', form.cleaned_data)
    if form.is_valid():
        user.YTHeaders = form.cleaned_data["YTHeaders"]
        user.save()
        if request.is_ajax():
            print('Getting here')
            return JsonResponse(data = json.loads(form.cleaned_data["YTHeaders"]), status=201, safe=False)
        if next_url != None:
            return redirect(next_url)
        form = YTHeadersForm()
    elif form.errors:
        if request.is_ajax():
            print("Here")
            return JsonResponse(data = form.errors, status=400, safe=False)
    return render(request, 'YTHeadersInput.html', context={'form': form})

class YTRequests(TemplateView, LoginRequiredMixin):
    
    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.YTHeaders is not None:
            try:
                return render(request, 'playlist_grid.html', context={'platform': 'ytmusic'})
            except (RefreshRequired, HeadersAuthenticationError):
                user.YTHeaders = None
                user.save()
                return redirect('ytmusic_authorization')
        else:
            return redirect("ytmusic_authorization")

@login_required()
def YT_playlists(request: HttpRequest, *args, **kwargs):
    user = request.user
    try:
        #Make a get headers function for YTMusic in the handler class
        handler = YTMusicHandler(user.YTHeaders)
        playlists = handler.get_playlist()
        playlists = standardPlaylistJSON(playlists)
        #return render(request, "playlist_grid.html", context={'playlists': playlists, 'platform': 'YTMusic'})
        return JsonResponse(playlists, safe=False, json_dumps_params={'indent': 4})
    except (RefreshRequired, HeadersAuthenticationError):
        user.YTHeaders = None
        user.save()
        return redirect('ytmusic_authorization')
    except Exception:
        user.YTHeaders = None
        user.save()
        return redirect('ytmusic_authorization')