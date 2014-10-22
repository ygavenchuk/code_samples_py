#-*- coding: utf-8 -*-

from pkg.utils.tests.fixtureman import FixtureManager
from .base import *


__author__ = 'y.gavenchuk'
__all__ = ['AirportNotFoundTestCase', 'AirportFoundTestCase', 'MultiAirportsFoundTestCase', ]

_fx_places = FixtureManager()
_fx_places.load(fixture_file='airport')


class _AirportMixin(object):
    def _get_url(self):
        """
        Возвращает URL по которому нужно получить список сущностей

        :return str:
        """
        return '/place/airport'


class _AirportMetaMixin(type):
    @classmethod
    def _get_fixture_manager(mcs):
        return _fx_places


class AirportNotFoundMeta(_AirportMetaMixin, PlaceNotFoundMeta):
    pass


class AirportFoundMeta(_AirportMetaMixin, PlaceFoundMeta):
    pass


class MultipleAirportsFoundMeta(_AirportMetaMixin, MultiplePlacesFoundMeta):
    pass


class AirportNotFoundTestCase(_AirportMixin, PlaceNotFoundTestCase, metaclass=AirportNotFoundMeta):
    pass


class AirportFoundTestCase(_AirportMixin, PlaceFoundTestCase, metaclass=AirportFoundMeta):
    pass


class MultiAirportsFoundTestCase(_AirportMixin, MultiPlacesFoundTestCase, metaclass=MultipleAirportsFoundMeta):
    pass
