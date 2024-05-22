from django.http import HttpResponse
from .models import MyModel
import pandas as pd
from django.core.cache import cache

def test_view(request):

    key = "mymodel_data"
    cached_data = cache.get(key)

    if cached_data:
        print("Data retrieved from cache memory successfully")
        return HttpResponse("From Cache: {}".format(cached_data))

    # Retrieve data and save it
    queryset = MyModel.objects.all()
    data = queryset.get_data()
    my_model_instance = MyModel(name="example")
    my_model_instance.save()  # This will trigger pre-save and post-save signals

    print('data retrieved - {}'.format(data))
    # Output the retrieved data or a message
    if len(data) >= 1:
        print("Data retrieved successfully")
        return HttpResponse("Data Retrieved: {}".format(data))
    else:
        print("No data retrieved")
        return HttpResponse("No Data Retrieved")
