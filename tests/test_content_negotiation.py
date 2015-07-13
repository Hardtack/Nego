import json
from json import JSONEncoder

import pytest

from nego.media_type import acceptable_media_types, MediaType
from nego.renderer import JSONRenderer, renderer, best_renderer, Renderer


class Dog(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "🐶[{}]".format(self.name)


class ConvertEncoder(JSONEncoder):
    """JSONEncoder with converter"""

    def default(self, obj):
        if isinstance(obj, (list, tuple)):
            return [self.default(x) for x in obj]
        elif isinstance(obj, dict):
            return {self.default(k): self.default(v) for k, v in obj.items()}
        elif isinstance(obj, Dog):
            dog = obj
            return {
                '__type__': 'Dog',
                'name': dog.name,
            }
        else:
            return super().default(obj)


@pytest.fixture
def json_renderer():
    return JSONRenderer(ConvertEncoder())


@pytest.fixture
def text_renderer():
    @renderer('text/plain')
    def render(obj, state):
        return str(obj)
    return render


def test_content_negotiation(json_renderer, text_renderer):
    renderers = [json_renderer, text_renderer]

    accept = 'application/json;q=0.9, text/plain;q=0.7'
    acceptable_types = acceptable_media_types(accept)
    renderer, media_type = best_renderer(acceptable_types, renderers)
    assert json_renderer == renderer
    assert MediaType('application/json').type == media_type.type

    accept = 'text/plain;q=0.7, application/json;q=0.9'
    acceptable_types = acceptable_media_types(accept)
    renderer, media_type = best_renderer(acceptable_types, renderers)
    assert json_renderer == renderer
    assert MediaType('application/json').type == media_type.type

    accept = 'text/plain;q=0.9, application/json;q=0.9'
    acceptable_types = acceptable_media_types(accept)
    renderer, media_type = best_renderer(acceptable_types, renderers)
    assert text_renderer == renderer
    assert MediaType('text/plain').type == media_type.type

    accept = 'text/*'
    acceptable_types = acceptable_media_types(accept)
    renderer, media_type = best_renderer(acceptable_types, renderers)
    assert text_renderer == renderer
    assert MediaType('text/plain').type == media_type.type

    accept = 'image/*'
    acceptable_types = acceptable_media_types(accept)
    renderer, media_type = best_renderer(acceptable_types, renderers)
    assert renderer is None
    assert media_type is None

    accept = '*/*'
    acceptable_types = acceptable_media_types(accept)
    renderer, media_type = best_renderer(acceptable_types, renderers)
    assert json_renderer == renderer
    assert MediaType('application/json').type == media_type.type


def test_render(json_renderer: Renderer, text_renderer: Renderer):
    dog = Dog('Happy')

    assert dict(
        __type__='Dog',
        name='Happy'
    ) == json.loads(json_renderer.render(dog))

    assert '🐶[Happy]' == text_renderer.render(dog)
