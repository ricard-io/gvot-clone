from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail.message import EmailMultiAlternatives
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import render_to_string


def send_templated(request, base_tpl, context, sender, recipients, **kwargs):
    def render_subject():
        template = "emails/{}.subject".format(base_tpl)
        subject = render_to_string(template, context, request=request)
        # Email subject *must not* contain newlines
        return ''.join(subject.splitlines())

    def render_message(html=False):
        if not html:
            template = "emails/{}.txt".format(base_tpl)
        else:
            template = "emails/{}.html".format(base_tpl)
        return render_to_string(template, context, request=request)

    context.update({
        'site': get_current_site(request),
        'settings': {'assistance': settings.ASSISTANCE},
    })

    subject = render_subject()
    message = render_message()

    email_message = EmailMultiAlternatives(
        subject, message, sender, recipients, **kwargs
    )
    try:
        html_message = render_message(html=True)
        email_message.attach_alternative(html_message, 'text/html')
    except TemplateDoesNotExist:
        pass

    email_message.send()
