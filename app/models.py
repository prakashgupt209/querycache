from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.cache import caches
from app.helpers import get_data_from_s3


class MyModel(models.Model):
    name = models.CharField(max_length=100)

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
    # key = f"mymodel_{instance.pk}_data"
    key = f"mymodel_data"
    cache = caches[settings.PREFERRED_CACHE]
    cache.delete(key)

@receiver(post_save, sender=MyModel)
def post_save_handler(sender, instance, **kwargs):
    """
    Handler for post-save signal to manage cache after saving the instance.
    """
    # key = f"mymodel_{instance.pk}_data"
    key = f"mymodel_data"
    queryset = MyModel.objects.all()
    data = queryset.get_data()
    data_json = data.to_json()

    cache = caches[settings.PREFERRED_CACHE]
    cache.set(key, data_json, timeout=settings.DEFAULT_CACHE_TIMEOUT)
