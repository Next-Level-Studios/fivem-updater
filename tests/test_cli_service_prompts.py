from fivemanager.cli import _alias_notice


def test_alias_notice_exists():
    assert callable(_alias_notice)
