from pathlib import Path

import pytest

from telegram_grep.config import ConfigError, load_auth_from_env


def test_load_auth_from_env_reads_required_values() -> None:
	auth = load_auth_from_env(
		{
			'TG_API_ID': '123',
			'TG_API_HASH': 'hash',
			'TG_SESSION': 'token',
			'TG_SESSION_FILE': '/tmp/custom.session',
			'TG_PHONE': '+995555000000',
		}
	)

	assert auth.api_id == 123
	assert auth.api_hash == 'hash'
	assert auth.session == 'token'
	assert auth.session_file == Path('/tmp/custom.session')
	assert auth.phone == '+995555000000'


def test_load_auth_from_env_uses_default_session_file() -> None:
	auth = load_auth_from_env({'TG_API_ID': '123', 'TG_API_HASH': 'hash'})

	assert auth.session is None
	assert auth.session_file == Path('telegram_grep.session')


def test_load_auth_from_env_rejects_missing_hash() -> None:
	with pytest.raises(ConfigError, match='TG_API_HASH'):
		load_auth_from_env({'TG_API_ID': '123'})


def test_load_auth_from_env_rejects_non_integer_api_id() -> None:
	with pytest.raises(ConfigError, match='integer'):
		load_auth_from_env({'TG_API_ID': 'abc', 'TG_API_HASH': 'hash'})
