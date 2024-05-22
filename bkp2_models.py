from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import redis
import pandas as pd
from django.conf import settings
from django.core.cache import cache
from app.helpers import get_data_from_s3

# Initialize Redis connection
redis_connection = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

# class MyModelQuerySet(models.QuerySet):
#     def create(self, **kwargs):
#         instance = super().create(**kwargs)
#         self._update_cache(instance)
#         return instance
#
#     def update(self, **kwargs):
#         instance = super().update(**kwargs)
#         self._update_cache(instance)
#         return instance
#
#     def _update_cache(self, instance):
#         """
#         Update cache after saving the instance.
#         """
#         key = f"mymodel_{instance.pk}_data"
#         queryset = self.all()
#         data = queryset.get_data()
#         data_json = data.to_json()
#         cache.set(key, data_json, timeout=settings.DEFAULT_CACHE_TIMEOUT)
#         redis_connection.set(key, data_json, ex=settings.DEFAULT_CACHE_TIMEOUT)
#
# class MyModelManager(models.Manager):
#     def get_queryset(self):
#         return MyModelQuerySet(self.model)

class MyModel(models.Model):
    name = models.CharField(max_length=100)

    # objects = MyModelManager()

    class CachedQuerySet(models.QuerySet):
        def get_data(self):
            """
            Called to hit the DB and get data
            :return: dataframe
            """
            return get_data_from_s3()

    objects = CachedQuerySet.as_manager()


@receiver(pre_save, sender=MyModel)
def pre_save_handler(sender, instance, **kwargs):
    """
    Handler for pre-save signal to manage cache before saving the instance.
    """
    key = f"mymodel_{instance.pk}_data"
    print(f"Pre-save handler triggered for key: {key}")
    if cache.get(key):
        cache.delete(key)
    if redis_connection.exists(key):
        redis_connection.delete(key)

@receiver(post_save, sender=MyModel)
def post_save_handler(sender, instance, **kwargs):
    """
    Handler for post-save signal to manage cache after saving the instance.
    """
    key = f"mymodel_{instance.pk}_data"
    print(f"Post-save handler triggered for key: {key}")
    queryset = MyModel.objects.all()
    data = queryset.get_data()
    data_json = data.to_json()
    cache.set(key, data_json, timeout=settings.DEFAULT_CACHE_TIMEOUT)
    redis_connection.set(key, data_json, ex=settings.DEFAULT_CACHE_TIMEOUT)
