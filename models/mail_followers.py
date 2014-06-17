# -*- coding: utf-8 -*-
##############################################################################
#
#    Trey, Kilobytes de Soluciones
#    Copyright (C) 2014-Today Trey, Kilobytes de Soluciones (<http://www.trey.es>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields
from openerp import tools, SUPERUSER_ID
from openerp.tools.translate import _
from openerp.tools.mail import plaintext2html
from openerp.addons.base.ir.ir_mail_server import MailDeliveryException

import base64
import re
from urllib import urlencode
from urlparse import urljoin
import time
import logging
_logger = logging.getLogger(__name__)


class mail_notification(osv.Model):
    _inherit = 'mail.notification'

    def _notify_email(self, cr, uid, ids, message_id, force_send=False, user_signature=True, context=None):
        message = self.pool['mail.message'].browse(cr, SUPERUSER_ID, message_id, context=context)

        # compute partners
        email_pids = self.get_partners_to_email(cr, uid, ids, message, context=None)
        if not email_pids:
            return True

        # compute email body (signature, company data)
        body_html = message.body
        user_id = message.author_id and message.author_id.user_ids and message.author_id.user_ids[0] and message.author_id.user_ids[0].id or None
        if user_signature:
            signature_company = self.get_signature_footer(cr, uid, user_id, res_model=message.model, res_id=message.res_id, context=context)
            body_html = tools.append_content_to_html(body_html, signature_company, plaintext=False, container_tag='div')

        # compute email references
        references = message.parent_id.message_id if message.parent_id else False

        # Si hay una plantilla cargar esta plantilla de notificaciones
        #model_ids = self.pool['ir.model'].search(cr, SUPERUSER_ID, [('model', '=', 'mail.notification')])
        #template_ids = self.pool['email.template'].search(cr, SUPERUSER_ID, [('model_id', '=', model_ids[0])])
        #
        #if template_ids:
        #    template = self.pool['email.template'].generate_email_batch(cr, uid, template_ids[0], ids, context={'body': message.body}, fields=None)
        #    _logger.warn('Datos de la plantilla: %s' % template)	
        #    body_html = template[ids[0]].body

        body_html = u'''<div style="background:#f5f5f5;border-radius:5px;padding:10px 20px;font-family:Arial, Helvetica, sans-serif; overflow:hidden; display:block;">
            <img src="data:image/png;base64,%s" width="48" height="48" alt="%s" style="border-radius:3px;float:left;margin-right:10px;">
            <div style="margin-top:13px; font-size:15px;font-weight:bold;">Notificacion generada por <a href="http://erp.trey.es/web#id=%s&amp;view_type=form&amp;model=res.partner">%s</a></div>
            <div style="margin:5px 0; overflow:hidden; display:block; height:20px;"></div>
            <div style="clear:both;border-radius:5px;border:1px solid #ccc;background:#fff; padding:24px 16px; overflow:hidden; display:block;">
                <p style="font-size:25px;font-weight:bold;">{{{SUBJECT}}}</p>
                <p style="font-size:12px;">%s</p>
                <span style="font-size:12px;"><a href="http://erp.trey.es/web?db=trey#action=mail.action_mail_redirect&&message_id=%s">Añadir Comentario</a></span>
            </div>
            <div>
            <p style="float:left; font-weight:normal; font-size:12px; color:#999">Este mensaje fue enviado por Trey el %s</p>
            <p style="float:right;"><img src="data:image/png;base64,
iVBORw0KGgoAAAANSUhEUgAAADgAAAAaCAYAAADi4p8jAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz
AAAOJgAADiYBou8l/AAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAXNSURB
VFiF1Zh/bNxlHcdfn+d735bJWIcwMhxCNnV/zLh0o8Skpb0e7V11jN6B/DCR/4wKJpiI/MEfRrIY
o0GimOgMxj/YZCNcmL2beqzXLdc7ioxkxLBMMdvUMjco6YJsZOvau3s+/tG77z39rteZ2oX0nXyT
5/359Xw+z+87UVXqEBHp7b+3y4reD/rZYj6znWWOiEt6+lNHrNitAIK+9fGktLQwLlHRGz6uRK4W
zJVNljekN55qrxOL5oCba/S4QR6q66oR/0wpl57sjt+/ISLVVQBlUy1fOnvz8SNHnivX7e5MJD/l
Ifeo6Cq81udLufSk2+G2bdtaL5T9TSBfwLBRVU976h2b8i8dPZzLnXdtowOD6416bXVesXLx1YO/
P75QQZ2vv9OpIh2I/YyInIhY9C9NbDfO0ZXL3wWeNVLZaWEAwLOGaz85MdkdH+yYWsHZa6fMHz2R
XkBEBWsreSAosCc+mBRp+TVSG0QFQbBiaa20nIvGU98ujmT2NlLwfm7RZJ0Zo0TjqVdN5dxdhUKh
Ek64e+zU9epTBI2AYFVKi1miJ1E+alBZ44nX9Ylp8yxCDJBAVWEKZk/n6EBql4jJ0FghAGWn3Yaw
JxpP/aoh0mNACTjX6I5u67d9fb7Eyj4bQPaBvATykijPSE889fysn/UUedix/w/IfofvLeaH8gDR
gVQnymtOIkWQqGN7BmWV8b1Nhdy+073x5DdU5DeO/g/WmifGDg2d6P3yfeu0Uvmx27cYvWv0QLZQ
593bt19vZiLjwKpaka8XhzOd8xUZhtTvwVgsdo3126YaA6Vvjeaz7c0co4mUhkQKPF1doT8ay2aD
GY7F7l5rff9tYHVN9Eapa0unPvWUDcUrAj21zo+W8tl2dS7pnoHkTlF5NOhLuK04nPl3Xd/R8S3/
utUTfUHACCcLB7Inl+wUVeG3xXzmSbc4AOv7Sac4RGRHuDgAVX26Qdjc+6XUba7es7rboSKqD7j6
lTdM9FojrwSfNRsgdNH/P/CwP2ui2uS0rYg9EYvdvTZsJBH/lMvV2s8B43VeGNl/OJpIHQc2Aijy
IBD0qWoGZxcRAGdKXe0HYenuwfJo5+3Nju/PO21jrZywvv9e+EM46jqpysbLIon+zmFf7Ov7ijPL
Ohi00D31VbJUBZ6Zb9nVsmoivwJUbwyLjDEv4ExTxVQfAIgl7m0Hbg0MreyqN5dkiYoy3TRP0b+L
Eq9TY3UbYi5dMWhExsOiwitD49FEshSc2MJDwDNWbRKRmog3iwczfwvC1Btr1qwpv//hjFK7xxS5
bAQXA2PlbZVg0KVqTLmUHxpddEBhN0r9SuqIDgyuB6+x/7Qxe+As0XQ6XUV439Gt6+u7Z92iE6mh
4lVLQLWRn/4kFotds9h40175ZSC4zlDzPUS31lhZKtUXXfu5e1A57dKyF3k8Hn+wDUB27FjUfh07
sP+vgPM6ocP6bcPReHJL2LY7PnhrbyL1g57+5OZm8Q7ncucFso7o0aAlkisU9p917efuQWUfQkdg
jz4+IzPfjCZSkz2QBp78XwtzUV2h3/em5D7glpqoB5E3o4nUu8A4SAvoLUbMWgXxxJQWDCiyG9Wv
1lgw8KK6K2w6Z1am/ZmdKvwjZLMSWD/7gF0cxrLZjzTSshVlj5smsA7oAr2D2TeqzBsghJva/DzC
REj8wdnVLX8K284p8HAud/5iq90s6A9RCsAp4F+gRVSOznWVXfVPDUNXSqqUS08WRzIPK9IP8kvg
EPAu8CHwGvCcqj5mVGLTF/w3FoqVTqerqrI3JH7xWDo9E7YV9z+Z5YRoIvUL4DuBQHVrcSR72U+/
ZVlgLJ7qt0KexpI+VMxn+uezXbK36NVGdGBwfVVl2ghfE5EncParKj9t5rcsCrwzmbzOU/NPD5yH
2iwEfaE4kh1u5rss/nQyF+TTTVR/bpVLjyzoexXyWXpEZGXt+rqIMKEwCjxS6trSPTw8fGEh1/8C
SxA2RjLatAAAAAAASUVORK5CYII="/></p> 
        </div></div>''' % (
            message.author_avatar,
            message.author_id.name,
            message.author_id.id,
            message.author_id.display_name,
            message.body,
            message.id,
            time.strftime("%d/%m/%Y")  # message.date,
        )
        references = False

        # create email values
        mail_values = {
            'mail_message_id': message.id,
            'auto_delete': True,
            'body_html': body_html,
            'recipient_ids': [(4, id) for id in email_pids],
            'references': references,
        }
        email_notif_id = self.pool.get('mail.mail').create(cr, uid, mail_values, context=context)
        if force_send:
            self.pool.get('mail.mail').send(cr, uid, [email_notif_id], context=context)
        return True


class mail_mail(osv.Model):
    _inherit = 'mail.mail'

    def send(self, cr, uid, ids, auto_commit=False, raise_exception=False, context=None):
        """ Sends the selected emails immediately, ignoring their current
            state (mails that have already been sent should not be passed
            unless they should actually be re-sent).
            Emails successfully delivered are marked as 'sent', and those
            that fail to be deliver are marked as 'exception', and the
            corresponding error mail is output in the server logs.

            :param bool auto_commit: whether to force a commit of the mail status
                after sending each mail (meant only for scheduler processing);
                should never be True during normal transactions (default: False)
            :param bool raise_exception: whether to raise an exception if the
                email sending process has failed
            :return: True
        """
        if context is None:
            context = {}
        ir_mail_server = self.pool.get('ir.mail_server')
        for mail in self.browse(cr, SUPERUSER_ID, ids, context=context):
            try:
                # TDE note: remove me when model_id field is present on mail.message - done here to avoid doing it multiple times in the sub method
                if mail.model:
                    model_id = self.pool['ir.model'].search(cr, SUPERUSER_ID, [('model', '=', mail.model)], context=context)[0]
                    model = self.pool['ir.model'].browse(cr, SUPERUSER_ID, model_id, context=context)
                else:
                    model = None
                if model:
                    context['model_name'] = model.name
                # handle attachments
                attachments = []
                for attach in mail.attachment_ids:
                    attachments.append((attach.datas_fname, base64.b64decode(attach.datas)))
                # specific behavior to customize the send email for notified partners
                email_list = []
                if mail.email_to:
                    email_list.append(self.send_get_email_dict(cr, uid, mail, context=context))
                for partner in mail.recipient_ids:
                    email_list.append(self.send_get_email_dict(cr, uid, mail, partner=partner, context=context))
                # headers
                headers = {}
                bounce_alias = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.bounce.alias", context=context)
                catchall_domain = self.pool['ir.config_parameter'].get_param(cr, uid, "mail.catchall.domain", context=context)
                if bounce_alias and catchall_domain:
                    if mail.model and mail.res_id:
                        headers['Return-Path'] = '%s-%d-%s-%d@%s' % (bounce_alias, mail.id, mail.model, mail.res_id, catchall_domain)
                    else:
                        headers['Return-Path'] = '%s-%d@%s' % (bounce_alias, mail.id, catchall_domain)

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                for email in email_list:
                    msg = ir_mail_server.build_email(
                        email_from=mail.email_from,
                        email_to=email.get('email_to'),
                        subject=email.get('subject'),
                        body=email.get('body'),
                        body_alternative=email.get('body_alternative'),
                        email_cc=tools.email_split(mail.email_cc),
                        reply_to=mail.reply_to,
                        attachments=attachments,
                        message_id=mail.message_id,
                        references=mail.references,
                        object_id=mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
                        subtype='html',
                        subtype_alternative='plain',
                        headers=headers)
                    res = ir_mail_server.send_email(cr, uid, msg,
                                                    mail_server_id=mail.mail_server_id.id,
                                                    context=context)

                if res:
                    mail.write({'state': 'sent', 'message_id': res})
                    mail_sent = True
                else:
                    mail.write({'state': 'exception'})
                    mail_sent = False

                # /!\ can't use mail.state here, as mail.refresh() will cause an error
                # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                self._postprocess_sent_message(cr, uid, mail, context=context, mail_sent=mail_sent)
            except Exception as e:
                _logger.exception('failed sending mail.mail %s', mail.id)
                mail.write({'state': 'exception'})
                self._postprocess_sent_message(cr, uid, mail, context=context, mail_sent=False)
                if raise_exception:
                    if isinstance(e, AssertionError):
                        # get the args of the original error, wrap into a value and throw a MailDeliveryException
                        # that is an except_orm, with name and value as arguments
                        value = '. '.join(e.args)
                        raise MailDeliveryException(_("Mail Delivery Failed"), value)
                    raise

            if auto_commit is True:
                cr.commit()
        return True

    def send_get_email_dict(self, cr, uid, mail, partner=None, context=None):
        """Return a dictionary for specific email values, depending on a
        partner, or generic to the whole recipients given by mail.email_to.

            :param browse_record mail: mail.mail browse_record
            :param browse_record partner: specific recipient partner
        """
        subject = self.send_get_mail_subject(cr, uid, mail, partner=partner, context=context)
        link = self.__get_partner_access_link(cr, uid, mail, partner, context=context, only_url=True)
        #body = self.send_get_mail_body(cr, uid, mail, partner=partner, context=context)
        body = mail.body_html
        body = body.replace('{{{SUBJECT}}}', '<a href="%s">%s</a>' % (link, subject or ''))
        body_alternative = tools.html2plaintext(body)
        return {
            'body': body,
            'body_alternative': body_alternative,
            'subject': '[TREY] %s' % subject,
            'email_to': self.send_get_mail_to(cr, uid, mail, partner=partner, context=context),
        }

    def send_get_mail_body(self, cr, uid, mail, partner=None, context=None):
        """Return a specific ir_email body. The main purpose of this method
        is to be inherited to add custom content depending on some module."""
        body = mail.body_html

        # generate footer
        link = self.__get_partner_access_link(cr, uid, mail, partner, context=context)
        if link:
            body = tools.append_content_to_html(body, link, plaintext=False, container_tag='div')
        return body

    def __get_partner_access_link(self, cr, uid, mail, partner=None, context=None, only_url=False):
        """Generate URLs for links in mails: partner has access (is user):
        link to action_mail_redirect action that will redirect to doc or Inbox """
        if context is None:
            context = {}
        if partner and partner.user_ids:
            base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
            # the parameters to encode for the query and fragment part of url
            query = {'db': cr.dbname}
            fragment = {
                'login': partner.user_ids[0].login,
                'action': 'mail.action_mail_redirect',
            }
            if mail.notification:
                fragment['message_id'] = mail.mail_message_id.id
            elif mail.model and mail.res_id:
                fragment.update(model=mail.model, res_id=mail.res_id)

            url = urljoin(base_url, "/web?%s#%s" % (urlencode(query), urlencode(fragment)))
            if only_url:
                return url
            else:
                return _("""<span class='oe_mail_footer_access'><small>Ref. <a style='color:inherit' href="%s">%s %s</a></small></span>""") % (url, context.get('model_name', ''), mail.record_name)
        else:
            return None

