from django import forms
from django.conf import settings
from django.utils.html import escape

THEMES = getattr(settings, 'MUACCOUNTS_THEMES', ())

DEFAULT_THEME_DICT = dict( (i[0], i[2][0][0]) for i in THEMES )

THEMES_DICT = {}
for codename, name, choices in THEMES:
    choices_dict = {}
    for choice in choices:
        try: v = choice[2]
        except IndexError: v = choice[0]
        choices_dict[choice[0]] = (choice[1], v)
    THEMES_DICT[codename] = (name, choices_dict)

def normalize_choices(choices):
    return tuple( (choice[0],choice[1]) for choice in choices )

def get_value(section_codename, choice_codename):
    return THEMES_DICT[section_codename][1][choice_codename][1]

# forms stuff
class ThemeWidget(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        widgets = []
        for codename, name, choices in THEMES:
            widgets.append(forms.Select(choices=normalize_choices(choices)))
        super(ThemeWidget, self).__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        if value is None: value = {} 
        rv = []
        for codename, name, choices in THEMES:
            rv.append(value.get(codename, choices[0][0]))
        return rv

    def format_output(self, rendered_widgets):
        out = []
        ww = iter(rendered_widgets)
        for codename, name, choices in THEMES:
            out.append('<label>%s %s</label><br />' % (
                escape(name), ww.next() ) )
        return ''.join(out)

class ThemeField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = []
        for codename, name, choices in THEMES:
            fields.append(forms.CharField())

        widget = ThemeWidget()

        kwargs.setdefault('required',False)
        super(ThemeField, self).__init__(
            fields, widget=widget, *args, **kwargs)

    def compress(self, data):
        rv = {}
        di = iter(data)
        for codename, name, choices in THEMES:
            rv[codename] = di.next()
        return rv
