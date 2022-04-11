import os
import sys
from multiprocessing import Process
import socket
from contextlib import closing

import pytest

from .pact_provider import run_server


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server():
    os.environ["PROVIDER_PORT"] = str(find_free_port())
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    yield proc

    # Cleanup after test
    if sys.version_info >= (3, 7):
        # multiprocessing.kill is new in 3.7
        proc.kill()
    else:
        proc.terminate()
