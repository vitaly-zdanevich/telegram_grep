from datetime import UTC, datetime

from telegram_grep.formatting import compact_text, format_hit, hit_to_json
from telegram_grep.models import Dialog, Message, SearchHit


def test_compact_text_collapses_whitespace() -> None:
	assert compact_text(' a\n  b\tc ') == 'a b c'


def test_format_hit_includes_dialog_and_context() -> None:
	hit = SearchHit(
		dialog=Dialog(id=1, title='Alice', kind='private', username='alice'),
		message=Message(id=2, date=_dt(), text='hello'),
		context=(Message(id=1, date=_dt(), text='before'),),
	)

	output = format_hit(hit)

	assert 'Alice @alice [private]' in output
	assert '2026-07-07 12:00 #2 in: hello' in output
	assert 'context 2026-07-07 12:00 #1 in: before' in output


def test_hit_to_json_serializes_datetime() -> None:
	hit = SearchHit(
		dialog=Dialog(id=1, title='Alice', kind='private'),
		message=Message(id=2, date=_dt(), text='hello'),
	)

	output = hit_to_json(hit)

	assert '"title": "Alice"' in output
	assert '"date": "2026-07-07T12:00:00+00:00"' in output


def _dt() -> datetime:
	return datetime(2026, 7, 7, 12, 0, tzinfo=UTC)
