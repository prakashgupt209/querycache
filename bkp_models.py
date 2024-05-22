from django.db import models

# Create your models here.
import redis
import pandas as pd
from django.db import models
from django.conf import settings
from django.core.cache import cache
from app.helpers import get_data_from_s3

# Initialize Redis connection
redis_connection = redis.StrictRedis(host=settings.REDIS_HOST,
                                     port=settings.REDIS_PORT,
                                     db=settings.REDIS_DB)

class MyModel(models.Model):
    name = models.CharField(max_length=100)

    class CachedQuerySet(models.QuerySet):
        def get_data(self):
            """
            Called to hit the DB and get data
            :return: dataframe
            """
            return get_data_from_s3()

        def cached(self, key, use_django = False, timeout=settings.DEFAULT_CACHE_TIMEOUT):
            """
            Custom queryset method to cache query results in Redis.
            """
            if use_django:
                cached_data = cache.get(key)
                if cached_data:
                    return cached_data
                result = self.get_data()
                result = result.to_json()
                cache.set(key, result, timeout=timeout)
                return result
            else:
                # Check if data is already cached
                cached_data = redis_connection.get(key)
                if cached_data:
                    # If cached data exists, return it
                    return cached_data

                # If data is not cached, execute the get_data() function and cache the result
                result = self.get_data()
                result = result.to_json()
                redis_connection.set(key, result, ex=timeout)
                return result

    objects = CachedQuerySet.as_manager()

