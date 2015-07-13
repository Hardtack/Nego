Nego
====

Content negotiation utilities for every web framework.


HTTP Media Type
---------------

`Nego` Provides abstracted HTTP media type.


Main Type & Sub Type
~~~~~~~~~~~~~~~~~~~~

``MediaType`` class parses raw media type string and split it into main/sub
type.

    >>> from nego import MediaType
    >>> MediaType('text/html')
    nego.MediaType('text/html')
    >>> MediaType('text/html').main_type
    'text'
    >>> MediaType('text/html').sub_type
    'html'
    >>> MediaType('application', 'json')
    nego.MediaType('application/json')


Parameters
~~~~~~~~~~

``MediaType`` class also parses parameters.

    >>> MediaType('application/json; charset=utf-8')
    nego.MediaType('application/json; charset=utf-8')
    >>> MediaType('application/json; charset=utf-8').params
    {'charset': 'utf-8'}
    >>> MediaType('application', 'json', dict(charset='utf-8'))
    nego.MediaType('application/json; charset=utf-8')
    >>> MediaType('text/html; q=0.8').quality
    0.8


Wildcard & Matching
~~~~~~~~~~~~~~~~~~~

You can use wildcard for media type.

    >>> MediaType('text/html') in MediaType('text/*')
    True
    >>> MediaType('text/*') in MediaType('text/html')
    False
    >>> MediaType('text/html') in MediaType('text/html')
    True
    >>> MediaType('text/html') in MediaType('application/*')
    False
    >>> MediaType('text/*') in MediaType('*/*')
    True


Content Negotiation
~~~~~~~~~~~~~~~~~~~

`Nego` provides content negotiation by function
`nego.media_type.choose_acceptable_media_type`.

    >>> from nego.media_type import choose_acceptable_media_type
    >>> jpeg_type = MediaType('image/jpeg')
    >>> png_type = MediaType('image/png')
    >>> html_type = MediaType('text/html; q=0.9')
    >>> json_type = MediaType('application/json; q=0.8')
    >>> choose_acceptable_media_type(
    ...     [png_type, jpeg_type],
    ...     [MediaType('text/html'), MediaType('application/*'),
    ...      MediaType('image/*')]
    ... )
    nego.MediaType('image/png')
    >>> choose_acceptable_media_type(
    ...     [json_type, html_type],
    ...     [MediaType('text/html'), MediaType('application/*')]
    ... )
    nego.MediaType('text/html; q=0.9')


Renderer
--------

`Renderer` renders a data into specific type of data. For example, you can make
a renderer that renders a data into json like ::

    import json

    from nego import Renderer

    class JSONRenderer(Renderer):
        __media_types__ = ['application/json']
        def render(self, data):
            return json.dumps(data)

And also plain text renderer like ::

    class TextRenderer(Renderer):
        __media_types__ = ['text/plain']
        def render(self, data):
            return str(data)

Content Negotiation
~~~~~~~~~~~~~~~~~~~

`Nego` also provides content negotiation using renderer by function
`nego.renderer.best_renderer`.


    >>> json_renderer = JSONRenderer()
    >>> text_renderer = TextRenderer())
    >>> renderers = [json_renderer, text_renderer]
    >>> accept = 'application/json;q=0.9, text/plain;q=0.7'
    >>> acceptable_types = acceptable_media_types(accept)
    >>> renderer, media_type = best_renderer(acceptable_types, renderers)
    >>> renderer
    json_renderer
    >>> media_type
    nego.MediaType('application/json')
    >>> renderer.render(dict(foo='bar'))
    '{"foo": "bar"}'

Using with Web Frameworks
-------------------------

Tornado
~~~~~~~

You can use `Nego` with tornado by making mixin. ::

    class NegoMixin(object):
        renderers = [JSONRenderer(), TextRenderer()]

        def nego(self, obj):
            accept = self.request.headers.get('Accept', '*/*')
            acceptable_types = acceptable_media_types(accept)
            renderer, media_type = best_renderer(acceptable_types, renderers)
            body = renderer.render(obj)
            self.set_header('Content-Type', str(media_type))
            self.write(body)
