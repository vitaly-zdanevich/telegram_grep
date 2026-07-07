"""Environment configuration for Telegram MTProto authentication."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from os import PathLike
from pathlib import Path


class ConfigError(ValueError):
	"""Raised when environment configuration is invalid."""


@dataclass(frozen=True, slots=True)
class TelegramAuth:
	"""MTProto credentials and session settings."""

	api_id: int
	api_hash: str
	session: str | None
	session_file: Path
	phone: str | None = None


def load_auth_from_env(
	env: Mapping[str, str],
	default_session_file: str | PathLike[str] = 'telegram_grep.session',
) -> TelegramAuth:
	"""Read MTProto credentials from environment variables."""
	api_id_raw = env.get('TG_API_ID', '').strip()
	api_hash = env.get('TG_API_HASH', '').strip()

	if not api_id_raw:
		raise ConfigError('TG_API_ID is required')
	if not api_hash:
		raise ConfigError('TG_API_HASH is required')

	try:
		api_id = int(api_id_raw)
	except ValueError as exc:
		raise ConfigError('TG_API_ID must be an integer') from exc

	session = env.get('TG_SESSION')
	if session is not None:
		session = session.strip() or None

	session_file_raw = env.get('TG_SESSION_FILE', '').strip()
	session_file = Path(session_file_raw) if session_file_raw else Path(default_session_file)

	phone = env.get('TG_PHONE')
	if phone is not None:
		phone = phone.strip() or None

	return TelegramAuth(
		api_id=api_id,
		api_hash=api_hash,
		session=session,
		session_file=session_file,
		phone=phone,
	)
