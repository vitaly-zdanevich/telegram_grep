"""Output formatting for search hits."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

from telegram_grep.models import Message, SearchHit


def compact_text(text: str) -> str:
	"""Collapse whitespace for stable terminal output."""
	return ' '.join(text.split())


def format_message(message: Message, prefix: str = '') -> str:
	"""Format a single message for text output."""
	date = message.date.strftime('%Y-%m-%d %H:%M')
	direction = 'out' if message.outgoing else 'in'
	return f'{prefix}{date} #{message.id} {direction}: {compact_text(message.text)}'


def format_hit(hit: SearchHit) -> str:
	"""Format a search hit with optional neighboring messages."""
	lines = [
		f'{hit.dialog.display_name} [{hit.dialog.kind}]',
		format_message(hit.message),
	]
	lines.extend(format_message(message, prefix='  context ') for message in hit.context)
	return '\n'.join(lines)


def _json_default(value: Any) -> str:
	if isinstance(value, datetime):
		return value.isoformat()
	raise TypeError(f'Unsupported JSON value: {value!r}')


def hit_to_json(hit: SearchHit) -> str:
	"""Serialize a search hit as a JSON Lines record."""
	return json.dumps(asdict(hit), default=_json_default, ensure_ascii=False, sort_keys=True)
