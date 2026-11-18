"""
Campus Lost & Found Analytics and Summary Reporting Module.

Generates statistical overviews of found inventory, claim resolution rates,
pending verification queues, and high-frequency campus loss hotspots for
administrative review.
"""

from src.database import get_connection


def get_system_summary() -> dict:
    """
    Calculate aggregate counts of users, found items, and ownership claims.

    Returns:
        dict: Dictionary containing total counts grouped by item and claim statuses.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM users")
    total_users = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM found_items")
    total_items = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM found_items WHERE status = 'unclaimed'")
    unclaimed_items = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM found_items WHERE status = 'claimed'")
    claimed_items = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM claims WHERE claim_status = 'pending'")
    pending_claims = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM claims WHERE claim_status = 'approved'")
    approved_claims = cursor.fetchone()["total"]

    conn.close()

    return {
        "total_users": total_users,
        "total_items": total_items,
        "unclaimed_items": unclaimed_items,
        "claimed_items": claimed_items,
        "pending_claims": pending_claims,
        "approved_claims": approved_claims,
    }


def get_top_locations(limit: int = 5) -> list[dict]:
    """
    Identify the campus locations with the highest number of reported found items.

    Args:
        limit (int, optional): Maximum number of locations to return. Defaults to 5.

    Returns:
        list[dict]: List of dictionaries containing 'location_found' and 'item_count'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT location_found, COUNT(*) AS item_count
        FROM found_items
        GROUP BY location_found
        ORDER BY item_count DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
