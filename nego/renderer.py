"""
nego.renderers
==============

HTTP Response Renderers

"""
import json
from abc import ABCMeta, abstractmethod, abstractproperty
from functools import wraps

from .media_type import MediaType


class Renderer(object, metaclass=ABCMeta):
    """Base renderer class."""

    @abstractproperty
    def __media_types__(self):
        """A collection of supporting media-type :class:`string`s.
        subclasses must redefine this value.

        """
        pass

    @property
    def media_types(self):
        """Collections of abstracted media-types.
        """
        return (MediaType(x) for x in self.__media_types__)

    def can_render(self, media_type):
        """Determines that renderer can render `media_type`.
        """
        return not self.choose_media_type(media_type) is None

    def choose_media_type(self, media_type: MediaType):
        """Chooses media type that will be used for rendering.
        """
        chosen_type = None
        for renderer_type in self.media_types:
            if media_type in renderer_type or renderer_type in media_type:
                chosen_type = renderer_type
        if chosen_type is None:
            return None
        elif chosen_type.has_wildcard_type:
            main_type = None
            sub_type = None
            if chosen_type.has_wildcard_main_type and \
                    not media_type.has_wildcard_main_type:
                main_type = media_type.main_type
            elif media_type.has_wildcard_main_type and \
                    not chosen_type.has_wildcard_main_type:
                main_type = chosen_type.main_type
            if chosen_type.has_wildcard_sub_type and \
                    not media_type.has_wildcard_sub_type:
                sub_type = media_type.sub_type
            elif media_type.has_wildcard_sub_type and \
                    not chosen_type.has_wildcard_sub_type:
                sub_type = chosen_type.sub_type
            if main_type is None or sub_type is None:
                # Cannot choose media type
                return None
            return MediaType(main_type, sub_type)
        else:
            return chosen_type

    @abstractmethod
    def render(self, data, state=None):
        """Renders `data`.

        :param data: data to be rendered
        :param state: state to be used for rendering

        """
        pass


class JSONRenderer(Renderer):
    """Renders object to json with JSONEncoder.
    """
    __media_types__ = ('application/json',)

    def __init__(self, encoder: json.JSONEncoder=json.JSONEncoder()):
        """Constructor

        :param encoder: encoder to be used with renderer.

        """
        super(JSONRenderer, self).__init__()
        self.encoder = encoder

    def render(self, data, state=None):
        return self.encoder.encode(data)


class FunctionRenderer(Renderer):
    """Renders object with a function.
    """
    __media_types__ = ()

    def __init__(self, fn, media_types):
        super(FunctionRenderer, self).__init__()
        self.fn = fn
        self.__media_types__ = tuple(str(x) for x in media_types)

    def render(self, data, state=None):
        return self.fn(data, state)

    def __call__(self, *args, **kwargs):
        return self.render(*args, **kwargs)


def renderer(*media_types):
    """Decorator that creates simple renderer with function.
    """
    def decorator(fn):
        renderer = wraps(fn)(FunctionRenderer(fn, media_types))
        return renderer
    return decorator


def best_renderer(acceptable_types, renderers) -> Renderer:
    """Choose best renderer and media type"""
    acceptable_types = sorted(
        acceptable_types,
        key=lambda x: (x.quality,
                       len(acceptable_types) - acceptable_types.index(x)),
        reverse=True,
    )
    for acceptable in acceptable_types:
        for renderer in renderers:
            if renderer.can_render(acceptable):
                return renderer, renderer.choose_media_type(acceptable)
    return None, None
