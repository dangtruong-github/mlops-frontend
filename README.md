# Overview:
A movie renting website, with collaborative filtering recommendation module 

https://film-recommendation.onrender.com/

# Members
1. Chu Hữu Đăng Trường - 22022505
2. Nguyễn Đức Anh - 22022504
3. Nguyễn Kim Hoàng Anh - 22022566

# Function:
- Rent film
- Rate film after renting
- Watch film (not available right now)

# Collaborative filtering
More information could be found here: https://github.com/dangtruong-github/ml_module

# How to run
Step 1: Run ```git clone``` then ```pip install requirements.txt``` to install required packages

Step 2: Modify the ```.env``` file to connect to your database

Step 3: Run the following code:
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
