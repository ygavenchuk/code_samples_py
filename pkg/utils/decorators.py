# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import update_wrapper


__all__ = ['render_to_json', ]


def render_to_json(func):
    def wrapper(request, *args, **kwargs):
        result = func(request, *args, **kwargs)
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, mimetype="application/json")
    return update_wrapper(wrapper, func)
