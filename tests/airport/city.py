#-*- coding: utf-8 -*-

from pkg.utils.tests.fixtureman import FixtureManager
from .base import *


__author__ = 'y.gavenchuk'
__all__ = ['CityNotFoundTestCase', 'CityFoundTestCase', 'MultiCitiesFoundTestCase', ]

_fx_places = FixtureManager()
_fx_places.load(fixture_file='city')


class _CityMixin(object):
    def _get_url(self):
        """
        Возвращает URL по которому нужно получить список сущностей

        :return str:
        """
        return '/place/city'


class _CityMetaMixin(type):
    @classmethod
    def _get_fixture_manager(mcs):
        return _fx_places


class CityNotFoundMeta(_CityMetaMixin, PlaceNotFoundMeta):
    pass


class CityFoundMeta(_CityMetaMixin, PlaceFoundMeta):
    pass


class MultipleCitiesFoundMeta(_CityMetaMixin, MultiplePlacesFoundMeta):
    pass


class CityNotFoundTestCase(_CityMixin, PlaceNotFoundTestCase, metaclass=CityNotFoundMeta):
    pass


class CityFoundTestCase(_CityMixin, PlaceFoundTestCase, metaclass=CityFoundMeta):
    pass


class MultiCitiesFoundTestCase(_CityMixin, MultiPlacesFoundTestCase, metaclass=MultipleCitiesFoundMeta):
    pass
