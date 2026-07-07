"""Command-line Telegram message search."""

from importlib.metadata import PackageNotFoundError, version

__all__ = ['__version__']

try:
	__version__ = version('telegram-grep')
except PackageNotFoundError:
	__version__ = '0.0.0'
