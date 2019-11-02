import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


logger = logging.getLogger('factory')
User = get_user_model()


class Command(BaseCommand):
    help = 'Create an user.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='User Name')
        parser.add_argument('email', type=str, help='User Email')
        parser.add_argument('password', type=str, help='User Password')
        parser.add_argument('--is-superuser', action='store_true', help='Is Super User.')

    def handle(self, username, email, password, **kwargs):
        is_superuser = kwargs['is_superuser']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create(username=username, email=email, is_superuser=is_superuser)
            user.set_password(password)
            user.save()
            logger.info(f"""
    An user has been setup, use this user to sign in:
        Username: {username}
        Password: {password}
""")
        else:
            logger.info(f'User {username} already exists.')
