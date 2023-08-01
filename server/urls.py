from django.urls import include
from django.urls import path, re_path
from . import views
app_name = 'server'
urlpatterns = [
    path('', views.index, name='index.html'),
    #path('log_out/', views.log_out, name='log_out'),
    # path('ws/video/', views.VideoConsumer.as_asgi()),
]