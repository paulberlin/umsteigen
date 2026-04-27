from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contact', views.contact, name='contact'),
    path('contact/', views.contact, name='contact'),
    path('stats', views.stats, name='stats'),
    path('privacy', views.privacy, name='privacy'),
    path('line/<int:id>/', views.line_detail, name='line_detail'),
    path('line/<slug:urlname>/', views.line_detail_name, name='line_detail_name'),
    path('line/<int:id>/<slug:sequence>', views.line_detail, name='line_detail'),
    path('line/', views.line_list, name='line_list'),
    path('station/<int:id>/', views.station_detail, name='station_detail'),
    path('station/<slug:urlname>/', views.station_detail_name, name='station_detail_name'),
    #path('station/<slug:urlname>/<slug:thanks>', views.station_detail_name, name='station_detail_name'),
    path('station/<int:id>', views.station_detail, name='station_detail'),
    path('station/<int:id>/add_change', views.station_add_change, name='station_add_change'),
    path('station/', views.station_list, name='station_list'),
]

