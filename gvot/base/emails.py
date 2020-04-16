import re

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string


def prepare_templated(request, base_tpl, context):
    def render_subject():
        template = "emails/{}.subject".format(base_tpl)
        subject = render_to_string(template, context)
        # Email subject *must not* contain newlines
        return ''.join(subject.splitlines())

    def render_message(html=False):
        if not html:
            template = "emails/{}.txt".format(base_tpl)
        else:
            template = "emails/{}.html".format(base_tpl)
        return render_to_string(template, context)

    context.update({
        'site': get_current_site(request),
        'settings': {'assistance': settings.ASSISTANCE},
        'request': {
            'base_url': "{}://{}".format(request.scheme, request.get_host()),
        },
    })

    subject = render_subject()
    message = render_message()
    try:
        html_message = render_message(html=True)
    except TemplateDoesNotExist:
        html_message = None

    return subject, message, html_message


def send_mass_templated(request, base_tpl, sender, datas, **kwargs):
    mass_messages = []
    connection = get_connection()
    for context, recepts in datas:
        subject, message, html = prepare_templated(request, base_tpl, context)
        email_message = EmailMultiAlternatives(
            subject, message, sender, recepts, connection=connection, **kwargs
        )
        if html:
            email_message.attach_alternative(html, 'text/html')
        mass_messages.append(email_message)
    return connection.send_messages(mass_messages)


def send_templated(request, base_tpl, context, sender, recipients, **kwargs):
    subject, message, html = prepare_templated(request, base_tpl, context)
    email_message = EmailMultiAlternatives(
        subject, message, sender, recipients, **kwargs
    )
    if html:
        email_message.attach_alternative(html, 'text/html')
    email_message.send()


def preview_templated(request, base_tpl, context, sender, recipients, **kwargs):
    subject, message, html = prepare_templated(request, base_tpl, context)
    if html:
        # Q&D body extraction
        html_parts = re.split(
            r'<\/?\s*body\b.*?>', html, maxsplit=2, flags=re.I | re.M | re.S
        )
        if len(html_parts) == 3:
            html = html_parts[1]
        else:
            html = """
            <div class="help-block help-critical">
            Erreur de prévisualisation HTML.<br>
            Vérifiez que votre template HTML est correct.
            </div>
            """
    return subject, message, html
