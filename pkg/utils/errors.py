# -*- coding: utf-8 -*-

NO_ERROR = 0
ERROR_UNKNOWN = -1
ERROR_INVALID_REQUEST_FORMAT = 0x00001
ERROR_INVALID_REQUEST_ACTION = 0x00002
ERROR_INVALID_REQUEST_BODY = 0x00003
ERROR_SAVE_DATA = 0x00008
ERROR_ATTACHMENT_SIZE_QUOTA_EXCEED_STANDART = 0x00009
ERROR_ATTACHMENT_SIZE_QUOTA_EXCEED_PREMIUM = 0x00010
ERROR_NOTE_SIZE_QUOTA_EXCEED = 0x00011
ERROR_TOTAL_SIZE_QUOTA_EXCEED = 0x00012

ERROR_NOT_WELL_FORMED = -1
ERROR_ACTION_PARAM_IS_MISSED = -2
ERROR_UNRECOGNIZED_ACTION = -3
ERROR_USER_ALREADY_EXISTS = -4
ERROR_STORAGE_ENGINE_RETURNS_ERROR = -5
ERROR_AUTH_FAILED = -6
ERROR_USER_NOT_EXISTS = -7
ERROR_INTERNAL_DATA_JSON_MALFORMED = -8
ERROR_WRONG_ARGUMENTS_COUNT = -9
ERROR_INTERNAL_SERVER_ERROR = -10
ERROR_INTERNAL_FILE_SYSTEM_ERROR = -11
ERROR_INTERNAL_SENDMAIL_ERROR = -12
ERROR_TOO_MUCH_REQUESTS = -13
ERROR_ACCESS_DENIED = -14
ERROR_MAX_EMAILS_LIMIT_REACHED = -15
ERROR_DATA_TOO_LARGE = -16
ERROR_ALREADY_LOCKED = -17
ERROR_EXTERNAL_DATA_MALFORMED = -18
ERROR_NOT_FOUND = -19
ERROR_COUNT_ITEMS_QUOTA_EXCEED = -20
ERROR_ITEM_ALREADY_EXISTS = -21
ERROR_UPLOADCARE_ERROR = -22
ERROR_UNDEFINED_ERROR = -1000


def get_error_message(error_code):
    error_messages = {
        NO_ERROR: '',
        ERROR_INVALID_REQUEST_FORMAT: 'Invalid request format',
        ERROR_INVALID_REQUEST_ACTION: 'Invalid request action',
        ERROR_INVALID_REQUEST_BODY: 'Invalid request body',
        ERROR_SAVE_DATA: 'Can\'t save data',
        ERROR_UNKNOWN: 'Unknown error',
        ERROR_ATTACHMENT_SIZE_QUOTA_EXCEED_STANDART: 'You will not be able to upload the file, as its size exceeds {:.1S}. '
                                                    'You can switch to Project Pro to be able to upload files up to {:.1S}.',
        ERROR_ATTACHMENT_SIZE_QUOTA_EXCEED_PREMIUM: 'Unfortunately, the file size exceeds {:.1S}.'
                                          'Unfortunately, the size of the note exceeds {:.1S}.',
        ERROR_NOTE_SIZE_QUOTA_EXCEED:  'Unfortunately, the size of the note exceeds {:.1S}.'
                                       'If you would like to create notes of larger size, '
                                       'you have to upgrade your subscription to Project Pro',
        ERROR_TOTAL_SIZE_QUOTA_EXCEED: 'You have reached your monthly traffic limit. To continue, '
                                       'you have to purchase Project Pro.'
    }

    return error_messages[error_code] if error_code in error_messages else error_messages[ERROR_UNKNOWN]


class BaseError(Exception):
    def __init__(self, code, message=None, *args, **kwargs):
        super(BaseError, self).__init__(code, message, *args, **kwargs)
        self.code = code
        self.message = message if not message is None else get_error_message(code)


class ParseRequestError(BaseError):
    pass
