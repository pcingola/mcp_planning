from fastmcp import Context
from fastmcp.server import dependencies

def get_session_id_from_request(ctx: Context | None = None) -> str | None:
    """
    Get the session ID from the HTTP request headers.
    If `ctx` is None, the current FastMCP request HTTP headers are used.
    """
    try:
        return (ctx or dependencies).get_http_request().headers.get("session-id")
    except (ValueError, RuntimeError):
        return None


def get_user_id_from_request(ctx: Context | None = None) -> str | None:
    """
    Get the user ID from the HTTP request headers.
    If `ctx` is None, the current FastMCP request HTTP headers are used.
    """
    try:
        return (ctx or dependencies).get_http_request().headers.get("user-id")
    except (ValueError, RuntimeError):
        return None


def get_session_id_tuple(ctx: Context | None = None) -> tuple[str, str]:
    """
    Get the user and session IDs from the user session.
    If `ctx` is None, the current FastMCP request HTTP headers are used.
    Returns: Tuple of (user_id, session_id).
    """
    user_id = get_user_id_from_request(ctx)
    user_id = user_id or "default_user"
    session_id = get_session_id_from_request(ctx)
    session_id = session_id or "default_session"
    return user_id, session_id