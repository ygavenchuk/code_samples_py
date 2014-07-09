# -*- coding: utf-8 -*-

__author__ = 'y.gavenchuk'


from os.path import join as path_join, abspath, dirname
from json import load as json_load
from copy import deepcopy
from inspect import stack as inspect_stack


__all__ = ['FixtureManager', ]


class FixtureManager(object):
    @staticmethod
    def _get_caller_filename():
        """
        Find and return filename of outer caller (external script)

        :return str:
        """
        for item in inspect_stack():
            if item and __file__ not in item:
                return item[1]

        return __file__

    def __init__(self):
        self.fixture_data = {}

    def load(self, fixture_data=None, fixture_file=None, file_ext='json', current_file=None):
        """
            Load fixtures from iterable (list, dict, tuple, ...) instance (fixture_data) or file

            :param fixture_data: iterable - iterable data container
            :param fixture_file: string - name of file, from where will be loaded data.
            :param file_ext: string - extension of file without(!) leading dot. If empty string or None - no
                            additional extensions used
            :param current_file: string - file, indicates from where need to search relative path of fixture_file

            :raise ImportError: - if fixture data source is undefined
        """
        if fixture_data is not None:
            self.fixture_data = fixture_data
        elif fixture_file is not None:
            if file_ext:
                fixture_file += '.' + file_ext
            with open(self.get_fixture_path(fixture_file, current_file), 'r') as fp:
                self.fixture_data = json_load(fp)
        else:
            raise ImportError('Undefined fixture data source')

    def get(self, fixture_name):
        """
            Get fixture data by it's name.

            :param fixture_name: string - name of fixture, which data need to return
            :return: Iterable - if fixture_name doesn't exists - will be returned an empty dict
        """
        result = self.fixture_data[fixture_name] if fixture_name in self.fixture_data else dict

        return deepcopy(result)

    def __getitem__(self, item):
        return self.get(item)

    @classmethod
    def get_fixture_path(cls, fixture_file, current_file=None):
        """
            Build and return absolute path to the fixture's file.

            :note: method doesn't check existence of file

            :param fixture_file: string - name of file, from where will be loaded data.
            :param current_file: string - file, indicates from where need to search relative path of fixture_file

            :return: string
        """

        if not current_file:
            current_file = cls._get_caller_filename()

        return path_join(abspath(dirname(current_file)), 'fixtures', fixture_file)
