# -*- coding: utf-8 -*-


from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings

from pkg.notes.models import NotesNotes
from client import send_request


@receiver(pre_save, sender=NotesNotes, )
def my_handler(sender, instance, **kwargs):
    server_url = getattr(settings, "PARSER_SERVER_URL", "http://parser-example.com/")
    parsed_text = send_request(server_url, instance.text)
    if parsed_text:
        instance.text = parsed_text.strip()
