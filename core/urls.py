from django.urls import path
from . import views
from django.conf.urls.static import static

from django.conf import settings


urlpatterns = [
    path('home/', views.homePage, name='home'),
    path('', views.homePage, name='home'),
    path('api/redeem/', views.collect_email, name='collect_email'),
    path('privacy/policy', views.privacyPolicy, name='privacyPolicy'),
    path('terms/service', views.termsService, name='termsService'),
    # dashboard
    path('dashboard/<str:username>/', views.dashboardPage, name='dashboard'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('dashboard/<str:username>/task/', views.finish_task_route, name='finishQuest'),
    path('dashboard/<str:username>/task/view', views.userTasks, name='userTasks'),
    # character menu and character chat
    path('dashboard/<str:username>/character/', views.characterPage, name='characterPage'),
    path('dashboard/<str:username>/character/talk/', views.characterTalk, name='characterTalk'),

    # world map bellow.
    path('dashboard/<str:username>/worldMap/', views.worldMapPage, name='worldMapPage'),
    # IRONSTEAD TOWN
    path('dashboard/<str:username>/ironstead/', views.ironsteadPage, name='ironsteadPage'),
    path('dashboard/<str:username>/ironstead/logging/', views.ironsteadLogging, name='ironsteadLogging'),

    # Ironstead market
    path('dashboard/<str:username>/ironstead/market/', views.marketView, name='marketView'),
    path('dashboard/<str:username>/ironstead/market/items', views.marketViewSendItems, name='getMarketItems'),
    # Ironstead blacksmith
    path('dashboard/<str:username>/ironstead/blacksmith/', views.blackSmithView, name='blackSmithView'),
    path('dashboard/<str:username>/ironstead/blacksmith/items', views.blackSmithFetch, name='getBlacksmithItems'),
    # Ironstead training
    path('dashboard/<str:username>/ironstead/training/', views.trainingView, name='trainingView'),
    path('dashboard/<str:username>/ironstead/training/grab', views.trainingGrab, name='trainingGrab'),
    #  guild
    path('dashboard/<str:username>/ironstead/guild/hall', views.ironsteadGuildHall, name='ironsteadGuild'),
    path('dashboard/<str:username>/ironstead/guild/hall/api', views.guildHallAPI, name='guildapi'),
    path('dashboard/<str:username>/npc', views.npc_chat_api, name='npc_chat_api'),

    # STORMWATCH TOWN
    path('dashboard/<str:username>/stormwatch/', views.stormwatchPage, name='stormwatchPage'),
    path('dashboard/<str:username>/stormwatch/alchemist', views.swAlchemist, name='swAlchemist'),

    # settings
    path('dashboard/<str:username>/settings/', views.settings, name='settings'),
    path('known/bugs', views.bugs, name='bugs'),

    #  adventure quests
    path('<str:username>/adventure/quest/', views.adventureQuests, name='adventureQuests'),
    path('<str:username>/adventure/quest/api', views.adventureQuestsAPI, name='adventureQuestsAPI'),
    path('<str:username>/adventure/quest/end/api', views.adventureQuestEndAPI, name='adventureQuestEndAPI'),
    path('<str:username>/adventure/quest/story/gen', views.adventureQuestsStoryGen, name='adventureQuestsStoryGen'),

    #dead screen
    path('dead/<str:username>/', views.deadView, name='deadView'),
    path('404/', views.handler404, name='handler404'),  # remove in production
    path('500/', views.server_error_view, name='handler500'),  # remove in production

    # complete tutorial
    path('api/complete_tutorial/', views.completeTutorial, name='completeTutorial'),
    # fuel my fire
    path('fuel/my/fire/', views.fuel_My_Fire, name='fuel_My_Fire'),

    #  blog
    path('blog/', views.blogView, name="blog_page"),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),

]
handler404 = 'core.views.handler404'
handler500 = 'core.views.server_error_view'


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
