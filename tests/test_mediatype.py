from nego.media_type import MediaType, can_accept, choose_acceptable_media_type


def map_list(func, *iterables):
    """Apply :func:`map` and convert to list."""
    return list(map(func, *iterables))


def test_media_type():
    application_json_type = MediaType('application/json')
    application_type = MediaType('application/*')
    assert application_json_type in application_type

    json_type = MediaType('*/json')
    assert application_json_type in json_type

    image_type = MediaType('image/*')
    assert application_json_type not in image_type

    assert application_json_type == MediaType('application/json')


def test_media_order():
    image_type = MediaType('image/jpeg')
    html_type = MediaType('text/html; q=0.9')
    json_type = MediaType('application/json; q=0.8')
    li = [html_type, json_type, image_type]
    assert [json_type, html_type, image_type] == \
        sorted(li, key=lambda x: x.quality)


def test_acceptablility():
    # Single
    media_types = map_list(MediaType, ['application/json'])
    acceptables = map_list(MediaType, ['application/json'])
    assert can_accept(acceptables, media_types)

    # Wildcard
    media_types = map_list(MediaType, ['*/*'])
    acceptables = map_list(MediaType, ['application/json'])
    assert can_accept(acceptables, media_types)

    # Partitial wildcard
    media_types = map_list(MediaType, ['text/*'])
    acceptables = map_list(MediaType, ['application/json'])
    assert not can_accept(acceptables, media_types)

    acceptables = map_list(MediaType, ['text/html'])
    assert can_accept(acceptables, media_types)

    # Multiple acceptables
    media_types = map_list(MediaType, ['text/html'])
    acceptables = map_list(MediaType, ['application/json', 'text/html'])
    assert can_accept(acceptables, media_types)

    media_types = map_list(MediaType, ['image/jpeg'])
    acceptables = map_list(MediaType, ['application/json', 'text/html'])
    assert not can_accept(acceptables, media_types)

    # Multiple media types
    media_types = map_list(MediaType, ['text/*', 'application/json'])
    acceptables = map_list(MediaType, ['application/json'])
    assert can_accept(acceptables, media_types)
    acceptables = map_list(MediaType, ['text/html'])
    assert can_accept(acceptables, media_types)

    acceptables = map_list(MediaType, ['image/jpeg'])
    assert not can_accept(acceptables, media_types)

    # Multiple both
    media_types = map_list(MediaType, ['text/html', 'application/*'])
    acceptables = map_list(MediaType, ['application/json', 'image/jpeg'])
    assert can_accept(acceptables, media_types)

    media_types = map_list(MediaType, ['text/html', 'application/*'])
    acceptables = map_list(MediaType, ['image/png', 'image/jpeg'])
    assert not can_accept(acceptables, media_types)


def test_quality():
    assert 1.0 == MediaType('image/jpeg').quality
    assert 0.8 == MediaType('image/jpeg; q=0.8').quality


def test_choosing():
    jpeg_type = MediaType('image/jpeg')
    png_type = MediaType('image/png')
    html_type = MediaType('text/html; q=0.9')
    json_type = MediaType('application/json; q=0.8')

    assert png_type.type == choose_acceptable_media_type(
        [png_type, jpeg_type],
        [MediaType('text/html'), MediaType('application/*'),
         MediaType('image/*')]
    ).type

    assert html_type.type == choose_acceptable_media_type(
        [json_type, html_type],
        [MediaType('text/html'), MediaType('application/*')]
    ).type
