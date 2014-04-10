# -*- coding: utf-8 -*-

__all__ = ['S3BotoStorage', ]


from storages.backends.s3boto import S3BotoStorage as sb3s_orig
from storages.utils import setting


class S3BotoStorageBase(sb3s_orig):
    s3_url = setting('S3_URL', '')

    def _clean_name(self, name):
        norm_name = super(S3BotoStorageBase, self)._clean_name(name)

        if self.s3_url:
            return norm_name.replace(self.s3_url.replace('//', '/'), self.s3_url)

        return norm_name

    def _normalize_name(self, name):
        return super(S3BotoStorageBase, self)._normalize_name(name.replace(self.s3_url, ''))

    def __init__(self, acl=None, bucket=None, **settings):
        super(S3BotoStorageBase, self).__init__(acl, bucket, **settings)

        if self.s3_url and self.bucket_name:
            self.s3_url = '/'.join((self.s3_url, self.bucket_name))

S3BotoStorage = lambda: S3BotoStorageBase()
