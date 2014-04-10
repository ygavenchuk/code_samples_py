# -*- coding: utf-8 -*-

__all__ = ['QuotaRouter', ]


class QuotaRouter(object):
    DB_NAME = u'xxxx'
    DB_MODELS = [u'NotesQuota', ]

    def db_for_read(self, model, **hints):
        return self.DB_NAME if unicode(getattr(model, '__name__', None)) in self.DB_MODELS else None

    def db_for_write(self, model, **hints):
        return self.DB_NAME if unicode(getattr(model, '__name__', None)) in self.DB_MODELS else None

    def allow_relation(self, obj1, obj2, **hints):
        return all((
            getattr(obj1, '__name__', None) in self.DB_MODELS,
            getattr(obj2, '__name__', None) in self.DB_MODELS,
        )) or None

    def allow_syncdb(self, db, model):
        return all((db == self.DB_NAME, getattr(model, '__name__', None) in self.DB_MODELS),) or None
