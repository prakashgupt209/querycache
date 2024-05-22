### Create a django project
django-admin startproject querycache

### cd myproject
python manage.py startapp app

### Update configuration in setings.py
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
DEFAULT_CACHE_TIMEOUT = 3600  # 1 hour

### Migrate Database
python manage.py makemigrations
python manage.py migrate

### To run the django server
python manage.py runserver 8080 (optional to provide the port)

### How to test the cache method

Go and hit the url 127.0.0.1:8080/test
This will initiate the get_data function which will fetch results from DB (in our case Glue DB)
and return the results.
Once you recieve the results in the URL.

Now as per the code after first time retrieval it will always cache the data ,
so that next time it doesnt have to hit the DB again

Now terminate the app (ctrl+c) in your terminal
Re-run the django server now using the python command in above line
Now when you go and hit 127.0.0.1:8080/test

You will have the data displayed in no time in the URL.
Thus proves that how fast data retrieval can be , once done from cache layer

