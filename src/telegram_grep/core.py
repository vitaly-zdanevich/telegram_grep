"""Core search orchestration independent from Telegram client libraries."""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from typing import Protocol

from telegram_grep.models import Dialog, Message, SearchHit, SearchOptions


class TelegramGateway(Protocol):
	"""Minimal async interface needed to search Telegram dialogs."""

	def iter_dialogs(self) -> AsyncIterator[Dialog]:
		"""Yield dialogs visible to the logged-in Telegram account."""
		...

	def search_messages(
		self,
		dialog: Dialog,
		query: str,
		limit: int,
	) -> AsyncIterator[Message]:
		"""Yield messages in `dialog` matching `query`."""
		...

	async def get_context(
		self,
		dialog: Dialog,
		message_id: int,
		radius: int,
	) -> Sequence[Message]:
		"""Return neighboring messages around `message_id`."""
		...


def dialog_allowed(dialog: Dialog, options: SearchOptions) -> bool:
	"""Return whether a dialog belongs to the selected search scope."""
	if options.groups_only:
		return dialog.kind == 'group'
	if dialog.kind == 'private':
		return True
	if dialog.kind == 'bot':
		return options.include_bots
	if dialog.kind == 'group':
		return options.include_groups
	return False


async def grep(
	gateway: TelegramGateway,
	query: str,
	options: SearchOptions,
) -> AsyncIterator[SearchHit]:
	"""Search allowed dialogs and yield matching messages."""
	if not query.strip():
		raise ValueError('query must not be empty')
	if options.limit_per_chat < 1:
		raise ValueError('limit_per_chat must be at least 1')
	if options.context < 0:
		raise ValueError('context must not be negative')

	async for dialog in gateway.iter_dialogs():
		if not dialog_allowed(dialog, options):
			continue
		async for message in gateway.search_messages(dialog, query, options.limit_per_chat):
			context: tuple[Message, ...] = ()
			if options.context:
				context = tuple(await gateway.get_context(dialog, message.id, options.context))
			yield SearchHit(dialog=dialog, message=message, context=context)
