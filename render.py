import sys
import cgi
import urllib2
import functools
import jinja2
import json
import calendar
from datetime import datetime


def escape_result(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not kwargs.get('escape_result', True):
            del kwargs['escape_result']
            return f(*args, **kwargs)
        t = f(*args, **kwargs)
        if t is None:
            return None
        if not isinstance(t, (str, unicode)):
            return '**'
        return cgi.escape(t, quote=True)
    return wrapper


def _string_func(f):
    @escape_result
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (LookupError, AttributeError, TypeError, ValueError):
            return '--'
    return wrapper

_env = jinja2.Environment(extensions=[
    'jinja2.ext.autoescape', 'jinja2.ext.loopcontrols', 'jinja2.ext.do',
], loader=jinja2.FileSystemLoader('templates'))


def _filter(f):
    _env.filters[f.__name__] = f
    return f


def _global(f):
    _env.globals[f.__name__] = f
    return f


@_filter
def tojson(obj):
    def default(obj):
        if isinstance(obj, datetime):
            return long(1000 * calendar.timegm(obj.timetuple()))
        return obj
    return json.dumps(obj, default=default).replace(
        '<', '\\u003c').replace('>', '\\u003e').replace(
            '&', '\\u0026').replace("'", '\\u0027')


@_filter
def urlencode(text):
    return urllib2.quote(text.encode('utf8')).replace('/', '%2F')


@_filter
@_string_func
def strftime(dt, fmt='%Y-%m-%d %H:%M:%S'):
    if not dt:
        return ''
    return dt.strftime(fmt.encode('utf-8')).decode('utf-8')


@_global
def render_comp(component, **kwargs):
    return render('components/%s.html' % component, **kwargs)


@_global
def js(filename):
    return render_comp('jslib', file=filename)


@_global
def css(filename):
    return render_comp('csslib', file=filename)


@_global
def link(page, title, id=None):
    return render_comp('link', page=page, title=title, id=id)


@_global
def icon(ic, id=None):
    return render_comp('icon', icon=ic, id=id)


def render(filename, **kwargs):
    return _env.get_template(filename).render(render_template=render, **kwargs)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        r = render('%s.html' % p)
        print 'Renderring', p
        with open('gen/%s.html' % p, 'w') as f:
            f.write(r.encode('utf-8'))
