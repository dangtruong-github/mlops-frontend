from orders.models import OrderMovie
from django.contrib import messages
from store.forms import ReviewForm
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Max

from store.models import ReviewRating, Movie, ReviewMovieRating, Actor, CastCredit
from carts.models import Cart, CartItem
from category.models import Category
from carts.views import _cart_id

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .chatModel import response_AI
from datetime import datetime
import pytz

utc=pytz.UTC

def store(request, category_slug=None):
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        movies = Movie.objects.all().filter(genres=categories)
    else:
        movies = Movie.objects.all().order_by('?')

    page = request.GET.get('page')
    page = page or 1
    paginator = Paginator(movies, 3)
    paged_movies = paginator.get_page(page)
    movie_count = movies.count()

    context = {
        'movies': paged_movies,
        'movie_count': movie_count,
        "slug": False
    }
    return render(request, 'store/store.html', context=context)


def movie_detail(request, id):
    login_true = request.user.is_authenticated

    try:
        single_movie = Movie.objects.get(id=id)
        #print(single_movie)
        cart = Cart.objects.get(cart_id=_cart_id(request=request))
        in_cart = CartItem.objects.filter(
            cart=cart,
            movie=single_movie
        ).exists()
    except Exception as e:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )

    try:
        ordermovie = OrderMovie.objects.filter(user=request.user, movie_id=single_movie.id)

        ordermovie_true = ordermovie.exists()

        #for item in ordermovie:
            #print(item.expiry_date)

        ordermovie = ordermovie.aggregate(Max('expiry_date'))['expiry_date__max']

        ordermovie = ordermovie.replace(tzinfo=utc)
        datetime_now = datetime.now().replace(tzinfo=utc)
        #print(ordermovie >= datetime_now)
        #print(ordermovie)
        #print(datetime_now)
    except Exception as e:
        print(e)
        ordermovie = None
        ordermovie_true = False

    try:
        list_of_movies = [single_movie]
        cast_credits_for_movie = CastCredit.objects.filter(movie__in=list_of_movies)

        # Retrieve Actors based on the CastCredits
        actors_for_movie = Actor.objects.filter(castcredit__in=cast_credits_for_movie).distinct()

    except Exception as e:
        print(e)
        actors_for_movie = None
        

    reviews = ReviewRating.objects.filter(movie_id=single_movie.id)

    ratings = ["5", "4.5", "4", "3.5", "3", "2.5", "2", "1.5", "1", "0.5"]

    context = {
        'login_true': login_true,
        'single_movie': single_movie,
        'in_cart': in_cart if 'in_cart' in locals() else False,
        'ordermovie': ordermovie_true,
        'reviews': reviews,
        'ratings': ratings,
        "actors_for_movie": actors_for_movie
    }

    #print(context)

    return render(request, 'store/movie_detail.html', context=context)

def search(request):
    if 'q' in request.GET:
        q = request.GET.get('q')
        movies = Movie.objects.order_by('-release_date').filter(Q(title__icontains=q) | Q(overview__icontains=q))
        movie_count = movies.count()
    context = {
        'movies': movies,
        'q': q,
        'movie_count': movie_count,
        "slug": True
    }
    return render(request, 'store/store.html', context=context)


def sub_search(request):
    genre_ids = request.GET.getlist('genre')
    min_rating = float(request.GET.get('min_rating', 1))
    max_rating = float(request.GET.get('max_rating', 5))
    min_price = float(request.GET.get('min_price', 0))
    max_price = float(request.GET.get('max_price', 100000))
    release_date_min_str = request.GET.get('release_date_min', "")
    release_date_max_str = request.GET.get('release_date_max', "")
    actor_name = request.GET.get('actor', '')

    genre_ids = [int(genre_id) for genre_id in genre_ids]

    release_date_min = datetime.strptime(release_date_min_str, '%Y-%m-%d') if release_date_min_str else None
    release_date_max = datetime.strptime(release_date_max_str, '%Y-%m-%d') if release_date_max_str else datetime.now()

    # Start with all movies and then apply filters
    movies = Movie.objects.all()

    if genre_ids:
        movies = movies.filter(genres__id__in=genre_ids)

    if min_rating or max_rating:
        movies = movies.filter(vote_average__gte=min_rating, vote_average__lte=max_rating)

    if min_price or max_price:
        movies = movies.filter(price__gte=min_price, price__lte=max_price)


    if release_date_min:
        movies = movies.filter(release_date__gte=release_date_min, release_date__lte=release_date_max)
    else:
        movies = movies.filter(release_date__lte=release_date_max)


    if actor_name:
        # Lấy danh sách các bộ phim mà diễn viên đó tham gia
        movies = movies.filter(castcredit__actor__name__icontains=actor_name)
    movie_count = movies.count()
    context = {
        'movies': movies,
        'movie_count': movie_count,
        "actor": actor_name,
        "genre_ids": genre_ids,
        "min_rating": min_rating,
        "max_rating": max_rating,
        "min_price": min_price,
        "max_price": max_price,
        "release_date_min": release_date_min_str,
        "release_date_max": release_date_max_str,
        "slug": True
    }

    #print(context)

    return render(request, 'store/store.html', context=context)



def submit_review(request, movie_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
            review = ReviewRating.objects.get(user__id=request.user.id, movie__id=movie_id)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request, "Thank you! Your review has been updated.")
            return redirect(url)
        except Exception:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.movie_id = movie_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, "Thank you! Your review has been submitted.")
                return redirect(url)

@csrf_exempt
def submit_message(request, movie_id):
    if request.method == "POST":
        try:
            # Lưu tin nhắn vào cơ sở dữ liệu hoặc thực hiện các thao tác cần thiết
            message = request.POST.get('message', None)
            # Do something with the message
            response = response_AI(message= message)
            return JsonResponse({'success': True, 'message' : response})  # Trả về một phản hồi JSON thành công
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})  # Trả về một phản hồi JSON lỗi nếu có lỗi xảy ra
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})  # Trả về một phản hồi JSON lỗi nếu yêu cầu không hợp lệ