import os
import sys
from pathlib import Path

import pulp
import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '6.api'))


@pytest.fixture(autouse=True)
def cbc_path(monkeypatch):
    path = os.environ.get('PYOPTBOOK_CBC_PATH')
    if path:
        monkeypatch.setattr(pulp.COIN_CMD, 'defaultPath', lambda self: path)
        if pulp.LpSolverDefault is not None:
            monkeypatch.setattr(pulp.LpSolverDefault, 'path', path)
