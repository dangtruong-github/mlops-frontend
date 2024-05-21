from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderMovie
from store.models import Product, Movie
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def sendEmail(request, order):
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()


def payments(request):
    print('hello')
    try:
        if  request.method == 'POST':
            data = request.POST
            order_id = data['orderID']
            trans_id = data['transID']
            payment_method = data['payment_method']
            status = data['status']

            # Lấy bản ghi order
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_id)
            # Tạo 1 bản ghi payment
            payment = Payment(
                user=request.user,
                payment_id=trans_id,
                payment_method=payment_method,
                amount_paid=order.order_total,
                status=status,
            )
            payment.save()

            order.payment = payment
            order.is_ordered = True
            order.save()

            # Chuyển hết cart_item thành order_product
            cart_items = CartItem.objects.filter(user=request.user)
            for item in cart_items:
                order_movie = OrderMovie()
                order_movie.order_id = order.id
                order_movie.payment = payment
                order_movie.user_id = request.user.id
                order_movie.movie_id = item.movie_id
                order_movie.quantity = item.quantity
                order_movie.movie_price = item.movie.price
                order_movie.ordered = True
                order_movie.save()

                cart_item = CartItem.objects.get(id=item.id)
                # movie_variation = cart_item.variations.all()
                order_movie = OrderMovie.objects.get(id=order_movie.id)
                # order_movie.variations.set(movie_variation)
                order_movie.save()

                # Reduce the quantity of the sold movies
                movie = Movie.objects.get(id=item.movie_id)
                # movie.stock -= item.quantity
                movie.save()

            # # Xóa hết cart_item
            CartItem.objects.filter(user=request.user).delete()

            # Gửi thư cảm ơn
            # sendEmail(request=request, order=order)

            # Phản hồi lại ajax
            data = {
                'order_number': order.order_number,
                'transID': payment.payment_id,
            }
        return JsonResponse({"data": data}, status=200)
    except Exception as e:
        return JsonResponse({"error": e}, status=400)


def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.movie.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")     # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_movies = OrderMovie.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_movies:
            subtotal += i.movie_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_movies': ordered_movies,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        print('succes')
        return render(request, 'orders/order_complete.html', context)
    except Exception:
        return redirect('home')