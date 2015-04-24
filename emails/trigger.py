from django.template.loader import render_to_string

from blockexplorer.settings import POSTMARK_SENDER, EMAIL_DEV_PREFIX, BASE_URL, ADMINS

from utils import split_email_header, cat_email_header, simple_pw_generator

from postmark import PMMail

import re


def postmark_send(subject, html_body, to_info, from_info, cc_info=None,
        replyto_info=None, bcc_info=None):
    " Send email via postmark "
    pm = PMMail(
            sender=from_info,
            to=to_info,
            subject=subject,
            html_body=html_body,
            cc=cc_info,
            bcc=bcc_info,
            reply_to=replyto_info,
            )
    return pm.send()


def test_mail_merge(body_template, context_dict):
    """
    Weak test to verify template fields are all in context_dict.

    Used in cases where we don't want a mail merge failing siltently.
    """
    template_content = open('templates/emails/'+body_template, 'r').read()
    variables = re.findall(r'{{(.*?)}}', template_content)
    # Trim whitespace and only take entries to the left of the first period (if applicable):
    variables = set([x.strip().split('.')[0] for x in variables])
    # Remove variable in all templates:
    variables.remove('BASE_URL')
    for variable in variables:
        if variable not in context_dict:
            raise Exception('Missing variable `%s` in `%s`' % (variable, body_template))


# TODO: create non-blocking queue system and move email sending to queue
def send_and_log(subject, body_template, to_user=None, to_email=None,
        to_name=None, body_context={}, from_name=None, from_email=None,
        cc_name=None, cc_email=None, replyto_name=None, replyto_email=None,
        fkey_objs={}):
    """
    Send and log an email
    """

    # TODO: find a better way to handle the circular dependency
    from emails.models import SentEmail

    assert subject
    assert body_template
    assert to_email or to_user

    if to_user:
        to_email = to_user.email
        to_name = to_user.get_full_name()

    if not from_email:
        from_name, from_email = split_email_header(POSTMARK_SENDER)

    body_context_modified = body_context.copy()
    body_context_modified['BASE_URL'] = BASE_URL

    unsub_code = simple_pw_generator(num_chars=10)
    verif_code = simple_pw_generator(num_chars=10)
    body_context_modified['unsub_code'] = unsub_code
    body_context_modified['verif_code'] = verif_code

    # Generate html body
    html_body = render_to_string('emails/'+body_template, body_context_modified)

    send_dict = {
            'html_body': html_body,
            'from_info': cat_email_header(from_name, from_email),
            'to_info': cat_email_header(to_name, to_email),
            'subject': subject,  # may be overwritten below
            }
    if cc_email:
        send_dict['cc_info'] = cat_email_header(cc_name, cc_email)
    if replyto_email:
        send_dict['replyto_info'] = cat_email_header(replyto_name, replyto_email)
    else:
        send_dict['replyto_info'] = 'BlockCypher <contact@blockcypher.com>'

    if EMAIL_DEV_PREFIX:
        send_dict['subject'] += ' [DEV]'
    else:
        # send_dict['bcc_info'] = ','.join([POSTMARK_SENDER, ])
        pass

    # Log everything
    se = SentEmail.objects.create(
            from_email=from_email,
            from_name=from_name,
            to_email=to_email,
            to_name=to_name,
            cc_name=cc_name,
            cc_email=cc_email,
            body_template=body_template,
            body_context=body_context,
            subject=subject,
            unsub_code=unsub_code,
            verif_code=verif_code,
            auth_user=fkey_objs.get('auth_user', to_user),
            address_subscription=fkey_objs.get('address_subscription'),
            transaction_event=fkey_objs.get('transaction_event'),
            address_forwarding=fkey_objs.get('address_forwarding'),
            )

    postmark_send(**send_dict)

    return se


def send_admin_email(subject, body_template, body_context):
    """
    Send an admin email and don't log it
    """
    body_context_modified = body_context.copy()
    body_context_modified['BASE_URL'] = BASE_URL

    # Generate html body
    html_body = render_to_string('emails/admin/'+body_template, body_context_modified)

    if EMAIL_DEV_PREFIX:
        subject += ' [DEV]'

    pm_dict = {
            'sender': POSTMARK_SENDER,
            'to': ','.join([x[1] for x in ADMINS]),
            'subject': subject,
            'html_body': html_body,
            }

    # Make email object
    pm = PMMail(**pm_dict)

    # Send email object (no logging)
    return pm.send()
