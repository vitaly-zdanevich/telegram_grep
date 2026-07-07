"""Typed data models for Telegram search."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

DialogKind = Literal['private', 'bot', 'group', 'channel', 'self']


@dataclass(frozen=True, slots=True)
class Dialog:
	"""A searchable Telegram dialog."""

	id: int
	title: str
	kind: DialogKind
	username: str | None = None

	@property
	def display_name(self) -> str:
		"""Return a compact human-readable dialog name."""
		if self.username:
			return f'{self.title} @{self.username}'
		return self.title


@dataclass(frozen=True, slots=True)
class Message:
	"""A Telegram message returned by search."""

	id: int
	date: datetime
	text: str
	outgoing: bool = False


@dataclass(frozen=True, slots=True)
class SearchHit:
	"""A matched message plus optional neighboring context."""

	dialog: Dialog
	message: Message
	context: tuple[Message, ...] = ()


@dataclass(frozen=True, slots=True)
class SearchOptions:
	"""Search scope and output options."""

	include_groups: bool = False
	groups_only: bool = False
	include_bots: bool = False
	limit_per_chat: int = 5
	context: int = 0
