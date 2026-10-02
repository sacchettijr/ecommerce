import os
import sys

# =========================================================
#   TESTES
# =========================================================


TESTING: bool = "test" in sys.argv or "PYTEST_VERSION" in os.environ
