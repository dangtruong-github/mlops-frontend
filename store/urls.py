from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:movie_id>/', views.submit_review, name='submit_review'),
    path('submit_message/<int:movie_id>/', views.submit_message, name='submit_message'),
    path('movie/<slug:id>/', views.movie_detail, name='movie_detail'),
]