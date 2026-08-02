def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def first_value(result, index=0, default=None):
    if result and result[0]:
        return result[0][index]
    return default


def first_value(rows, col=0, default=None):
    """Safely pull a single value out of a fetchall() result, e.g. first_value(db.average_order_value())"""
    if not rows:
        return default
    return rows[0][col]


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_rerun():
    """Attempt to rerun the Streamlit script in a way that's compatible
    across Streamlit versions.

    - Prefer `st.experimental_rerun()` when available.
    - If absent, try raising the internal RerunException used by Streamlit.
    - As a last resort toggle a session-state flag so callers can detect
      a requested rerun on next render.
    """
    try:
        import streamlit as st

        # Preferred API when present
        rerun = getattr(st, "experimental_rerun", None)
        if callable(rerun):
            return rerun()

        # Fallback: raise Streamlit's internal rerun exception
        try:
            from streamlit.runtime.scriptrunner.script_runner import RerunException

            raise RerunException
        except Exception:
            # Last resort: set a small toggle in session_state to indicate a
            # requested rerun. The app will naturally rerun when state changes
            # in many environments.
            st.session_state.__dict__.setdefault("_safe_rerun_toggle", False)
            st.session_state._safe_rerun_toggle = not st.session_state._safe_rerun_toggle
            return None
    except Exception:
        # If even importing streamlit fails here, do nothing.
        return None
