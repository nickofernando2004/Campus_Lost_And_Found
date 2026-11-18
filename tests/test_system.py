"""
End-to-End Unit Test Suite for the Campus Lost & Found Verification System.

Verifies database schema creation, user registration/authentication, found item
reporting and keyword search, claim submission, admin claim approval, and
summary analytics reporting using an isolated temporary SQLite database.
"""

import os
import unittest
import src.database as db
from src.auth import register_user, login_user
from src.items import report_found_item, list_items, search_items
from src.claims import submit_claim, list_pending_claims, review_claim
from src.reports import get_system_summary, get_top_locations


class TestCampusLostAndFound(unittest.TestCase):
    """Test cases validating core workflows across all modular components."""

    def setUp(self) -> None:
        """Redirect database path to a clean temporary test file before each test."""
        self.test_db = "test_campus_lost_found.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        db.DB_NAME = self.test_db
        db.init_db()

    def tearDown(self) -> None:
        """Remove temporary test database after each test completes."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_full_lost_and_found_lifecycle(self) -> None:
        """Verify registration, item logging, search, claim approval, and analytics."""
        # 1. Register admin and student users
        self.assertTrue(register_user("admin_user", "pass123", "admin"))
        self.assertTrue(register_user("student_finder", "pass123", "student"))
        self.assertTrue(register_user("student_owner", "pass123", "student"))

        finder = login_user("student_finder", "pass123")
        owner = login_user("student_owner", "pass123")
        self.assertIsNotNone(finder)
        self.assertIsNotNone(owner)

        # 2. Report found item and verify search
        self.assertTrue(
            report_found_item(
                "Black Lenovo Charger",
                "Electronics",
                "65W USB-C laptop adapter",
                "Computer Lab 1",
                finder["user_id"],
            )
        )
        matches = search_items("Lenovo")
        self.assertEqual(len(matches), 1)
        item_id = matches[0]["item_id"]

        # 3. Submit ownership claim and verify pending queue
        self.assertTrue(
            submit_claim(item_id, owner["user_id"], "Serial number ends in 8842X")
        )
        pending = list_pending_claims()
        self.assertEqual(len(pending), 1)

        # 4. Approve claim as admin and verify item status flips to 'claimed'
        self.assertTrue(review_claim(pending[0]["claim_id"], "approved"))
        self.assertEqual(len(list_items(include_claimed=False)), 0)
        self.assertEqual(len(list_items(include_claimed=True)), 1)

        # 5. Verify analytics summary and hotspot counts
        summary = get_system_summary()
        self.assertEqual(summary["total_items"], 1)
        self.assertEqual(summary["claimed_items"], 1)
        self.assertEqual(summary["approved_claims"], 1)

        hotspots = get_top_locations()
        self.assertEqual(hotspots[0]["location_found"], "Computer Lab 1")


if __name__ == "__main__":
    unittest.main()
