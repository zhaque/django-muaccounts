from django import template
register = template.Library()

import muaccounts.themes

@register.tag
def theme ( parser, token ): 
    try:
        tag_name, codename = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents[0]
    return ThemeValueNode( codename )

class ThemeValueNode ( template.Node ): 
    def __init__ ( self, codename ): 
        self.codename = codename

    def render ( self, context ): 
        return muaccounts.themes.get_value(
            self.codename,
            context['request'].muaccount.theme[self.codename])
