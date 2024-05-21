from django.shortcuts import render
from store.models import Product, Movie

def home(request):
    products = Movie.objects.all().filter()
    context = {
        'products': products,
    }
    return render(request, 'home.html', context=context)