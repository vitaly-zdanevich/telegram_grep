import asyncio
from io import StringIO

import pytest
from pytest import MonkeyPatch

from telegram_grep.cli import parse_args, run_async


def test_parse_args_defaults_to_private_search() -> None:
	query, options, json_output = parse_args(['wikimedia', 'commons'])

	assert query == 'wikimedia commons'
	assert not options.include_groups
	assert not options.groups_only
	assert not options.include_bots
	assert options.limit_per_chat == 5
	assert not json_output


def test_parse_args_reads_scope_flags() -> None:
	query, options, json_output = parse_args(
		[
			'--groups',
			'--include-bots',
			'--limit-per-chat',
			'2',
			'--context',
			'1',
			'--json',
			'bot',
		]
	)

	assert query == 'bot'
	assert options.include_groups
	assert options.include_bots
	assert options.limit_per_chat == 2
	assert options.context == 1
	assert json_output


def test_parse_args_rejects_zero_limit() -> None:
	with pytest.raises(SystemExit):
		parse_args(['--limit-per-chat', '0', 'bot'])


def test_parse_args_rejects_negative_context() -> None:
	with pytest.raises(SystemExit):
		parse_args(['--context', '-1', 'bot'])


def test_run_async_reports_missing_auth(monkeypatch: MonkeyPatch) -> None:
	monkeypatch.delenv('TG_API_ID', raising=False)
	monkeypatch.delenv('TG_API_HASH', raising=False)
	stdout = StringIO()
	stderr = StringIO()

	exit_code = asyncio.run(run_async(['bot'], stdout, stderr))

	assert exit_code == 2
	assert stdout.getvalue() == ''
	assert 'TG_API_ID is required' in stderr.getvalue()
