from collections.abc import AsyncIterator, Sequence
from datetime import UTC, datetime
from typing import TypeVar

import pytest

from telegram_grep.core import dialog_allowed, grep
from telegram_grep.models import Dialog, Message, SearchOptions

T = TypeVar('T')


class FakeGateway:
	def __init__(self) -> None:
		self.dialogs = [
			Dialog(id=1, title='Alice', kind='private', username='alice'),
			Dialog(id=2, title='Project Group', kind='group'),
			Dialog(id=3, title='News', kind='channel'),
			Dialog(id=4, title='BotFather', kind='bot', username='BotFather'),
		]
		self.messages = {
			1: [Message(id=10, date=_dt(), text='Wikimedia Commons bot discussion')],
			2: [Message(id=20, date=_dt(), text='Group Wikimedia Commons bot discussion')],
			4: [Message(id=40, date=_dt(), text='Bot private match')],
		}
		self.context = {
			1: [Message(id=9, date=_dt(), text='before'), Message(id=11, date=_dt(), text='after')],
		}

	async def iter_dialogs(self) -> AsyncIterator[Dialog]:
		for dialog in self.dialogs:
			yield dialog

	async def search_messages(
		self,
		dialog: Dialog,
		query: str,
		limit: int,
	) -> AsyncIterator[Message]:
		count = 0
		for message in self.messages.get(dialog.id, []):
			if query.lower() in message.text.lower() and count < limit:
				count += 1
				yield message

	async def get_context(
		self,
		dialog: Dialog,
		message_id: int,
		radius: int,
	) -> Sequence[Message]:
		return self.context.get(dialog.id, ())


def _dt() -> datetime:
	return datetime(2026, 7, 7, 12, 0, tzinfo=UTC)


def test_dialog_allowed_defaults_to_private_human_chats() -> None:
	options = SearchOptions()

	assert dialog_allowed(Dialog(id=1, title='Alice', kind='private'), options)
	assert not dialog_allowed(Dialog(id=2, title='Group', kind='group'), options)
	assert not dialog_allowed(Dialog(id=3, title='Channel', kind='channel'), options)
	assert not dialog_allowed(Dialog(id=4, title='Bot', kind='bot'), options)


def test_dialog_allowed_can_include_groups_and_bots() -> None:
	options = SearchOptions(include_groups=True, include_bots=True)

	assert dialog_allowed(Dialog(id=1, title='Group', kind='group'), options)
	assert dialog_allowed(Dialog(id=2, title='Bot', kind='bot'), options)


def test_dialog_allowed_groups_only_skips_private_chats() -> None:
	options = SearchOptions(groups_only=True)

	assert dialog_allowed(Dialog(id=1, title='Group', kind='group'), options)
	assert not dialog_allowed(Dialog(id=2, title='Alice', kind='private'), options)


def test_grep_searches_private_chats_by_default() -> None:
	hits = list_async(grep(FakeGateway(), 'Wikimedia Commons bot', SearchOptions()))

	assert [hit.dialog.title for hit in hits] == ['Alice']
	assert hits[0].message.text == 'Wikimedia Commons bot discussion'


def test_grep_can_include_groups() -> None:
	hits = list_async(
		grep(
			FakeGateway(),
			'Wikimedia Commons bot',
			SearchOptions(include_groups=True),
		)
	)

	assert [hit.dialog.title for hit in hits] == ['Alice', 'Project Group']


def test_grep_can_include_context() -> None:
	hits = list_async(
		grep(
			FakeGateway(),
			'Wikimedia Commons bot',
			SearchOptions(context=1),
		)
	)

	assert [message.text for message in hits[0].context] == ['before', 'after']


def test_grep_rejects_empty_query() -> None:
	with pytest.raises(ValueError, match='empty'):
		list_async(grep(FakeGateway(), ' ', SearchOptions()))


def list_async(iterator: AsyncIterator[T]) -> list[T]:
	async def collect() -> list[T]:
		return [item async for item in iterator]

	import asyncio

	return asyncio.run(collect())
