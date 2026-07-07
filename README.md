# telegram_grep

Search Telegram messages from the command line.

By default `telegram-grep` searches private one-to-one human chats only. It skips
groups, channels, and bot dialogs unless you opt in.

## Install

```sh
python -m pip install .
```

For development:

```sh
python -m pip install -e '.[dev]'
```

## Authentication

This uses Telegram MTProto through [Telethon](https://docs.telethon.dev/), not
the Bot API. A Telegram bot token cannot search your personal private chats.

Required environment:

```sh
export TG_API_ID=123456
export TG_API_HASH=0123456789abcdef0123456789abcdef
```

Session options:

```sh
# Recommended for automation: Telethon StringSession token.
export TG_SESSION='...'

# Or a local session file. Default: ./telegram_grep.session
export TG_SESSION_FILE=/path/to/telegram_grep.session
```

If neither session option exists, Telethon will create/use `telegram_grep.session`
and may prompt interactively for login. You can also set `TG_PHONE` for the first
login.

## Usage

Search private human chats:

```sh
telegram-grep 'wikimedia commons bot'
```

Include groups:

```sh
telegram-grep --groups 'wikimedia commons bot'
```

Search only groups:

```sh
telegram-grep --groups-only 'wikimedia commons bot'
```

Include bot private dialogs:

```sh
telegram-grep --include-bots 'wikimedia commons bot'
```

Print JSON Lines:

```sh
telegram-grep --json 'wikimedia commons bot'
```

Show neighboring messages:

```sh
telegram-grep --context 2 'wikimedia commons bot'
```

## Related Documentation

- [Telethon documentation](https://docs.telethon.dev/)
- [Telethon sessions](https://docs.telethon.dev/en/stable/concepts/sessions.html)
- [Telegram API development tools](https://my.telegram.org/apps)
- [Telegram MTProto API](https://core.telegram.org/api)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)

## Publishing

CI publishes to PyPI on every push to `main` after tests pass.

PyPI must have a Trusted Publisher configured for:

- owner/repository: `vitaly-zdanevich/telegram_grep`
- workflow: `.github/workflows/ci.yml`
- environment: `pypi`

Versions are derived from Git tags/commits through `hatch-vcs`, because PyPI
does not allow re-uploading the same version.
