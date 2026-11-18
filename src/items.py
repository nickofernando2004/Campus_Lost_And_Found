"""
Found Items Catalog Module for the Campus Lost & Found System.

Handles logging newly found campus items, retrieving unclaimed inventory,
and searching records by item name, category, or location found.
"""

from datetime import datetime
from src.database import get_connection


def report_found_item(
    item_name: str,
    category: str,
    description: str,
    location_found: str,
    reported_by: int,
    date_found: str | None = None,
) -> bool:
    """
    Log a newly found item into the found_items table.

    Args:
        item_name (str): Short name or title of the found item (e.g., 'Black Umbrella').
        category (str): Item classification (e.g., 'Electronics', 'ID/Wallet', 'Personal').
        description (str): General physical details without revealing private proof markers.
        location_found (str): Campus building, room, or landmark where the item was found.
        reported_by (int): User ID of the student or admin logging the report.
        date_found (str | None, optional): Date found (YYYY-MM-DD). Defaults to today's date.

    Returns:
        bool: True if the item is recorded successfully, False if validation fails.
    """
    item_name = item_name.strip()
    category = category.strip()
    description = description.strip()
    location_found = location_found.strip()

    # Validate that required descriptive fields are provided
    if not all([item_name, category, description, location_found]):
        print("Error: Item name, category, description, and location are all required.")
        return False

    if not date_found or not date_found.strip():
        date_found = datetime.now().strftime("%Y-%m-%d")
    else:
        date_found = date_found.strip()

    conn = get_connection()
    cursor = conn.cursor()

    # Insert the found item with default 'unclaimed' custody status
    cursor.execute(
        """
        INSERT INTO found_items (
            item_name, category, description, location_found, date_found, status, reported_by
        )
        VALUES (?, ?, ?, ?, ?, 'unclaimed', ?)
        """,
        (item_name, category, description, location_found, date_found, reported_by),
    )
    conn.commit()
    conn.close()

    print(f"Success: '{item_name}' logged at {location_found} (Status: unclaimed).")
    return True


def list_items(include_claimed: bool = False) -> list[dict]:
    """
    Retrieve found items from the catalog, joined with the reporter's username.

    Args:
        include_claimed (bool, optional): If False, returns only 'unclaimed' items.
            If True, returns all items regardless of status. Defaults to False.

    Returns:
        list[dict]: List of item records formatted as dictionaries.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if include_claimed:
        cursor.execute(
            """
            SELECT f.item_id, f.item_name, f.category, f.description,
                   f.location_found, f.date_found, f.status, u.username AS reporter
            FROM found_items f
            JOIN users u ON f.reported_by = u.user_id
            ORDER BY f.item_id DESC
            """
        )
    else:
        cursor.execute(
            """
            SELECT f.item_id, f.item_name, f.category, f.description,
                   f.location_found, f.date_found, f.status, u.username AS reporter
            FROM found_items f
            JOIN users u ON f.reported_by = u.user_id
            WHERE f.status = 'unclaimed'
            ORDER BY f.item_id DESC
            """
        )

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def search_items(keyword: str) -> list[dict]:
    """
    Search found items by matching a keyword against name, category, or location.

    Args:
        keyword (str): Partial or full search string entered by the user.

    Returns:
        list[dict]: Matching found item records as dictionaries.
    """
    pattern = f"%{keyword.strip()}%"
    conn = get_connection()
    cursor = conn.cursor()

    # Perform case-insensitive LIKE search across key item attributes
    cursor.execute(
        """
        SELECT f.item_id, f.item_name, f.category, f.description,
               f.location_found, f.date_found, f.status, u.username AS reporter
        FROM found_items f
        JOIN users u ON f.reported_by = u.user_id
        WHERE f.item_name LIKE ?
           OR f.category LIKE ?
           OR f.location_found LIKE ?
        ORDER BY f.item_id DESC
        """,
        (pattern, pattern, pattern),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
