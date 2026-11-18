"""
Database Sample Data Seeder for the Campus Lost & Found System.

Populates the SQLite database with realistic default student/admin accounts,
sample found campus items across multiple categories, and an initial pending
ownership claim for immediate testing and demonstration.
"""

from src.database import init_db, get_connection
from src.auth import register_user, login_user
from src.items import report_found_item, list_items
from src.claims import submit_claim


def seed_database() -> None:
    """
    Initialize tables and insert sample users, found items, and a pending claim.

    Checks whether sample data already exists before inserting to remain safe
    against accidental duplicate runs.
    """
    init_db()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS count FROM users")
    existing_users = cursor.fetchone()["count"]
    conn.close()

    if existing_users > 0:
        print("Database already contains records. Skipping seed insertion.")
        return

    print("Seeding sample accounts...")
    register_user("osa_admin", "admin123", "admin")
    register_user("juan_cs", "student123", "student")
    register_user("maria_it", "student123", "student")

    juan = login_user("juan_cs", "student123")
    maria = login_user("maria_it", "student123")

    if juan and maria:
        print("\nSeeding sample found items...")
        report_found_item(
            item_name="Casio Scientific Calculator",
            category="Electronics",
            description="Black fx-991ES PLUS with blue sticker on the back cover",
            location_found="CAS Building Room 204",
            reported_by=juan["user_id"],
        )
        report_found_item(
            item_name="NORSU Student ID & Lanyard",
            category="ID-Wallet",
            description="BS Computer Science ID inside clear plastic holder",
            location_found="Main Library 2nd Floor",
            reported_by=maria["user_id"],
        )
        report_found_item(
            item_name="Aquaflask 22oz Tumbler",
            category="Personal",
            description="Matte navy blue insulated bottle with minor dent at base",
            location_found="University Canteen",
            reported_by=juan["user_id"],
        )

        items = list_items(include_claimed=False)
        if items:
            first_item_id = items[-1]["item_id"]
            print("\nSeeding sample ownership claim...")
            submit_claim(
                item_id=first_item_id,
                claimant_id=maria["user_id"],
                proof_description="Has my initials 'M.I.' written under the battery cover",
            )

    print("\nDatabase seeding complete! Sample credentials:")
    print("  Admin   -> username: osa_admin | password: admin123")
    print("  Student -> username: juan_cs   | password: student123")
    print("  Student -> username: maria_it  | password: student123")


if __name__ == "__main__":
    seed_database()
