from django.urls import path
from . import views
# from django.views.generic.base import RedirectView
# from django.contrib.staticfiles.storage import staticfiles_storage

urlpatterns = [
    path('', views.loadDC, name = "loadDC"),
    path('home/', views.home, name = "home"),
    path('tags/', views.tags, name="tags"),
    path('analysis/', views.analysis, name="analysis")
] 