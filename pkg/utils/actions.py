# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.conf import settings
from django.dispatch.dispatcher import receiver

from ..notes.models import note_updated
from ..RedisSession import RSession
from .errors import *
import json


__all__ = [
    'update_cookie', 'update_session_expire', 'request_parser', 'response_builder', 'get_request_action',
    'BaseActions',
]


class BaseActions(object):
    def __init__(self, user_id):
        """
            :param int user_id: user's id
        """
        self.user_id = user_id


@receiver(note_updated)
def _update_time_changed(**kwargs):
    RSession.set_last_update('notes_last_update', kwargs['update_time'])


def request_parser(request, allowed_actions):
    """
    Parse request from client, define and return action type (action handler) and request's body params

    :param HttpRequest request: request params
    :param dict allowed_actions: dict with allowed actions in format 'action': callable_handler
    :return: {'action': handler, 'body': {}}
    :raise: ParseRequestError
    """

    if request.method != 'POST' or not request.is_ajax() or len(request.body) < 1:
        raise ParseRequestError(ERROR_INVALID_REQUEST_FORMAT)

    request_data = json.loads(request.body, request.encoding)

    if not isinstance(request_data, dict):
        raise ParseRequestError(ERROR_INVALID_REQUEST_FORMAT)

    if not 'action' in request_data:
        raise ParseRequestError(ERROR_INVALID_REQUEST_ACTION)

    if not request_data['action'] in allowed_actions:
        raise ParseRequestError(ERROR_INVALID_REQUEST_ACTION)

    if not 'body' in request_data or len(request_data['body']) < 1:
        raise ParseRequestError(ERROR_INVALID_REQUEST_BODY)

    action = allowed_actions[request_data['action']](request_data['body'])

    return {
        'action': action['handler'],
        'body': action['body'],
    }


def response_builder(request, parser=None):
    """

    :param HttpRequest request:  request params
    :param callable parser: request parser
    :return: dict
    """

    result = {"errorCode": NO_ERROR, "body": {}}
    user_id = request.user.pk

    if not callable(parser):
        result['errorCode'] = ERROR_INVALID_REQUEST_ACTION
        result['errorMessage'] = get_error_message(result['errorCode'])

        return result

    try:
        request_result = parser(request)
    except ParseRequestError as err:
        result['errorCode'] = err.code
        result['errorMessage'] = err.message

        return result

    action_handler = request_result['action']
    request_body = request_result['body']
    try:
        user_notes = action_handler(user_id, **request_body)
        if user_notes is not None:
            result["body"].update(user_notes)
    except BaseError as err:
        result['errorCode'] = err.code
        result['errorMessage'] = err.message

    return result


def get_request_action(allowed_actions, body):
    """
        Select request action from allowed list, execute it and return result

        :param dict allowed_actions: list of allowed actions. Keys are names of action, value - callable handler
        :param dict body: request body

        :return dict: {'handler: request_handler, 'body': args_of_handler}
    """

    current_action = set(allowed_actions.keys()).intersection(set(body.keys()))
    if len(current_action) != 1:
        raise ParseRequestError(ERROR_INVALID_REQUEST_ACTION)

    return allowed_actions[current_action.pop()]()

