from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='movies_by_category'),
    path('search/', views.search, name='search'),
    path('sub_search/', views.sub_search, name='sub_search'),
    path('submit_review/<int:movie_id>/', views.submit_review, name='submit_review'),
    path('submit_message/<int:movie_id>/', views.submit_message, name='submit_message'),
    path('movie/<slug:id>/', views.movie_detail, name='movie_detail'),
]