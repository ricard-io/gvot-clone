from django import forms

from tapeforms.contrib.bootstrap import BootstrapTapeformMixin


class BigLabelTapeformMixin(BootstrapTapeformMixin):
    def get_field_label_css_class(self, bound_field):
        if isinstance(bound_field.field.widget, forms.CheckboxInput):
            css_class = super().get_field_label_css_class(bound_field)
            return 'h3 ' + (css_class or "")  # avoid possible None
        return 'h3 mt-3'

    def get_field_container_css_class(self, bound_field):
        css_class = super().get_field_container_css_class(bound_field)
        if isinstance(bound_field.field.widget, forms.CheckboxInput):
            return 'mt-4 ' + (css_class or "")  # avoid possible None
        return css_class
