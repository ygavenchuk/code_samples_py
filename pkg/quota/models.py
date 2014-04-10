# -*- coding: utf-8 -*-

from django.db import models

from pkg.utils import errors
from pkg.utils.models import NNConfig
from pkg.notes.models import NotesNotes, NotesUsers, NotesAttachements
from pkg.utils.filetools import HumanizeSize as sizeformat
from pkg.notes.utils import build_notes_pk


class NotesQuota(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    usage = models.IntegerField(default=0, blank=True)

    class Meta:
        db_table = 'notes'


class UsersPremiumLimits(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(NotesUsers, to_field='id', db_column='user_id')
    note_max_size = models.IntegerField(db_column='NOTES_MAX_SIZE')
    total_max_size = models.IntegerField(db_column='NOTES_MONTH_USAGE_QUOTA')
    attachments_max_size = models.IntegerField(db_column='NOTES_MAX_ATTACHMENT_SIZE')

    class Meta:
        db_table = 'users_premium_limits'


class UsersPremium(models.Model):
    STATUS_UNPAYED = 'unpayed'
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_CANCELLED = 'cancelled'

    user = models.ForeignKey(NotesUsers, to_field='id', db_column='id', primary_key=True)

    status = models.CharField(
        choices=(
            (STATUS_UNPAYED, STATUS_UNPAYED, ),
            (STATUS_ACTIVE, STATUS_ACTIVE, ),
            (STATUS_EXPIRED, STATUS_EXPIRED, ),
            (STATUS_CANCELLED,  STATUS_CANCELLED, ),
        ),
        max_length=10
    )
    start_date = models.DateField()
    end_date = models.DateField()

    @property
    def is_premium(self):
        return self.status == self.STATUS_ACTIVE

    class Meta:
        db_table = 'users_premium'


class QuotaLimits(NNConfig):
    @property
    def note_max_size(self):
        """
        Max size of sigle note (text + all attachments). In bytes
        """
        return int(self.NOTES_MAX_SIZE)

    @note_max_size.setter
    def note_max_size(self, value):
        self._set_item('NOTES_MAX_SIZE', value)

    @property
    def total_max_size(self):
        """
        Total Max size of all notes + all attachments. In bytes
        """
        return int(self.NOTES_MONTH_USAGE_QUOTA)

    @total_max_size.setter
    def total_max_size(self, value):
        self._set_item('NOTES_MONTH_USAGE_QUOTA', int(value))

    @property
    def attachments_max_size(self):
        """
        Max size of attachment. In bytes
        """
        return int(self.NOTES_MAX_ATTACHMENT_SIZE)

    @attachments_max_size.setter
    def attachments_max_size(self, value):
        self._set_item('NOTES_MAX_ATTACHMENT_SIZE', int(value))


class UserLimits(object):
    """
    Wrapper for different limit classes of prepaid and free accounts
    """
    _limiter = None
    _user_id = None

    def _get_user_limits(self):
        if self._user_id:
            premium_user = UsersPremium.objects.filter(user_id=self._user_id, status=UsersPremium.STATUS_ACTIVE)
            premium_user_limits = UsersPremiumLimits.objects.filter(user_id=self._user_id)

            if premium_user.exists() and premium_user_limits.exists():
                return premium_user_limits.get()

        return QuotaLimits()

    def __init__(self, user_id=None):
        self._user_id = user_id
        self._limiter = self._get_user_limits()

    @property
    def note_max_size(self):
        """
        Max size of sigle note (text + all attachments). In bytes
        """
        return int(self._limiter.note_max_size)

    @property
    def total_max_size(self):
        """
        Total Max size of all notes + all attachments. In bytes
        """
        return int(self._limiter.total_max_size)

    @property
    def attachments_max_size(self):
        """
        Total Max size of all attachments of current note. In bytes
        """
        return int(self._limiter.attachments_max_size)


class QuotaLimitError(errors.BaseError):
    pass


class NoteQuotaLimitError(QuotaLimitError):
    def __init__(self, curr_size, max_size):
        error_code = errors.ERROR_NOTE_SIZE_QUOTA_EXCEED
        error_text = errors.get_error_message(error_code).format(
             sizeformat(max_size))

        self.error_text = error_text

        super(NoteQuotaLimitError, self).__init__(error_code, error_text)


class TotalQuotaLimitError(QuotaLimitError):
    def __init__(self, curr_size, max_size):
        error_code = errors.ERROR_TOTAL_SIZE_QUOTA_EXCEED
        error_text = errors.get_error_message(error_code)

        self.error_text = error_text

        super(TotalQuotaLimitError, self).__init__(error_code, error_text)


class AttachmentsQuotaLimitError(QuotaLimitError):
    def __init__(self, curr_size, max_size, is_pro=False):
        error_code = errors.ERROR_ATTACHMENT_SIZE_QUOTA_EXCEED_PREMIUM
        first_param = max_size
        second_param = max_size

        #если обычний пользователь
        if not is_pro:
            error_code = errors.ERROR_ATTACHMENT_SIZE_QUOTA_EXCEED_STANDART
            second_param = int(NNConfig().NOTES_MAX_ATTACHMENT_SIZE_PREMIUM_DEFAULT)

        error_text = errors.get_error_message(error_code).format(
                    sizeformat(first_param),
                    sizeformat(second_param))

        self.error_text = error_text

        super(AttachmentsQuotaLimitError, self).__init__(error_code, error_text)


class QuotaValidator(object):

    def __init__(self, instance, prev_size, new_size):
        self._instance = instance
        self._prev_size = prev_size or 0
        self._new_size = new_size or 0

    def _update_used(self, new_used_size):
        notes_quota = NotesQuota.objects.get_or_create(user_id=self._instance.user_id)[0]

        if new_used_size:
            notes_quota.usage += new_used_size
            notes_quota.save()

    def validate(self):
        quota_checker = CheckQuotaLimit(self._instance.user_id)
        data_provider = SignalSizeDataProvider(self._instance, self._prev_size, self._new_size)

        attachments_size = data_provider.attachments_size
        quota_checker.check_attachment_limit(attachments_size)

        total_size = data_provider.total_size
        quota_checker.check_total_limit(total_size)

        note_size = data_provider.note_size
        quota_checker.check_note_limit(note_size)

        self._update_used(total_size)


class CheckQuotaLimit(object):
    user_id = None

    def _get_limits(self):
        return UserLimits(user_id=self.user_id)

    def __init__(self, user_id):
        self.user_id = user_id

        self.limits = self._get_limits()
        self.notes_quota = NotesQuota.objects.get_or_create(user_id=self.user_id)[0]

    def check_total_limit(self, size):
        used_size = size + self.notes_quota.usage

        if used_size and used_size > self.limits.total_max_size:
            raise TotalQuotaLimitError(size, self.limits.total_max_size)

    def check_attachment_limit(self, size):
        if size and size > self.limits.attachments_max_size:
            is_premium = UsersPremium.objects.filter(
                user_id=self.user_id,
                status=UsersPremium.STATUS_ACTIVE
            ).exists()

            raise AttachmentsQuotaLimitError(size, self.limits.attachments_max_size, is_premium)

    def check_note_limit(self, size):
        if size > self.limits.note_max_size:
            raise NoteQuotaLimitError(size, self.limits.note_max_size)

# some code has been removed


class SignalSizeDataProvider(object):
    """
    It's dummy class
    """
    pass
