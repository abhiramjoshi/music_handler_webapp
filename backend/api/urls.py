from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('test/', views.test, name='test'),
    path('authorize/spotify/', views.spotify_auth, name='spotify_authorization'),
    path('callback/spotify/', views.spotify_callback, name='spotify_authorization_callback'),
    path('spotify/landing/', views.SpotifyRequests.as_view(), name='spotify_landing'),
    path('spotify/playlists/', views.spotify_playlists, name='spotify_playlists'),
    path('authorize/callback/', views.callback, name='authorization_callback'),
    path('authorize/apple/', views.apple_auth, name='apple_authorization'),
    path('callback/apple/', views.apple_callback, name='apple_authorization_callback'),
    path('authorize/YTMusic', views.YT_get_headers, name='ytmusic_authorization'),
    path('YTMusic/landing/', views.YTRequests.as_view(), name='ytmusic_landing'),
    path('YTMusic/playlists/', views.YT_playlists, name='ytmusic_playlists'),
    path('merge/', views.merge.as_view(), name='merge'),
    path('transfer/', views.tranfer, name='transfer')
]
