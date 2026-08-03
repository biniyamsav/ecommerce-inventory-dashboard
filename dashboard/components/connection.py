import psycopg2
from psycopg2.pool import SimpleConnectionPool
import streamlit as st
from typing import Any


@st.cache_resource
def _get_pool():
    return SimpleConnectionPool(
        1,
        10,
        host=st.secrets["db"]["host"],
        dbname=st.secrets["db"]["dbname"],
        user=st.secrets["db"]["user"],
        password=st.secrets["db"]["password"],
        port=st.secrets["db"]["port"],
    )


def get_connection() -> Any:
    pool = _get_pool()
    raw = pool.getconn()

    class _PooledWrapper:
        def __init__(self, raw_conn, pool_ref):
            self._raw = raw_conn
            self._pool = pool_ref

        def cursor(self, *args, **kwargs):
            return self._raw.cursor(*args, **kwargs)

        def close(self):
            try:
                self._pool.putconn(self._raw)
            except Exception:
                try:
                    self._raw.close()
                except Exception:
                    pass

        def __getattr__(self, name):
            return getattr(self._raw, name)

    return _PooledWrapper(raw, pool)