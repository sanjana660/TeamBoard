import secrets

from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Company


@receiver(pre_save, sender=User)
def cache_user_adding_state(sender, instance, **kwargs):
    instance._was_adding = instance._state.adding


@receiver(post_save, sender=User)
def create_company_profile(sender, instance, **kwargs):
    if getattr(instance, '_was_adding', False):
        Company.objects.create(
            user=instance,
            company_name=instance.email,
            api_key=secrets.token_urlsafe(32),
        )
