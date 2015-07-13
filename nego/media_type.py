"""
nego.media_type
===============

HTTP media type

"""


def parse_header(s: str) -> tuple:
    """Parses parameter header
    """
    params = _parse_header_params(';'+s)
    key = params.pop(0).lower()
    pdict = {}
    for param in params:
        i = param.find('=')
        if i >= 0:
            name = param[:i].strip().lower()
            value = param[i+1:].strip()
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
                value = value.replace(r'\\', '\\').replace(r'\"', '"')
            pdict[name] = value
    return key, pdict


def _parse_header_params(s):
    li = []
    while s[:1] == ';':
        s = s[1:]
        end = s.find(';')
        while end > 0 and s.count('"', 0, end) % 2:
            # For quote
            end = s.find(';', end+1)
        end = end if end >= 0 else len(s)
        li.append(s[:end].strip())
        s = s[end:]
    return li


class MediaType(object):
    """Abstracted media type class."""
    def __init__(self, raw_or_main_type, sub_type=None, params: dict=None):
        if sub_type is None:
            raw = raw_or_main_type
            self.raw = raw
            media_type, self.params = parse_header(raw)
            if params:
                self.params.update(params)
            self.main_type, sep, self.sub_type = media_type.partition('/')
        else:
            main_type = raw_or_main_type
            self.main_type = main_type
            self.sub_type = sub_type
            self.params = (params or {}).copy()

    @property
    def has_wildcard_main_type(self) -> bool:
        return self.main_type == '*'

    @property
    def has_wildcard_sub_type(self) -> bool:
        return self.sub_type == '*'

    @property
    def has_wildcard_type(self) -> bool:
        return self.has_wildcard_main_type or self.has_wildcard_sub_type

    @property
    def is_wildcard_type(self) -> bool:
        return self.has_wildcard_main_type and self.has_wildcard_sub_type

    @property
    def type(self):
        return self.main_type, self.sub_type

    def __contains__(self, other):
        for k, v in self.params.items():
            if k != 'q' and other.params.get(k, None) != v:
                return False
        if self.main_type == '*' and self.sub_type == '*':
            return True
        if self.sub_type == '*' and self.main_type == other.main_type:
            return True
        if self.main_type == '*' and self.sub_type == other.sub_type:
            return True
        return self.type == other.type

    def __eq__(self, other):
        if isinstance(other, str):
            return self == MediaType(other)
        elif isinstance(other, MediaType):
            return self.type == other.type and self.quality == other.quality
        else:
            return False

    def __repr__(self):
        return 'nego.MediaType({0!r})'.format(str(self))

    def __str__(self):
        return '; '.join(['%s/%s' % (self.main_type, self.sub_type)] +
                         ['%s=%s' % (k, v)
                          for k, v in self.params.items()])

    @property
    def quality(self) -> float:
        q = self.params.get('q', None)
        if q is None:
            return 1.0
        return float(q)


def acceptable_media_types(accept_field: str):
    """Extract acceptable media types from request"""
    accept_field = '' if accept_field is None else accept_field
    li = [x.strip() for x in accept_field.split(',')] or ['*/*']
    acceptable_types = [MediaType(x) for x in li]
    return sorted(
        acceptable_types,
        key=lambda x: (x.quality,
                       len(acceptable_types) - acceptable_types.index(x)),
        reverse=True,
    )


def choose_acceptable_media_type(acceptable_types, supported_types) -> MediaType:
    """Choose best acceptable media type for acceptable media types.
    :param acceptable_types: collection of media type acceptable
    :param supported_types: collection of media type supported

    :returns: best acceptable media type or :const:`None` if cannot handle.

    """
    # Reorder accept
    acceptable_types = sorted(
        acceptable_types,
        key=lambda x: (x.quality,
                       len(acceptable_types) - acceptable_types.index(x)),
        reverse=True,
    )
    for acceptable in acceptable_types:
        for supported in supported_types:
            if acceptable in supported:
                return acceptable
    return None


def can_accept(acceptable_types, supported_types) -> bool:
    """Determines acceptablility.
    :param acceptable_types: collection of media type acceptable
    :param supported_types: collection of media type supported

    """
    return (
        choose_acceptable_media_type(acceptable_types, supported_types) is not
        None
    )
