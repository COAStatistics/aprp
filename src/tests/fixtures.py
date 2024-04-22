import pytest
from bs4 import BeautifulSoup
from django.http import HttpResponse


class Object:
    def __init__(self):
        self.cleaned_data = {}


@pytest.fixture
def _object():
    return Object()


@pytest.fixture
def outbox():
    from django.core import mail

    return mail.outbox


@pytest.fixture
def client():
    from django.test.client import Client, RequestFactory

    class _Client(Client):

        def __init__(self, enforce_csrf_checks=False, **defaults):
            super().__init__(enforce_csrf_checks, **defaults)
            self.factory = RequestFactory()

        def get_soup(self, *args, **kwargs):
            response = self.get(*args, **kwargs)

            if isinstance(response, HttpResponse):
                return BeautifulSoup(response.content, "lxml")

            return BeautifulSoup(response.render().content, "lxml")

        def post_soup(self, *args, **kwargs):
            response = self.post(*args, **kwargs)

            try:
                return BeautifulSoup(response.render().content, "lxml")
            except AttributeError:
                return BeautifulSoup(response.content, "lxml")

    return _Client()
