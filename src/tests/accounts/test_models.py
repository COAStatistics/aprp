import pytest

from apps.accounts.models import GroupInformation
from tests.accounts.factories import GroupInformationFactory


@pytest.mark.django_db
class TestGroupInformationModel:
    def test_instance(self, group_info_of_afa):
        info = group_info_of_afa

        assert info.group is not None
        assert info.parent is not None

    def test_email_dns_field_validation(self, group_info_of_moa):
        with pytest.raises(Exception):
            GroupInformationFactory.create(
                group=group_info_of_moa.group,
                email_dns='this_is_not_a_valid_email_dns',
            )

    def test_instance_with_null_group(self):
        with pytest.raises(Exception):
            GroupInformationFactory.create(group=None)

    def test_instance_delete_with_group(self, group_info_of_moa):
        group_info_of_moa.group.delete()

        with pytest.raises(Exception):
            GroupInformation.objects.get(id=group_info_of_moa.id)

    def test_instance_delete_with_parent(self, group_info_of_afa):
        group_info_of_afa.parent.delete()

        info = GroupInformation.objects.get(id=group_info_of_afa.id)

        assert info.parent is None

    def test_parents_method(self, group_info_of_afa_stat):
        info_afa = group_info_of_afa_stat.parent
        info_moa = info_afa.parent
        parents = group_info_of_afa_stat.parents()

        assert len(parents) == 3
        assert parents[0] == group_info_of_afa_stat
        assert parents[1] == info_afa
        assert parents[2] == info_moa

    def test_has_child_method(self, group_info_of_afa_stat):
        info_afa = group_info_of_afa_stat.parent

        assert info_afa.has_child is True

    def test_query_set_end_groups_method(self, group_info_of_afa_stat):
        end_groups = GroupInformation.objects.end_groups()

        assert end_groups.count() == 1
        assert end_groups.first() == group_info_of_afa_stat
