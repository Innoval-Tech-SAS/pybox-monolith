import pytest

from receivables.debtors.utils.identity_mask_utils import (
    mask_email,
    mask_phone,
    phone_compare_key,
)


class TestMaskEmail:
    def test_keeps_two_first_chars_and_the_suffix_after_the_last_dot(self):
        assert mask_email("dev.innovaltect@gmail.com") == "de*************@*****.com"

    def test_only_the_last_dot_is_kept_visible(self):
        assert mask_email("ana@mail.empresa.com.co") == "an*@****************.co"

    def test_short_local_part_still_hides_something(self):
        assert mask_email("ab@x.co") == "a*@*.co"
        assert mask_email("a@x.co") == "*@*.co"

    def test_domain_without_dot_is_fully_masked(self):
        assert mask_email("juan@localhost") == "ju**@*********"

    def test_never_leaks_the_full_local_part(self):
        masked = mask_email("maria.perez@correo.com")
        assert "perez" not in masked and "correo" not in masked


class TestMaskPhone:
    def test_only_last_four_digits_are_visible(self):
        assert mask_phone("573001234567") == "********4567"

    def test_ignores_non_digits(self):
        assert mask_phone("+57 300-123-4567") == "********4567"

    def test_short_number_still_hides_something(self):
        assert mask_phone("123") == "**3"


class TestPhoneCompareKey:
    @pytest.mark.parametrize("raw", ["3001234567", "573001234567", "+57 300 123 4567"])
    def test_same_number_with_or_without_country_code_matches(self, raw):
        assert phone_compare_key(raw) == "3001234567"

    @pytest.mark.parametrize("raw", ["", "abc", "12345"])
    def test_too_short_has_no_key(self, raw):
        assert phone_compare_key(raw) is None
