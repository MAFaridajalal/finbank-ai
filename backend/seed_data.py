"""
Seed data script for FinBank AI.
Populates the database with sample banking data.
"""

from datetime import datetime, timedelta
import random
from decimal import Decimal

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import (
    CustomerTier, Branch, Customer, AccountType, Account,
    Transaction, Loan, Card
)


def seed_database():
    """Seed the database with sample data."""
    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(CustomerTier).count() > 0:
            print("Database already seeded. Skipping...")
            return

        print("Seeding database...")

        # Customer Tiers
        tiers = [
            CustomerTier(name="Basic", min_balance=0, benefits="Standard banking services"),
            CustomerTier(name="Premium", min_balance=10000, benefits="Priority service, lower fees, higher limits"),
            CustomerTier(name="VIP", min_balance=100000, benefits="Dedicated advisor, premium rates, exclusive offers"),
        ]
        db.add_all(tiers)
        db.commit()
        print("Added customer tiers")

        # Branches
        branches = [
            Branch(name="Downtown", address="100 Main Street", city="Seattle", manager_name="Sarah Johnson"),
            Branch(name="Westside", address="500 Oak Avenue", city="Seattle", manager_name="Michael Chen"),
            Branch(name="Airport", address="1200 Airport Way", city="Seattle", manager_name="Emily Davis"),
            Branch(name="Bellevue", address="200 Bellevue Way", city="Bellevue", manager_name="Robert Wilson"),
        ]
        db.add_all(branches)
        db.commit()
        print("Added branches")

        # Account Types
        account_types = [
            AccountType(name="Checking", interest_rate=0.01, min_balance=0),
            AccountType(name="Savings", interest_rate=2.50, min_balance=100),
            AccountType(name="Investment", interest_rate=4.50, min_balance=5000),
            AccountType(name="Money Market", interest_rate=3.50, min_balance=2500),
        ]
        db.add_all(account_types)
        db.commit()
        print("Added account types")

        # Customers
        customers_data = [
            ("John", "Smith", "john.smith@email.com", "555-0101", "123 Pine St", "Seattle", 2, 1),
            ("Sarah", "Johnson", "sarah.j@email.com", "555-0102", "456 Oak Ave", "Seattle", 3, 2),
            ("Michael", "Brown", "m.brown@email.com", "555-0103", "789 Elm St", "Seattle", 1, 3),
            ("Emily", "Davis", "emily.d@email.com", "555-0104", "321 Maple Dr", "Bellevue", 2, 4),
            ("Robert", "Wilson", "r.wilson@email.com", "555-0105", "654 Cedar Ln", "Seattle", 1, 1),
            ("Jennifer", "Taylor", "j.taylor@email.com", "555-0106", "987 Birch Rd", "Seattle", 2, 2),
            ("David", "Anderson", "d.anderson@email.com", "555-0107", "147 Spruce Way", "Bellevue", 3, 4),
            ("Lisa", "Thomas", "l.thomas@email.com", "555-0108", "258 Walnut St", "Seattle", 1, 3),
            ("James", "Jackson", "j.jackson@email.com", "555-0109", "369 Chestnut Ave", "Seattle", 2, 1),
            ("Maria", "Garcia", "m.garcia@email.com", "555-0110", "741 Ash Blvd", "Bellevue", 1, 4),
        ]

        customers = []
        for data in customers_data:
            customer = Customer(
                first_name=data[0],
                last_name=data[1],
                email=data[2],
                phone=data[3],
                address=data[4],
                city=data[5],
                tier_id=data[6],
                branch_id=data[7],
            )
            customers.append(customer)
        db.add_all(customers)
        db.commit()
        print("Added customers")

        # Accounts
        accounts_data = [
            # John Smith - Premium
            ("CHK-001234", 1, 1, 5420.50),
            ("SAV-001234", 1, 2, 25000.00),
            ("INV-001234", 1, 3, 150000.00),
            # Sarah Johnson - VIP
            ("CHK-002345", 2, 1, 12500.00),
            ("SAV-002345", 2, 2, 85000.00),
            ("INV-002345", 2, 3, 500000.00),
            ("MKT-002345", 2, 4, 75000.00),
            # Michael Brown - Basic
            ("CHK-003456", 3, 1, 1200.00),
            ("SAV-003456", 3, 2, 3500.00),
            # Emily Davis - Premium
            ("CHK-004567", 4, 1, 8900.00),
            ("SAV-004567", 4, 2, 45000.00),
            # Robert Wilson - Basic
            ("CHK-005678", 5, 1, 2100.00),
            # Jennifer Taylor - Premium
            ("CHK-006789", 6, 1, 6700.00),
            ("SAV-006789", 6, 2, 32000.00),
            # David Anderson - VIP
            ("CHK-007890", 7, 1, 15000.00),
            ("SAV-007890", 7, 2, 120000.00),
            ("INV-007890", 7, 3, 350000.00),
            # Lisa Thomas - Basic
            ("CHK-008901", 8, 1, 980.00),
            # James Jackson - Premium
            ("CHK-009012", 9, 1, 7500.00),
            ("SAV-009012", 9, 2, 28000.00),
            # Maria Garcia - Basic
            ("CHK-010123", 10, 1, 1850.00),
            ("SAV-010123", 10, 2, 5200.00),
        ]

        accounts = []
        for data in accounts_data:
            account = Account(
                account_number=data[0],
                customer_id=data[1],
                type_id=data[2],
                balance=Decimal(str(data[3])),
                status="active",
            )
            accounts.append(account)
        db.add_all(accounts)
        db.commit()
        print("Added accounts")

        # Transactions
        transaction_types = ["deposit", "withdrawal", "transfer"]
        descriptions = {
            "deposit": ["Payroll deposit", "Wire transfer", "Cash deposit", "Check deposit", "Direct deposit"],
            "withdrawal": ["ATM withdrawal", "Cash withdrawal", "Bill payment", "Online purchase"],
            "transfer": ["To savings", "To checking", "Internal transfer", "Monthly savings"],
        }

        transactions = []
        txn_counter = 1
        for account in accounts:
            # Generate 5-15 transactions per account
            num_transactions = random.randint(5, 15)
            for _ in range(num_transactions):
                txn_type = random.choice(transaction_types)
                amount = Decimal(str(random.randint(50, 5000)))
                desc = random.choice(descriptions[txn_type])
                days_ago = random.randint(0, 90)

                txn = Transaction(
                    transaction_id=f"TXN-{txn_counter:08d}",
                    account_id=account.id,
                    type=txn_type,
                    amount=amount,
                    description=desc,
                    created_at=datetime.now() - timedelta(days=days_ago),
                )
                transactions.append(txn)
                txn_counter += 1
        db.add_all(transactions)
        db.commit()
        print(f"Added {len(transactions)} transactions")

        # Loans
        loans_data = [
            ("LN-001001", 1, "mortgage", 350000, 6.5, 360, 2212.24, 325000),
            ("LN-002001", 2, "auto", 45000, 5.9, 60, 868.14, 38000),
            ("LN-003001", 3, "personal", 10000, 12.0, 36, 332.14, 8500),
            ("LN-004001", 4, "mortgage", 280000, 6.75, 360, 1816.77, 265000),
            ("LN-006001", 6, "auto", 32000, 6.2, 48, 753.82, 24000),
            ("LN-007001", 7, "mortgage", 500000, 6.25, 360, 3078.59, 485000),
            ("LN-007002", 7, "personal", 25000, 10.0, 48, 634.44, 18000),
            ("LN-009001", 9, "auto", 28000, 5.5, 60, 534.45, 22000),
        ]

        loans = []
        for data in loans_data:
            loan = Loan(
                loan_number=data[0],
                customer_id=data[1],
                type=data[2],
                principal=Decimal(str(data[3])),
                interest_rate=Decimal(str(data[4])),
                term_months=data[5],
                monthly_payment=Decimal(str(data[6])),
                remaining_balance=Decimal(str(data[7])),
                status="active",
            )
            loans.append(loan)
        db.add_all(loans)
        db.commit()
        print("Added loans")

        # Cards
        cards_data = [
            ("4532-XXXX-XXXX-1234", 1, "debit", None),
            ("5425-XXXX-XXXX-2345", 1, "credit", 15000),
            ("4532-XXXX-XXXX-3456", 4, "debit", None),
            ("5425-XXXX-XXXX-4567", 4, "credit", 10000),
            ("4532-XXXX-XXXX-5678", 7, "debit", None),
            ("5425-XXXX-XXXX-6789", 7, "credit", 50000),
            ("4532-XXXX-XXXX-7890", 2, "debit", None),
            ("5425-XXXX-XXXX-8901", 2, "credit", 75000),
            ("4532-XXXX-XXXX-9012", 6, "debit", None),
            ("5425-XXXX-XXXX-0123", 9, "credit", 12000),
        ]

        cards = []
        for data in cards_data:
            card = Card(
                card_number=data[0],
                account_id=data[1],
                type=data[2],
                credit_limit=Decimal(str(data[3])) if data[3] else None,
                expiry_date=datetime.now().date() + timedelta(days=random.randint(365, 1095)),
                status="active",
            )
            cards.append(card)
        db.add_all(cards)
        db.commit()
        print("Added cards")

        print("Database seeding complete!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_database()
