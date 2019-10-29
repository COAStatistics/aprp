import pytest
from django.test import TestCase


@pytest.mark.builder_backend
class BuilderBackendTestCase(TestCase):
    pass


@pytest.mark.builder
class BuilderTestCase(TestCase):
    pass
