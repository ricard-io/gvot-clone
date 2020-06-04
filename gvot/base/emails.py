import re

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.template import Context, Template
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.http import urlencode

from wagtail.core.templatetags.wagtailcore_tags import richtext


def prepare_templated(request, template, context, embed=False):
    def autoescape(s):
        return "{{% autoescape off %}}{}{{% endautoescape %}}".format(s)

    def render_subject():
        subject = Template(autoescape(template.sujet)).render(Context(context))
        # Email subject *must not* contain newlines
        return ''.join(subject.splitlines())

    def render_message(html=False, insert_head=False):
        if html and insert_head:
            subject = render_subject()
            body = render_message(html=True, insert_head=False)
            return render_to_string(
                'emails/habillage.html', {'subject': subject, 'body': body},
            )
        elif html and not embed:
            # relative urls have to be absoluted
            html = re.sub(
                r'href=(.)/',
                r'href=\1{{ request.base_url }}/',
                richtext(template.html),
            )
            return Template(richtext(html)).render(Context(context))
        elif html and embed:
            # embedded preview
            return Template(richtext(template.html)).render(Context(context))
        else:
            return Template(autoescape(template.texte)).render(
                Context(context)
            )

    context.update(
        {
            'settings': {'assistance': settings.ASSISTANCE},
            'request': {
                'base_url': "{}://{}".format(
                    request.scheme, request.get_host()
                ),
            },
        }
    )

    subject = render_subject()
    message = render_message()
    try:
        html_message = render_message(html=True, insert_head=not embed)
    except TemplateDoesNotExist:  # also TemplateSyntaxError
        html_message = None

    return subject, message, html_message


def preview_templated(
    request, template, context, sender, recipients, **kwargs
):
    subject, message, html = prepare_templated(
        request, template, context, embed=True
    )
    return subject, message, html


def unsubscribe_link(recipients):
    return '<mailto:{}?{}>'.format(
        settings.ASSISTANCE,
        urlencode({'subject': 'unsubscribe {}'.format(recipients)}),
    )


def send_templated(request, template, context, sender, recipients, **kwargs):
    subject, message, html = prepare_templated(request, template, context)
    email_message = EmailMultiAlternatives(
        subject, message, sender, recipients, **kwargs
    )
    if html:
        email_message.attach_alternative(html, 'text/html')
    email_message.extra_headers['List-Unsubscribe'] = unsubscribe_link(
        recipients
    )
    email_message.send()


def send_mass_templated(request, template, sender, datas, **kwargs):
    mass_messages = []
    connection = get_connection()
    for context, recepts in datas:
        subject, message, html = prepare_templated(request, template, context)
        email_message = EmailMultiAlternatives(
            subject, message, sender, recepts, connection=connection, **kwargs
        )
        if html:
            email_message.attach_alternative(html, 'text/html')
        email_message.extra_headers['List-Unsubscribe'] = unsubscribe_link(
            recepts
        )
        mass_messages.append(email_message)
    return connection.send_messages(mass_messages)
