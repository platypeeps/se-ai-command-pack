"""Subprocess coverage bootstrap for the repo-own coverage floor (task A-020).

Python auto-imports ``sitecustomize`` from any ``sys.path`` entry at startup.
The coverage run puts this directory on ``PYTHONPATH`` and sets
``COVERAGE_PROCESS_START`` so child ``python`` processes (install.py and the
.github/scripts invoked as subprocesses by the test suite) start measuring
coverage; ``coverage.process_startup()`` is a no-op unless that variable is set.

This directory is intentionally NOT a package (no ``__init__.py``) and holds no
``test*.py``, so ``unittest discover -s tests`` never collects it.
"""

import coverage

coverage.process_startup()
