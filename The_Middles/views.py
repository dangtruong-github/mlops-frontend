from django.shortcuts import render
from store.models import Movie

def home(request):
    movies = Movie.objects.all().filter()
    context = {
        'movies': movies,
    }
    return render(request, 'home.html', context=context)