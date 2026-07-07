"""Command-line interface for telegram-grep."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from collections.abc import Sequence
from typing import TextIO

from telegram_grep.config import ConfigError, load_auth_from_env
from telegram_grep.core import grep
from telegram_grep.formatting import format_hit, hit_to_json
from telegram_grep.models import SearchOptions
from telegram_grep.telethon_backend import TelethonGateway


def build_parser() -> argparse.ArgumentParser:
	"""Create the command-line parser."""
	parser = argparse.ArgumentParser(
		prog='telegram-grep',
		description='Search Telegram private chats by text.',
	)
	parser.add_argument('query', nargs='+', help='text to search for')
	parser.add_argument(
		'--groups',
		action='store_true',
		help='include group chats in addition to private chats',
	)
	parser.add_argument(
		'--groups-only',
		action='store_true',
		help='search groups and skip private chats',
	)
	parser.add_argument(
		'--include-bots',
		action='store_true',
		help='include private bot dialogs',
	)
	parser.add_argument(
		'--limit-per-chat',
		type=_positive_int,
		default=5,
		help='maximum matches per dialog (default: 5)',
	)
	parser.add_argument(
		'--context',
		type=_non_negative_int,
		default=0,
		help='neighboring messages to print before/after a match (default: 0)',
	)
	parser.add_argument(
		'--json',
		action='store_true',
		help='print JSON Lines instead of text',
	)
	return parser


def parse_args(argv: Sequence[str]) -> tuple[str, SearchOptions, bool]:
	"""Parse CLI args into a query, search options, and output mode."""
	args = build_parser().parse_args(argv)
	query = ' '.join(args.query).strip()
	if not query:
		raise ValueError('query must not be empty')
	options = SearchOptions(
		include_groups=bool(args.groups),
		groups_only=bool(args.groups_only),
		include_bots=bool(args.include_bots),
		limit_per_chat=args.limit_per_chat,
		context=args.context,
	)
	return query, options, bool(args.json)


def _positive_int(raw_value: str) -> int:
	"""Parse an argparse integer that must be at least one."""
	value = _parse_int(raw_value)
	if value < 1:
		raise argparse.ArgumentTypeError('must be at least 1')
	return value


def _non_negative_int(raw_value: str) -> int:
	"""Parse an argparse integer that must be zero or greater."""
	value = _parse_int(raw_value)
	if value < 0:
		raise argparse.ArgumentTypeError('must not be negative')
	return value


def _parse_int(raw_value: str) -> int:
	"""Parse an argparse integer with a concise user-facing error."""
	try:
		return int(raw_value)
	except ValueError as exc:
		raise argparse.ArgumentTypeError('must be an integer') from exc


async def run_async(
	argv: Sequence[str],
	stdout: TextIO,
	stderr: TextIO,
) -> int:
	"""Run the search command."""
	try:
		query, options, json_output = parse_args(argv)
		auth = load_auth_from_env(os.environ)
	except (ConfigError, ValueError) as exc:
		print(f'error: {exc}', file=stderr)
		return 2

	try:
		async with TelethonGateway(auth) as gateway:
			found = False
			async for hit in grep(gateway, query, options):
				found = True
				if json_output:
					print(hit_to_json(hit), file=stdout)
				else:
					print(format_hit(hit), file=stdout)
					print(file=stdout)
			return 0 if found else 1
	except KeyboardInterrupt:
		print('interrupted', file=stderr)
		return 130


def main(argv: Sequence[str] | None = None) -> int:
	"""Run telegram-grep."""
	return asyncio.run(run_async(sys.argv[1:] if argv is None else argv, sys.stdout, sys.stderr))
