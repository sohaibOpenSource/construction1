# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
from genshi.template.eval import LookupBase

import html
import pytz
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
try:
    from genshi.core import Markup
except ImportError:
    logger.debug('Cannot import py3o.template')

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, html2plaintext
from odoo import models, fields
from odoo.tools.misc import formatLang, format_date

def format_user_tz(self):
    lang = self._context.get("lang")
    record_lang = self.env["res.lang"].with_context({'not_recursion': True}).search([("code", "=", lang)], limit=1)
    if record_lang:
        datetime_format = "%s %s" % (record_lang.date_format, record_lang.time_format)
        date_format = record_lang.date_format
    else:
        datetime_format = DEFAULT_SERVER_DATETIME_FORMAT
        date_format = DEFAULT_SERVER_DATE_FORMAT
    user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
    return datetime_format, date_format, user_tz

def format_multiline_value(value):
    # http://docs.oasis-open.org/office/v1.2/OpenDocument-v1.2-part1.html
    # http://www.datypic.com/sc/odf/t-text_boolean.html
    if value:
        return Markup(html.escape(value).replace('\n', '<text:line-break/>').
                      replace('\t', '<text:s/><text:s/><text:s/><text:s/>'))
    return ""

@classmethod
def genshi_lookup_attr(cls, obj, key):
    __traceback_hide__ = True
    try:
        val = getattr(obj, key)
    except AttributeError:
        if hasattr(obj.__class__, key):
            raise
        else:
            try:
                if type(obj) == dict:
                    val = obj[key]
                else:
                    if key.split('bf_label_')[1:]:
                        key, = key.split('bf_label_')[1:]
                        model_fields = obj.fields_get()
                        val = obj[key]
                        for field_name, field in model_fields.items():
                            if field_name == key:
                                val = ''
                                if 'string' in field:
                                    val = field.get('string')
                    else:
                        key = key.split('bf_')[1]
                        model_fields = obj.fields_get()
                        datetime_format, date_format, user_tz = format_user_tz(obj)
                        val = obj[key]
                        for field_name, field in model_fields.items():
                            if field_name == key:
                                if field.get('type') in ['selection', 'date', 'datetime', 'text', 'html', 'monetary', 'boolean', 'many2many', 'float', 'char']:
                                    field_val = val = getattr(obj, key)
                                    if field.get('type') == 'selection':
                                        if field_val:
                                            val = dict(obj._fields[field_name]._description_selection(obj.env)).get(field_val)
                                        else:
                                            val = ''
                                    elif field.get('type') == 'date':
                                        if field_val:
                                            val = format_date(obj.env, field_val)
                                        else:
                                            val = ''
                                    elif field.get('type') == 'datetime':
                                        def format_datetime(dt_attendance):
                                            if dt_attendance:
                                                return fields.Datetime.from_string(dt_attendance).replace(
                                                    tzinfo=pytz.utc
                                                ).astimezone(user_tz).strftime(datetime_format)
                                            else:
                                                return ''
                                        val = format_datetime(field_val)
                                    elif field.get('type') == 'text':
                                        val = format_multiline_value(field_val)
                                    elif field.get('type') == 'html':
                                        val = html2plaintext(field_val).strip()
                                    elif field.get('type') == 'monetary':
                                        val = formatLang(obj.env, field_val, currency_obj=obj.currency_id)
                                    elif field.get('type') == 'boolean':
                                        # Ref. https://www.htmlsymbols.xyz/miscellaneous-symbols/ballot-box-symbols
                                        if field_val:
                                            # https://www.htmlsymbols.xyz/unicode/U+2611
                                            # val = u"☑"
                                            val = "\u2611"
                                        else:
                                            # https://www.htmlsymbols.xyz/unicode/U+2610
                                            # val = u"☐"
                                            val = "\u2610"
                                    elif field.get('type') == 'many2many':
                                        val = ", ".join([i.display_name for i in field_val])
                                    elif field.get('type') == 'float':
                                        val = field_val
                                        if 'digits' in field:
                                            if field.get('digits'):
                                                precision, scale = field.get('digits')
                                                # val = formatLang(obj.env, field_val, dp='Product Price')
                                                # float_repr
                                                val = formatLang(obj.env, field_val, digits=scale)
                                        else:
                                            val = formatLang(obj.env, field_val, digits=2)
                                    elif field.get('type') == 'char':
                                        if field_val:
                                            val = field_val
                                        else:
                                            val = ''

            except (KeyError, TypeError, IndexError):
                val = cls.undefined(key, owner=obj)
    return val

setattr(LookupBase, 'lookup_attr', genshi_lookup_attr)
del genshi_lookup_attr
del LookupBase
