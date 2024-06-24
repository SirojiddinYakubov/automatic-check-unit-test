import pytest
from rest_framework import serializers

serializer_name = 'TagSerializer'
view_name = 'TagViewSet'
view_path = 'shares.views'
model_name = 'Tag'
app_name = 'shares'


@pytest.mark.order(4)
@pytest.mark.django_db
def test_tag_viewset_class_exists():
    try:
        from shares.views import TagViewSet
    except ImportError:
        assert False, f"{view_name} class missing from {view_path}"

    try:
        from shares.models import Tag
    except ImportError:
        assert False, f"{model_name} class missing from {app_name}.models"

    assert hasattr(TagViewSet, 'queryset'), f"{view_name} queryset missing"
    assert getattr(TagViewSet, 'queryset') is not None, f"{view_name} queryset missing"
    assert hasattr(TagViewSet.queryset, 'model'), f"{view_name} queryset model missing"
    assert TagViewSet.queryset.model is Tag, f"{view_name} queryset model incorrect. " \
                                             f"Expected {model_name}, got {TagViewSet.queryset.model}"

    assert hasattr(TagViewSet, 'serializer_class'), f"{view_name} serializer_class missing"
    assert getattr(TagViewSet, 'serializer_class') is not None, f"{view_name} serializer_class missing"
    serializer = TagViewSet.serializer_class
    assert serializer.__name__ == serializer_name
    assert issubclass(serializer, serializers.ModelSerializer), f"{serializer_name} is not a ModelSerializer"
    assert hasattr(serializer, 'Meta'), f"{serializer_name} Meta missing"
    assert getattr(serializer, 'Meta') is not None, f"{serializer_name} Meta missing"
    assert hasattr(serializer.Meta, 'model'), f"{serializer_name} Meta model missing"
    assert serializer.Meta.model is Tag, f"{serializer_name} Meta model incorrect. " \
                                         f"Expected {model_name}, got {serializer.Meta.model}"
    assert hasattr(serializer.Meta, 'fields'), f"{serializer_name} Meta fields missing"
    assert getattr(serializer.Meta, 'fields') is not None, f"{serializer_name} Meta fields missing"
    assert serializer.Meta.fields == ['id', 'name', 'description']
