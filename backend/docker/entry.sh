#!/usr/bin/env sh
set -e

. /.venv/bin/activate

  exec /.venv/bin/uvicorn main:app --port ${API_INFO_PORT:-8000} --host 0.0.0.0 --reload
else
  exec /.venv/bin/uvicorn main:app --port ${API_INFO_PORT:-8000} --host 0.0.0.0 --reload
fi
