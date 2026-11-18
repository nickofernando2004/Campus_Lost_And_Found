"""
Ownership Claim Verification Module for the Campus Lost & Found System.

Manages student claim submissions with proof-of-ownership descriptions,
retrieves pending/user claim histories, and allows campus security/OSA
admins to approve or reject claims with automatic item status updates.
"""

from datetime import datetime
from src.database import get_connection


def submit_claim(item_id: int, claimant_id: int, proof_description: str) -> bool:
    """
    Submit a new ownership claim for an unclaimed found item.

    Verifies that the item exists and is still 'unclaimed' before logging
    a 'pending' claim record for admin review.

    Args:
        item_id (int): Primary key ID of the found item being claimed.
        claimant_id (int): User ID of the student submitting the claim.
        proof_description (str): Identifying details proving ownership
            (e.g., wallpaper, serial number, contents inside a bag).

    Returns:
        bool: True if the claim is submitted successfully, False otherwise.
    """
    proof_description = proof_description.strip()
    if not proof_description:
        print("Error: Proof of ownership description cannot be empty.")
        return False

    conn = get_connection()
    cursor = conn.cursor()

    # Verify the target item exists and check its custody status
    cursor.execute(
        "SELECT item_name, status FROM found_items WHERE item_id = ?",
        (item_id,),
    )
    item = cursor.fetchone()

    if not item:
        print(f"Error: Item ID {item_id} does not exist.")
        conn.close()
        return False

    if item["status"] != "unclaimed":
        print(f"Error: '{item['item_name']}' has already been claimed.")
        conn.close()
        return False

    # Prevent duplicate pending claims by the same student on the same item
    cursor.execute(
        """
        SELECT claim_id FROM claims
        WHERE item_id = ? AND claimant_id = ? AND claim_status = 'pending'
        """,
        (item_id, claimant_id),
    )
    if cursor.fetchone():
        print("Error: You already have a pending claim for this item.")
        conn.close()
        return False

    # Record the new pending claim in the database
    cursor.execute(
        """
        INSERT INTO claims (item_id, claimant_id, proof_description, claim_status)
        VALUES (?, ?, ?, 'pending')
        """,
        (item_id, claimant_id, proof_description),
    )
    conn.commit()
    conn.close()

    print(f"Claim submitted for '{item['item_name']}'! Awaiting admin verification.")
    return True


def list_user_claims(claimant_id: int) -> list[dict]:
    """
    Retrieve all ownership claims submitted by a specific student.

    Args:
        claimant_id (int): User ID of the claimant.

    Returns:
        list[dict]: List of claim records joined with item details.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT c.claim_id, c.item_id, f.item_name, c.proof_description,
               c.claim_status, c.submitted_at, c.reviewed_at
        FROM claims c
        JOIN found_items f ON c.item_id = f.item_id
        WHERE c.claimant_id = ?
        ORDER BY c.claim_id DESC
        """,
        (claimant_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_pending_claims() -> list[dict]:
    """
    Retrieve all pending ownership claims awaiting admin verification.

    Returns:
        list[dict]: Pending claims joined with item names and claimant usernames.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT c.claim_id, c.item_id, f.item_name, f.description AS item_desc,
               u.username AS claimant, c.proof_description, c.submitted_at
        FROM claims c
        JOIN found_items f ON c.item_id = f.item_id
        JOIN users u ON c.claimant_id = u.user_id
        WHERE c.claim_status = 'pending'
        ORDER BY c.claim_id ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def review_claim(claim_id: int, decision: str) -> bool:
    """
    Approve or reject a pending ownership claim (Admin privilege).

    When approved, updates the claim status to 'approved', marks the associated
    item as 'claimed', and automatically rejects any competing pending claims
    for that same item.

    Args:
        claim_id (int): Primary key ID of the claim to review.
        decision (str): Either 'approved' or 'rejected'.

    Returns:
        bool: True if the review updates cleanly, False otherwise.
    """
    decision = decision.strip().lower()
    if decision not in ("approved", "rejected"):
        print("Error: Decision must be 'approved' or 'rejected'.")
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT item_id, claim_status FROM claims WHERE claim_id = ?",
        (claim_id,),
    )
    claim = cursor.fetchone()

    if not claim:
        print(f"Error: Claim ID {claim_id} not found.")
        conn.close()
        return False

    if claim["claim_status"] != "pending":
        print(f"Error: Claim #{claim_id} has already been {claim['claim_status']}.")
        conn.close()
        return False

    reviewed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update the selected claim's status and review timestamp
    cursor.execute(
        """
        UPDATE claims
        SET claim_status = ?, reviewed_at = ?
        WHERE claim_id = ?
        """,
        (decision, reviewed_at, claim_id),
    )

    if decision == "approved":
        # Mark the found item as claimed
        cursor.execute(
            "UPDATE found_items SET status = 'claimed' WHERE item_id = ?",
            (claim["item_id"],),
        )
        # Automatically reject competing pending claims on the same item
        cursor.execute(
            """
            UPDATE claims
            SET claim_status = 'rejected', reviewed_at = ?
            WHERE item_id = ? AND claim_id != ? AND claim_status = 'pending'
            """,
            (reviewed_at, claim["item_id"], claim_id),
        )

    conn.commit()
    conn.close()
    print(f"Claim #{claim_id} has been {decision}.")
    return True
