from orders.models import OrderMovie
from django.contrib import messages
from store.forms import ReviewForm
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.db.models import Q

from store.models import ReviewRating, Movie, ReviewMovieRating
from carts.models import Cart, CartItem
from category.models import Category
from carts.views import _cart_id

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .chatModel import response_AI
from datetime import datetime

def store(request, category_slug=None):
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        movies = Movie.objects.all().filter(genres=categories)
    else:
        movies = Movie.objects.all().order_by('id')

    page = request.GET.get('page')
    page = page or 1
    paginator = Paginator(movies, 3)
    paged_movies = paginator.get_page(page)
    movie_count = movies.count()

    context = {
        'movies': paged_movies,
        'movie_count': movie_count,
    }
    return render(request, 'store/store.html', context=context)


def movie_detail(request, id):
    try:
        single_movie = Movie.objects.get(id=id)
        print(single_movie)
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
        ordermovie = OrderMovie.objects.filter(user=request.user, movie_id=single_movie.id).exists()
    except Exception:
        ordermovie = None

    reviews = ReviewRating.objects.filter(movie_id=single_movie.id)

    ratings = ["5", "4.5", "4", "3.5", "3", "2.5", "2", "1.5", "1", "0.5"]

    context = {
        'single_movie': single_movie,
        'in_cart': in_cart if 'in_cart' in locals() else False,
        'ordermovie': ordermovie,
        'reviews': reviews,
        'ratings': ratings
    }
    return render(request, 'store/movie_detail.html', context=context)

def search(request):
    if 'q' in request.GET:
        q = request.GET.get('q')
        movies = Movie.objects.order_by('-release_date').filter(Q(title__icontains=q) | Q(overview__icontains=q))
        movie_count = movies.count()
    context = {
        'movies': movies,
        'q': q,
        'movie_count': movie_count
    }
    return render(request, 'store/store.html', context=context)


def sub_search(request):
    genre_ids = request.GET.getlist('genre')
    min_rating = request.GET.get('min_rating', 1)
    max_rating = request.GET.get('max_rating', 5)
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 2000)
    release_date_min_str = request.GET.get('release_date_min', '')
    release_date_max_str = request.GET.get('release_date_max', '')
    actor_name = request.GET.get('actor', '')



    release_date_min = datetime.strptime(release_date_min_str, '%Y-%m-%d') if release_date_min_str else None
    release_date_max = datetime.strptime(release_date_max_str, '%Y-%m-%d') if release_date_max_str else None

    # Start with all movies and then apply filters
    movies = Movie.objects.all()

    if genre_ids:
        movies = movies.filter(genres__id__in=genre_ids)

    if min_rating or max_rating:
        movies = movies.filter(vote_average__gte=min_rating, vote_average__lte=max_rating)

    if min_price or max_price:
        movies = movies.filter(price__gte=min_price, price__lte=max_price)


    if release_date_max:
        # Để xử lý trường hợp người dùng không nhập ngày kết thúc, chúng ta sẽ xem xét các bộ phim có release_date không quá ngày tìm kiếm
        release_date_max = release_date_max.replace(hour=23, minute=59, second=59)  # Đặt giờ, phút và giây cuối cùng của ngày
        movies = movies.filter(release_date__lte=release_date_max)

    if actor_name:
        # Lấy danh sách các bộ phim mà diễn viên đó tham gia
        movies = movies.filter(castcredit__actor__name__icontains=actor_name)
    movie_count = movies.count()
    context = {
        'movies': movies,
        'movie_count': movie_count
    }
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