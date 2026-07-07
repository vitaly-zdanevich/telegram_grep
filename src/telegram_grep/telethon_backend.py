"""Telethon adapter for MTProto-backed Telegram search."""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from typing import Any

from telegram_grep.config import TelegramAuth
from telegram_grep.models import Dialog, DialogKind, Message


class TelethonGateway:
	"""TelegramGateway implementation backed by Telethon."""

	def __init__(self, auth: TelegramAuth) -> None:
		self._auth = auth
		self._client: Any | None = None
		self._entities: dict[int, Any] = {}

	async def __aenter__(self) -> TelethonGateway:
		"""Open the Telegram client session."""
		from telethon import TelegramClient
		from telethon.sessions import StringSession

		session_arg: Any
		if self._auth.session:
			session_arg = StringSession(self._auth.session)
		else:
			session_arg = str(self._auth.session_file)

		client = TelegramClient(session_arg, self._auth.api_id, self._auth.api_hash)
		await client.start(phone=self._auth.phone)
		self._client = client
		return self

	async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
		"""Close the Telegram client session."""
		if self._client is not None:
			await self._client.disconnect()
		self._client = None
		self._entities.clear()

	@property
	def client(self) -> Any:
		"""Return the connected Telethon client."""
		if self._client is None:
			raise RuntimeError('TelethonGateway is not connected')
		return self._client

	async def iter_dialogs(self) -> AsyncIterator[Dialog]:
		"""Yield Telethon dialogs converted to typed project models."""
		async for raw_dialog in self.client.iter_dialogs():
			entity = raw_dialog.entity
			dialog = Dialog(
				id=int(raw_dialog.id),
				title=str(raw_dialog.name or raw_dialog.title or raw_dialog.id),
				kind=classify_entity(entity),
				username=getattr(entity, 'username', None),
			)
			self._entities[dialog.id] = entity
			yield dialog

	async def search_messages(
		self,
		dialog: Dialog,
		query: str,
		limit: int,
	) -> AsyncIterator[Message]:
		"""Yield messages matching `query` in one dialog."""
		entity = self._entity_for(dialog)
		async for raw_message in self.client.iter_messages(entity, search=query, limit=limit):
			text = str(getattr(raw_message, 'raw_text', '') or '')
			if not text.strip():
				continue
			yield Message(
				id=int(raw_message.id),
				date=raw_message.date,
				text=text,
				outgoing=bool(getattr(raw_message, 'out', False)),
			)

	async def get_context(
		self,
		dialog: Dialog,
		message_id: int,
		radius: int,
	) -> Sequence[Message]:
		"""Return neighboring messages around one matched message."""
		entity = self._entity_for(dialog)
		ids = [idx for idx in range(message_id - radius, message_id + radius + 1) if idx > 0]
		if not ids:
			return ()

		raw_messages = await self.client.get_messages(entity, ids=ids)
		messages: list[Message] = []
		for raw_message in raw_messages:
			if raw_message is None or raw_message.id == message_id:
				continue
			text = str(getattr(raw_message, 'raw_text', '') or '')
			if not text.strip():
				continue
			messages.append(
				Message(
					id=int(raw_message.id),
					date=raw_message.date,
					text=text,
					outgoing=bool(getattr(raw_message, 'out', False)),
				)
			)
		return tuple(sorted(messages, key=lambda item: item.id))

	def _entity_for(self, dialog: Dialog) -> Any:
		try:
			return self._entities[dialog.id]
		except KeyError as exc:
			raise RuntimeError(f'unknown dialog entity: {dialog.id}') from exc


def classify_entity(entity: Any) -> DialogKind:
	"""Map a Telethon entity to a search scope kind."""
	from telethon.tl.types import Channel, Chat, User

	if isinstance(entity, User):
		if bool(getattr(entity, 'is_self', False)):
			return 'self'
		if bool(getattr(entity, 'bot', False)):
			return 'bot'
		return 'private'
	if isinstance(entity, Chat):
		return 'group'
	if isinstance(entity, Channel):
		if bool(getattr(entity, 'megagroup', False)):
			return 'group'
		return 'channel'
	return 'channel'
