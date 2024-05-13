import pytest

from tests.accounts.factories import (
    GroupFactory,
    GroupInformationFactory,
)


@pytest.fixture
def group_of_moa():
    return GroupFactory(name='農業部')


@pytest.fixture
def group_of_afa():
    return GroupFactory(name='農糧署')


@pytest.fixture
def group_of_afa_stat():
    return GroupFactory(name='農糧署統計室')


@pytest.fixture
def group_info_of_moa(group_of_moa):
    return GroupInformationFactory(
        name='農業部',
        group=group_of_moa,
        email_dns='moa.gov.tw',
    )


@pytest.fixture
def group_info_of_afa(group_of_afa, group_info_of_moa):
    return GroupInformationFactory(
        name='農糧署',
        group=group_of_afa,
        email_dns='mail.afa.gov.tw',
        parent=group_info_of_moa,
    )


@pytest.fixture
def group_info_of_afa_stat(group_of_afa_stat, group_info_of_afa):
    return GroupInformationFactory(
        name='統計室',
        group=group_of_afa_stat,
        email_dns='mail.afa.gov.tw',
        parent=group_info_of_afa,
    )
