from django.urls import path
from . import views
from django.conf.urls.static import static

from django.conf import settings


urlpatterns = [
    path('home/', views.homePage, name='home'),
    path('', views.homePage, name='home'),
    path('dashboard/<str:username>/', views.dashboardPage, name='dashboard'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('dashboard/<str:username>/task/', views.finish_task_route, name='finishQuest'),
    path('dashboard/<str:username>/character/', views.characterPage, name='characterPage'),
    path('dashboard/<str:username>/healthMotivation/', views.healthMotivation, name='healthMotivation'),
    # world map bellow.
    path('dashboard/<str:username>/worldMap/', views.worldMapPage, name='worldMapPage'),
    # Ironstead town
    path('dashboard/<str:username>/ironstead/', views.ironsteadPage, name='ironsteadPage'),
    # Ironstead market
    path('dashboard/<str:username>/ironstead/market/', views.marketView, name='marketView'),
    path('dashboard/<str:username>/ironstead/market/items', views.marketViewSendItems, name='getMarketItems'),
    # Ironstead blacksmith
    path('dashboard/<str:username>/ironstead/blacksmith/', views.blackSmithView, name='blackSmithView'),
    path('dashboard/<str:username>/ironstead/blacksmith/items', views.blackSmithFetch, name='getBlacksmithItems'),
    # Ironstead training
    path('dashboard/<str:username>/ironstead/training/', views.trainingView, name='trainingView'),
    path('dashboard/<str:username>/ironstead/training/grab', views.trainingGrab, name='trainingGrab'),
    # settings
    path('dashboard/<str:username>/settings/', views.settings, name='settings'),
    path('known/bugs', views.bugs, name='bugs'),

    #  guild
    path('dashboard/<str:username>/ironstead/guild/hall', views.ironsteadGuildHall, name='ironsteadGuild'),
    path('dashboard/<str:username>/ironstead/guild/hall/api', views.guildHallAPI, name='guildapi'),
    path('dashboard/<str:username>/npc', views.npc_chat_api, name='npc_chat_api'),

    #dead screen
    path('dead/<str:username>/', views.deadView, name='deadView'),
    path('404/', views.handler404, name='handler404'),  # remove in production
    path('500/', views.server_error_view, name='handler500'),  # remove in production
]
handler404 = 'core.views.handler404'
handler500 = 'core.views.server_error_view'


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)