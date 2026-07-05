from fivemanager.tmux import format_bytes, session_name


def test_session_name_is_stable_and_namespaced():
    assert session_name({"id": 2, "key": "main-rp"}) == "fivemanager-2-main-rp"


def test_format_bytes():
    assert format_bytes(None) == "-"
    assert format_bytes(512) == "512B"
    assert format_bytes(1024 * 1024) == "1M"
    assert format_bytes(1024 * 1024 * 1024) == "1.0G"
