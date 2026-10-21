import os
import sys
import tempfile

# Isolate tests from the real database, uploads and model. These must be set
# before any backend module is imported, because settings are read at import.
_TMP = tempfile.mkdtemp(prefix="aiscategorizer_test_")
os.environ["MONGODB_URL"] = "mongodb://127.0.0.1:1"  # unreachable -> SQLite fallback
os.environ["SQLITE_FALLBACK_PATH"] = os.path.join(_TMP, "test.db")
os.environ["UPLOAD_DIR"] = os.path.join(_TMP, "uploads")
os.environ["MODEL_DIR"] = os.path.join(_TMP, "no_model")
os.environ["SECRET_KEY"] = "test-secret"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
