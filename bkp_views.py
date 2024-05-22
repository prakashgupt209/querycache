from django.http import HttpResponse
from .models import MyModel

# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")

def test_view(request):
    # Call the cached queryset method to fetch and cache data
    cached_result = MyModel.objects.all().cached("example_cache2_key",use_django=False)

    # Output the cached result or a message
    if cached_result:
        print("From the cache memory")
        return HttpResponse("Cached Data: {}".format(cached_result))
    else:
        print('Result returned from non cached memory')
        return HttpResponse("No Cached Data Found - {}".format(cached_result))

