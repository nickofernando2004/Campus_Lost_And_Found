"""
Main Command-Line Interface (CLI) Entry Point for the Campus Lost & Found System.

Integrates database initialization, user authentication, found item reporting,
keyword searching, student ownership claims, and admin claim verification into
a unified, role-aware interactive terminal application.
"""

from src.database import init_db
from src.auth import register_user, login_user
from src.items import report_found_item, list_items, search_items
from src.claims import (
    submit_claim,
    list_user_claims,
    list_pending_claims,
    review_claim,
)


def display_items(items: list[dict]) -> None:
    """
    Format and print a list of found item records in the terminal.

    Args:
        items (list[dict]): Item dictionaries returned from items module queries.
    """
    if not items:
        print("\nNo matching found items available.")
        return

    print("\n--- Campus Lost & Found Catalog ---")
    for item in items:
        print(
            f"[ID: {item['item_id']}] {item['item_name']} ({item['category']}) "
            f"| Location: {item['location_found']} | Date: {item['date_found']} "
            f"| Status: {item['status'].upper()}"
        )
        print(f"   Description: {item['description']} (Reported by: {item['reporter']})")


def user_session(user: dict) -> None:
    """
    Run the authenticated interactive menu loop tailored to the user's role.

    Students can view/search found items, report found items, submit ownership
    claims, and track their claim statuses. Admins additionally get options to
    view full item history and approve/reject pending ownership claims.

    Args:
        user (dict): Authenticated user dictionary ('user_id', 'username', 'role').
    """
    while True:
        print(f"\n--- Welcome, {user['username']} ({user['role'].capitalize()}) ---")
        print("1. View Unclaimed Items")
        print("2. Search Found Items")
        print("3. Report a Found Item")
        print("4. Submit an Ownership Claim")
        print("5. My Submitted Claims")
        if user["role"] == "admin":
            print("6. Review Pending Claims (Admin)")
            print("7. View All Items History (Admin)")
        print("0. Logout")

        choice = input("Select an option: ").strip()

        if choice == "1":
            display_items(list_items(include_claimed=False))

        elif choice == "2":
            keyword = input("Enter item name, category, or campus location: ")
            display_items(search_items(keyword))

        elif choice == "3":
            print("\n--- Report a Found Item ---")
            name = input("Item Name: ")
            category = input("Category (Electronics / ID-Wallet / Books / Personal): ")
            description = input("General Description: ")
            location = input("Campus Location Found: ")
            date_found = input("Date Found (YYYY-MM-DD, leave blank for today): ")
            report_found_item(name, category, description, location, user["user_id"], date_found)

        elif choice == "4":
            print("\n--- Submit an Ownership Claim ---")
            try:
                item_id = int(input("Enter Found Item ID to claim: ").strip())
                proof = input("Enter Proof of Ownership (e.g., wallpaper, serial #, contents): ")
                submit_claim(item_id, user["user_id"], proof)
            except ValueError:
                print("Error: Item ID must be a valid number.")

        elif choice == "5":
            claims = list_user_claims(user["user_id"])
            if not claims:
                print("\nYou have not submitted any ownership claims.")
            else:
                print("\n--- My Submitted Claims ---")
                for c in claims:
                    reviewed = c["reviewed_at"] if c["reviewed_at"] else "Pending Review"
                    print(
                        f"[Claim #{c['claim_id']}] Item: {c['item_name']} (ID: {c['item_id']}) "
                        f"| Status: {c['claim_status'].upper()} | Reviewed: {reviewed}"
                    )
                    print(f"   Proof Submitted: {c['proof_description']}")

        elif choice == "6" and user["role"] == "admin":
            pending = list_pending_claims()
            if not pending:
                print("\nNo pending claims awaiting verification.")
            else:
                print("\n--- Pending Ownership Claims ---")
                for p in pending:
                    print(
                        f"[Claim #{p['claim_id']}] Item #{p['item_id']}: {p['item_name']} "
                        f"| Claimant: {p['claimant']} | Submitted: {p['submitted_at']}"
                    )
                    print(f"   Item Desc: {p['item_desc']}")
                    print(f"   Claimant Proof: {p['proof_description']}")
                try:
                    cid = int(input("\nEnter Claim ID to review (0 to cancel): ").strip())
                    if cid != 0:
                        decision = input("Decision ('approved' or 'rejected'): ")
                        review_claim(cid, decision)
                except ValueError:
                    print("Error: Claim ID must be a valid number.")

        elif choice == "7" and user["role"] == "admin":
            display_items(list_items(include_claimed=True))

        elif choice == "0":
            print("Logging out...")
            break

        else:
            print("Invalid option. Please try again.")


def main() -> None:
    """
    Initialize the SQLite database and launch the primary authentication menu.
    """
    init_db()

    while True:
        print("\n=========================================")
        print("   CAMPUS LOST & FOUND VERIFICATION SYSTEM")
        print("=========================================")
        print("1. Register Account")
        print("2. Login")
        print("3. Exit")

        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            print("\n--- Register New Account ---")
            username = input("Choose Username: ")
            password = input("Choose Password: ")
            role = input("Role ('student' or 'admin', default 'student'): ").strip() or "student"
            register_user(username, password, role)

        elif choice == "2":
            print("\n--- User Login ---")
            username = input("Username: ")
            password = input("Password: ")
            user = login_user(username, password)
            if user:
                user_session(user)

        elif choice == "3":
            print("Thank you for using the Campus Lost & Found System. Goodbye!")
            break

        else:
            print("Invalid selection. Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()
