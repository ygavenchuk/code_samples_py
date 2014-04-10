# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import update_wrapper


__all__ = ['render_to_json', 'data_provider', ]


def render_to_json(func):
    def wrapper(request, *args, **kwargs):
        result = func(request, *args, **kwargs)
        json_data = json.dumps(result, cls=DjangoJSONEncoder)
        return HttpResponse(json_data, mimetype="application/json")
    return update_wrapper(wrapper, func)


def data_provider(data_set_source):
    """Data provider decorator, allows another callable to provide the data for the test"""

    from collections import Iterable

    def test_decorator(fn):
        def repl(self, *args):

            if callable(data_set_source):
                data_list = data_set_source()
            elif isinstance(data_set_source, Iterable):
                data_list = data_set_source
            else:
                data_list = None

            #if you need some method that would be runed after each fixture iteration
            #write your own _after_fixture_action() in test case
            if hasattr(self, '_after_fixture_action'):
                after_fixture_hook = self._after_fixture_action
            else:
                after_fixture_hook = lambda: None

            for i in data_list:
                try:
                    fn(self, *i)
                except AssertionError:
                    print "Assertion error caught with data set ", i
                    raise
                finally:
                    after_fixture_hook()

        return repl
    return test_decorator
