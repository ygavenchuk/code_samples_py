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
    """
        Data provider decorator, allows another callable to provide the data
        for the test. If data_set_source is empty or (if callable) return
        empty sequence will be raise ValueError exception

        :param collections.Iterable | callable data_set_source: data source

        :raises: TypeError|ValueError
    """

    from collections import Iterable

    def get_data_source():
        if callable(data_set_source):
            data_source = data_set_source()
        elif isinstance(data_set_source, Iterable):
            data_source = data_set_source
        else:
            raise TypeError("The '%s' is unsupported type of data set source!" % type(data_set_source))

        if not data_source:
            raise ValueError("There's no data in current data set!")

        return data_source

    def test_decorator(fn):
        def repl(self, *args):
            # The setUp method has been called already.
            # And the tearDown cannot be called after last iteration
            # The next code solves this contradiction
            def _set_up():
                """
                Replace local setUp function to the original TestCase's instance
                """
                repl._setUp = self.setUp

            def _tear_down():
                """
                Replace local tearDown function to the original TestCase's instance
                """
                repl._tearDown = self.tearDown

            repl._setUp = _set_up
            repl._tearDown = _tear_down

            data_source = get_data_source()
            step = 0
            for i in data_source:
                repl._tearDown()
                repl._setUp()

                try:
                    fn(self, *i)
                    step += 1
                except AssertionError:
                    print("Step #%i. Assertion error caught with data set " % step, i)
                    raise

        return update_wrapper(repl, fn)
    return test_decorator

