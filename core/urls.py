from django.urls import path
from . import views

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
    path('dashboard/<str:username>/worldMap/', views.worldMapPage, name='mapPage'),
    # Ironstead town
    path('dashboard/<str:username>/ironstead/', views.ironsteadPage, name='mapPage'),

    # Ironstead market
    path('dashboard/<str:username>/market/', views.marketView, name='marketView'),
    path('dashboard/<str:username>/market/items', views.marketViewSendItems, name='getMarketItems'),
    # Ironstead blacksmith
    path('dashboard/<str:username>/blacksmith/', views.blackSmithView, name='blackSmithView'),
    path('dashboard/<str:username>/blacksmith/items', views.blackSmithFetch, name='getBlacksmithItems'),


]