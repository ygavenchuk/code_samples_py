# -*- coding: utf-8 -*-

from django.dispatch.dispatcher import receiver

from pkg.notes.models import note_pre_size_change
from models import QuotaValidator


@receiver(note_pre_size_change)
def _validate_quota(sender, instance, prev_size, new_size, **kwargs):
    QuotaValidator(instance, prev_size, new_size).validate()
