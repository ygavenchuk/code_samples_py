#-*- coding: utf-8 -*-

import json
from abc import abstractmethod, abstractclassmethod

from django.test import TestCase

from pkg.utils.decorators import data_provider


__author__ = 'y.gavenchuk'
__all__ = [
    'PlaceNotFoundTestCase', 'PlaceFoundTestCase', 'MultiPlacesFoundTestCase',
    'PlaceNotFoundMeta', 'PlaceFoundMeta', 'MultiplePlacesFoundMeta',
]


class PlacesMeta(type):
    """
    Основная сложность тестов, содержащихся тут состоит в data_provider-е
    Точнее в том, что после декорирования тест-метод поменять уже нельзя
    т.к. данные/фикстуры уже внутри тест.метода.

    Вариант с отложенной загрузкой фикстур на практие приводит к необходимости
    создания реестра фикстур с возможностью внешнего управления каждой из
    записей оного реестра, что чрезмерно усложнило бы код FixtureManager-а
    и увеличило время на разработку и отладку.

    Исходя из этого было решено пойти другим путём - декорированием
    экземпляров тест-класов "на лету". Тут на помощь пришли мета-классы
    (документацию к основному из них Вы какраз сейчас читаете).

    Побочным эффектом такого решения оказалось отсутствие "тела" в
    классах-потомках :))
    """

    @abstractclassmethod
    def _get_fixture_manager(cls):
        """
        :return FixtureManager:
        """
        pass

    @abstractclassmethod
    def _get_decorator_to_method(cls, method_name):
        """
        Возвращает data_provider-декоратор для указанного метода

        :param str method_name: имя метода, которое нужно декорировать
        :return callable:
        """
        pass

    @classmethod
    def _get_test_methods(mcs, item):
        """
        Возвращает filter-список всех тест-методов указанного класса

        :param TestCase item:
        :return filter:
        """
        return filter(lambda x: x.startswith('test_'), dir(item))

    @classmethod
    def _update_test_methods(mcs, item):
        """
        Декорирует data_provider-ом тест-методы указанного класса

        :param TestCase item:
        """
        for method in mcs._get_test_methods(item):
            old_method = getattr(item, method)
            decorator = mcs._get_decorator_to_method(method)
            setattr(item, method, decorator(old_method))

    def __new__(mcs, name, bases, attrs):
        super_new = super(PlacesMeta, mcs).__new__
        module = attrs.pop('__module__')
        new_class = super_new(mcs, name, bases, {'__module__': module})

        mcs._update_test_methods(new_class)

        return new_class


class PlaceNotFoundMeta(PlacesMeta):
    @classmethod
    def _get_decorator_to_method(mcs, method_name):
        fx_man = mcs._get_fixture_manager()
        decorators = {
            'test_place_without_required_data_return_status_400': data_provider(fx_man['invalid_place']),
            'test_place_without_required_data_return_error_description': data_provider(fx_man['invalid_place']),
            'test_server_should_return_status_404': data_provider(fx_man['no_place']),
        }

        return decorators[method_name]


class PlaceFoundMeta(PlacesMeta):
    @classmethod
    def _get_decorator_to_method(mcs, method_name):
        fx_man = mcs._get_fixture_manager()
        return data_provider(fx_man['single_place'])


class MultiplePlacesFoundMeta(PlacesMeta):
    @classmethod
    def _get_decorator_to_method(mcs, method_name):
        fx_man = mcs._get_fixture_manager()
        return data_provider(fx_man['multiple_places'])


class _PlacesMixin(object):
    @abstractmethod
    def _get_url(self):
        """
        Возвращает URL по которому нужно получить список сущностей

        :return str:
        """
        return ''


class PlaceNotFoundTestCase(TestCase, _PlacesMixin):
    def test_place_without_required_data_return_status_400(self, data):
        """
            Попытка получить список мест без необходимых параметров
            приводит к 400-й ошибке
        """
        response = self.client.get(self._get_url(), data)
        self.assertEqual(response.status_code, 400)

    def test_place_without_required_data_return_error_description(self, data):
        """
            При ошибке в запросе (400-й код) в "теле" ответа содержатся
            объяснения
        """
        response = self.client.get(self._get_url(), data)
        self.assertTrue(response.content)

    def test_server_should_return_status_404(self, data):
        """
        Если запрос валидный,но по нему ничего не найдено - в ответе должен быть код 404
        """
        response = self.client.get(self._get_url(), data)

        self.assertEqual(response.status_code, 404)


class PlaceFoundTestCase(TestCase, _PlacesMixin):
    def test_server_should_return_status_200(self, data):
        """
        Статус - 200 OK
        """
        response = self.client.get(self._get_url(), data)

        self.assertEqual(response.status_code, 200)

    def test_answer_should_be_json_encoded(self, data):
        """
        Ответ должен быть в json-представлении
        """
        response = self.client.get(self._get_url(), data)

        self.assertIn('application/json', response['Content-Type'])

    def test_answer_should_contain_non_empty_body(self, data):
        """
        Ответ должен содержать не пустое "тело"
        """
        response = self.client.get(self._get_url(), data)

        self.assertTrue(response.content)

    def test_answers_should_contain_place_code(self, data):
        """
        Ответ должен содержать код места
        """
        response = self.client.get(self._get_url(), data)
        places = json.loads(response.content.decode('utf-8'))

        self.assertIn('code', places[0])
        self.assertTrue(places[0]['code'])

    def test_answers_should_contain_place_name(self, data):
        """
        Ответ должен содержать название места
        """
        response = self.client.get(self._get_url(), data)
        places = json.loads(response.content.decode('utf-8'))

        self.assertIn('name', places[0])
        self.assertTrue(places[0]['name'])


class MultiPlacesFoundTestCase(TestCase, _PlacesMixin):
    def _get_places(self, data):
        """
        Осуществляет запрос и возвращает json-декодированный ответ

        :param dict data: параметры запроса
        :return list: список мест
        """
        response = self.client.get(self._get_url(), data)
        return json.loads(response.content.decode('utf-8'))

    def test_place_code_should_be_in_each_answer_item(self, data):
        """
        Код места должен быть в каждой записи ответа
        """
        for place in self._get_places(data):
            self.assertIn('code', place)
            self.assertTrue(place['code'])

    def test_place_name_should_be_in_each_answer_item(self, data):
        """
        Название места должно быть в каждой записи ответа
        """
        for place in self._get_places(data):
            self.assertIn('name', place)
            self.assertTrue(place['name'])
