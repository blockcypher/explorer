# Raven client that does nothing if there is no SENTRY_DSN (e.g. localhost)

from blockexplorer.settings import SENTRY_DSN
from raven import Client

client = Client(SENTRY_DSN)
