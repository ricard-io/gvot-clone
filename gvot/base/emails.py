from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.template import Context, Template
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string


def prepare_templated(request, template, context, insert_head=False):
    def render_subject():
        subject = Template(template.sujet).render(Context(context))
        # Email subject *must not* contain newlines
        return ''.join(subject.splitlines())

    def render_message(html=False, insert_head=False):
        if html and insert_head:
            subject = render_subject()
            body = render_message(html=True, insert_head=False)
            return render_to_string(
                'emails/habillage.html', {'subject': subject, 'body': body},
            )
        elif html:
            return Template(template.html).render(Context(context))
        else:
            return Template(template.texte).render(Context(context))

    context.update(
        {
            'site': get_current_site(request),
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
        html_message = render_message(html=True, insert_head=insert_head)
    except TemplateDoesNotExist:  # also TemplateSyntaxError
        html_message = None

    return subject, message, html_message


def preview_templated(
    request, template, context, sender, recipients, **kwargs
):
    subject, message, html = prepare_templated(request, template, context)
    return subject, message, html


def send_templated(request, template, context, sender, recipients, **kwargs):
    subject, message, html = prepare_templated(request, template, context)
    email_message = EmailMultiAlternatives(
        subject, message, sender, recipients, **kwargs
    )
    if html:
        email_message.attach_alternative(html, 'text/html')
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
        mass_messages.append(email_message)
    return connection.send_messages(mass_messages)
