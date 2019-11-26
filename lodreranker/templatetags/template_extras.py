from django import template
from lodreranker.utils import chunks
import re

register = template.Library()

@register.filter
def keyvalue(dict, key):
    try:
        return dict.get(key,'')
    except (KeyError, TypeError):
        return ''

@register.filter
def paragraphs(value):
    output = ['<p>']
    max_periods_per_paragraph = 2
    periods_read = 0
    words_read = 0
    for word in value.split(' '):
        output.append(word)
        words_read+=1
        if (word[-1:]=='.'):
            if (words_read >= 15):
                periods_read +=1
                words_read = 0
                if (periods_read % max_periods_per_paragraph == 0):
                    output.append('</p><p>')
    
    output.append('</p>')
    return ' '.join(output)

@register.filter
def extract(value):
    return f"{value.split('</p>')[0]}</p>"


@register.filter
def percent(value):
    if value<1:
        return f'{round(value*100,2)}%'
    else:
        return value

