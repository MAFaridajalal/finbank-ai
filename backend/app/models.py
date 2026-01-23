"""
SQLAlchemy models for FinBank AI banking entities.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CustomerTier(Base):
    """Customer tier levels (Basic, Premium, VIP)."""
    __tablename__ = "customer_tiers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    min_balance = Column(Numeric(15, 2), default=0)
    benefits = Column(String(255))

    customers = relationship("Customer", back_populates="tier")


class Branch(Base):
    """Bank branch locations."""
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    city = Column(String(50))
    manager_name = Column(String(100))

    customers = relationship("Customer", back_populates="branch")


class Customer(Base):
    """Bank customers."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    address = Column(String(255))
    city = Column(String(50))
    tier_id = Column(Integer, ForeignKey("customer_tiers.id"))
    branch_id = Column(Integer, ForeignKey("branches.id"))
    created_at = Column(DateTime, server_default=func.now())

    tier = relationship("CustomerTier", back_populates="customers")
    branch = relationship("Branch", back_populates="customers")
    accounts = relationship("Account", back_populates="customer")
    loans = relationship("Loan", back_populates="customer")


class AccountType(Base):
    """Account types (Checking, Savings, Investment)."""
    __tablename__ = "account_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    interest_rate = Column(Numeric(5, 2), default=0)
    min_balance = Column(Numeric(15, 2), default=0)

    accounts = relationship("Account", back_populates="account_type")


class Account(Base):
    """Customer bank accounts."""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(20), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    type_id = Column(Integer, ForeignKey("account_types.id"))
    balance = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default="active")
    opened_at = Column(DateTime, server_default=func.now())

    customer = relationship("Customer", back_populates="accounts")
    account_type = relationship("AccountType", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", foreign_keys="Transaction.account_id")
    cards = relationship("Card", back_populates="account")


class Transaction(Base):
    """Financial transactions."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(20), unique=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    type = Column(String(20), nullable=False)  # deposit, withdrawal, transfer
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(String(255))
    recipient_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    account = relationship("Account", back_populates="transactions", foreign_keys=[account_id])
    recipient_account = relationship("Account", foreign_keys=[recipient_account_id])


class Loan(Base):
    """Customer loans."""
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    loan_number = Column(String(20), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    type = Column(String(50), nullable=False)  # mortgage, auto, personal
    principal = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2))
    term_months = Column(Integer)
    monthly_payment = Column(Numeric(15, 2))
    remaining_balance = Column(Numeric(15, 2))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())

    customer = relationship("Customer", back_populates="loans")


class Card(Base):
    """Credit and debit cards."""
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String(20), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    type = Column(String(20), nullable=False)  # credit, debit
    credit_limit = Column(Numeric(15, 2))
    expiry_date = Column(Date)
    status = Column(String(20), default="active")

    account = relationship("Account", back_populates="cards")


class ChatSession(Base):
    """AI chat sessions."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    """Chat messages in a session."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String(20))  # user, assistant
    content = Column(Text)
    agents_used = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")
