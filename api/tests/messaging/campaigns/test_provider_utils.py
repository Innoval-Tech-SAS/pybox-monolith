"""Tests puros de `provider_utils.py`: selección de proveedor por canal y
normalización de teléfonos antes de enviar. El caso de mayor riesgo es
`normalize_phone` -- si antepone el indicativo dos veces, el envío falla contra
el proveedor real; si nunca lo antepone, el mensaje no llega.
"""

import pytest

from messaging.campaigns.utils.provider_utils import (
    is_phone_channel,
    normalize_phone,
    provider_for_channel,
)
from messaging.channels.enums.channel_enums import ChannelName
from messaging.contacts.enums.contact_enums import ProviderType


class TestProviderForChannel:
    @pytest.mark.parametrize("channel", [ChannelName.SMS, ChannelName.EMAIL])
    def test_nrs360_channels_map_to_nrs360(self, channel):
        assert provider_for_channel(channel) == ProviderType.NRS360

    def test_whatsapp_maps_to_whatsapp_cloud(self):
        assert provider_for_channel(ChannelName.WHATSAPP) == ProviderType.WHATSAPP_CLOUD

    @pytest.mark.parametrize("channel", [ChannelName.CALL, ChannelName.CALL_IA])
    def test_voice_channels_have_no_provider(self, channel):
        # NRS360_CHANNELS solo cubre SMS/EMAIL -- las llamadas no tienen proveedor
        # mapeado en esta función (se resuelven por otra vía en el dispatcher).
        assert provider_for_channel(channel) is None


class TestIsPhoneChannel:
    @pytest.mark.parametrize(
        "channel",
        [ChannelName.SMS, ChannelName.WHATSAPP, ChannelName.CALL, ChannelName.CALL_IA],
    )
    def test_phone_channels_return_true(self, channel):
        assert is_phone_channel(channel) is True

    def test_email_is_not_a_phone_channel(self):
        assert is_phone_channel(ChannelName.EMAIL) is False


class TestNormalizePhone:
    def test_local_number_gets_country_code_prefixed(self):
        assert normalize_phone("3001234567", "57") == "573001234567"

    def test_number_already_prefixed_is_left_as_is(self):
        assert normalize_phone("573001234567", "57") == "573001234567"

    def test_strips_plus_spaces_and_dashes_before_prefixing(self):
        assert normalize_phone("+57 300-123-4567", "57") == "573001234567"

    def test_country_code_with_plus_sign_is_normalized_too(self):
        assert normalize_phone("3001234567", "+57") == "573001234567"

    def test_empty_value_returns_value_unchanged(self):
        assert normalize_phone("", "57") == ""

    def test_empty_country_code_returns_value_unchanged(self):
        assert normalize_phone("3001234567", "") == "3001234567"

    def test_short_number_starting_with_code_digits_is_still_prefixed(self):
        # 10 digitos o menos: aunque "empiece" con el codigo por coincidencia, se trata
        # como numero local (la condicion exige len(digits) > 10 para NO prefijar).
        assert normalize_phone("5712345", "57") == "575712345"

    def test_none_country_code_does_not_raise(self):
        assert normalize_phone("3001234567", None) == "3001234567"
