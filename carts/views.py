from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from store.models import Movie
from carts.models import Cart, CartItem


def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id

def add_cart(request, movie_id):
    current_user = request.user
    movie = Movie.objects.get(id=movie_id)    # Get object movie
    if current_user.is_authenticated:
        # movie_variations = list()
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST.get(key)
                # try:
                #     variation = Variation.objects.get(movie=movie, variation_category__iexact=key, variation_value__iexact=value)
                #     movie_variations.append(variation)
                # except ObjectDoesNotExist:
                #     pass

        is_exists_cart_item = CartItem.objects.filter(movie=movie, user=current_user).exists()
        if is_exists_cart_item:
            cart_items = CartItem.objects.filter(
                movie=movie,
                user=current_user
            )
            # existing_variation_list = [list(item.variations.all()) for item in cart_items]
            id = [item.id for item in cart_items]
            # if movie_variations in existing_variation_list:
            #     idex = existing_variation_list.index(movie_variations)
            #     cart_item = CartItem.objects.get(id=id[idex])
            #     cart_item.quantity += 1
            # else:
            #     cart_item = CartItem.objects.create(
            #         movie=movie,
            #         user=current_user,
            #         quantity=1
            #     )
        else:
            cart_item = CartItem.objects.create(
                movie=movie,
                user=current_user,
                quantity=1
            )
        # if len(movie_variations) > 0:
        #     cart_item.variations.clear()
        #     for item in movie_variations:
        #         cart_item.variations.add(item)
        # cart_item.save()
        return redirect('cart')
    else:
        # movie_variations = list()
        # if request.method == 'POST':
        #     for item in request.POST:
        #         key = item
        #         value = request.POST.get(key)
        #         try:
        #             variation = Variation.objects.get(movie=movie, variation_category__iexact=key, variation_value__iexact=value)
        #             movie_variations.append(variation)
        #         except ObjectDoesNotExist:
        #             pass
        # try:
        #     cart = Cart.objects.get(cart_id=_cart_id(request=request))  # Get cart using the _cart_id
        # except Cart.DoesNotExist:
        #     cart = Cart.objects.create(
        #         cart_id=_cart_id(request)
        #     )
        # cart.save()

        # is_exists_cart_item = CartItem.objects.filter(movie=movie, cart=cart).exists()
        # if is_exists_cart_item:
        #     cart_items = CartItem.objects.filter(
        #         movie=movie,
        #         cart=cart
        #     )
        #     existing_variation_list = [list(item.variations.all()) for item in cart_items]
        #     id = [item.id for item in cart_items]
        #     if movie_variations in existing_variation_list:
        #         idex = existing_variation_list.index(movie_variations)
        #         cart_item = CartItem.objects.get(id=id[idex])
        #         cart_item.quantity += 1
        #     else:
        #         cart_item = CartItem.objects.create(
        #             movie=movie,
        #             cart=cart,
        #             quantity=1
        #         )
        # else:
        #     cart_item = CartItem.objects.create(
        #         movie=movie,
        #         cart=cart,
        #         quantity=1
        #     )
        # if len(movie_variations) > 0:
        #     cart_item.variations.clear()
        #     for item in movie_variations:
        #         cart_item.variations.add(item)
        # cart_item.save()
        return redirect('cart')


def remove_cart(request, movie_id, cart_item_id):
    movie = get_object_or_404(Movie, id=movie_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                id=cart_item_id,
                movie=movie,
                user=request.user
            )
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(
                id=cart_item_id,
                movie=movie,
                cart=cart
            )
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except Exception:
        pass
    return redirect('cart')


def remove_cart_item(request, movie_id, cart_item_id):
    movie = get_object_or_404(Movie, id=movie_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                id=cart_item_id,
                movie=movie,
                user=request.user
            )
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request=request))
            cart_item = CartItem.objects.get(
                id=cart_item_id,
                movie=movie,
                cart=cart
            )
        cart_item.delete()
    except Exception:
        pass
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request=request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.movie.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = total * 2 / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass    # Chỉ bỏ qua
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax if "tax" in locals() else "",
        'grand_total': grand_total if "tax" in locals() else 0,
    }
    return render(request, 'store/cart.html', context=context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        # cart = Cart.objects.get(cart_id=_cart_id(request=request))
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        for cart_item in cart_items:
            total += cart_item.movie.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = total * 2 / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass    # Chỉ bỏ qua
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax if "tax" in locals() else "",
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context=context)