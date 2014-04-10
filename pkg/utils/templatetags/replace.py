# -*- coding: utf-8 -*-


import re

from django import template


register = template.Library()


@register.filter
def replace(string, args):
    search = unicode(args.split(args[0])[1])
    replace = unicode(args.split(args[0])[2])

    return re.sub(search, replace, unicode(string))
