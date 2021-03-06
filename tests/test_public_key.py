from mock import patch
import pytest

from constants import SSH_KEY_1, SSH_KEY_BAD
from fixtures import session, users  # noqa: F401
from grouper.plugin.base import BasePlugin
from grouper.plugin.exceptions import PluginRejectedPublicKey
from grouper.plugin.proxy import PluginProxy
from grouper.public_key import (
    add_public_key,
    BadPublicKey,
    DuplicateKey,
    get_public_keys_of_user,
    PublicKeyParseError,
)


class PublicKeyPlugin(BasePlugin):
    def will_add_public_key(self, key):
        raise PluginRejectedPublicKey()


def test_duplicate_key(session, users):
    user = users["cbguder@a.co"]

    add_public_key(session, user, SSH_KEY_1)
    assert len(get_public_keys_of_user(session, user.id)) == 1

    with pytest.raises(DuplicateKey):
        add_public_key(session, user, SSH_KEY_1)

    assert len(get_public_keys_of_user(session, user.id)) == 1


def test_bad_key(session, users):
    user = users["cbguder@a.co"]

    with pytest.raises(PublicKeyParseError):
        add_public_key(session, user, SSH_KEY_BAD)

    assert get_public_keys_of_user(session, user.id) == []


@patch("grouper.public_key.get_plugin_proxy")
def test_rejected_key(get_plugin_proxy, session, users):
    get_plugin_proxy.return_value = PluginProxy([PublicKeyPlugin()])

    user = users["cbguder@a.co"]

    with pytest.raises(BadPublicKey):
        add_public_key(session, user, SSH_KEY_1)

    assert get_public_keys_of_user(session, user.id) == []
