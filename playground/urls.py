from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#URL config
urlpatterns = [
    path('index/', views.index),
    path('index/getsummoner', views.get_summoner)
]

urlpatterns += staticfiles_urlpatterns()

