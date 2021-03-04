from django import forms

from tapeforms.contrib.bootstrap import BootstrapTapeformMixin


class FixBootstrapTapeformMixin(BootstrapTapeformMixin):
    """
    Avoid having multiple class attributes in html.
    """

    def get_widget_css_class(self, field_name, field):
        if field.widget.__class__ in [
            forms.RadioSelect,
            forms.CheckboxSelectMultiple,
            forms.CheckboxInput,
        ]:
            return None
        else:
            return self.widget_css_class or None


class BigLabelTapeformMixin(FixBootstrapTapeformMixin):
    def get_field_label_css_class(self, bound_field):
        if isinstance(bound_field.field.widget, forms.CheckboxInput):
            css_class = super().get_field_label_css_class(bound_field)
            return 'h3 ' + (css_class or "")  # avoid possible None
        return 'h3 mt-3'

    def get_field_container_css_class(self, bound_field):
        css_class = super().get_field_container_css_class(bound_field)
        if isinstance(bound_field.field.widget, forms.CheckboxInput):
            return 'pl-0 mt-4 ' + (css_class or "")  # avoid possible None
        return css_class
