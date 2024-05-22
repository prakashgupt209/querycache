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

    data = MyModel.objects.get_data()   # this initiates
    # Create a new instance of MyModel with the retrieved data
    my_model_instance = MyModel()
    # Save the instance, triggering pre-save and post-save signals
    my_model_instance.save()

    print('data retrieved - {}'.format(data))
    # Output the retrieved data or a message
    if len(data) >= 1:
        print("Data retrieved successfully")
        return HttpResponse("Data Retrieved: {}".format(data))
    else:
        print("No data retrieved")
        return HttpResponse("No Data Retrieved")
