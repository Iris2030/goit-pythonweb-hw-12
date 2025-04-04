import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Contact, User
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session(setup_db):

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_contact(db_session):
    contact = Contact(first_name="Mia", last_name="Lee", email="mia@example.com", phone_number="+1234567890", birth_date="2000-01-01")
    db_session.add(contact)
    db_session.commit()

    db_contact = db_session.query(Contact).filter(Contact.email == "mia@example.com").first()
    assert db_contact is not None
    assert db_contact.first_name == "Mia"
    assert db_contact.last_name == "Lee"
    assert db_contact.email == "mia@example.com"
    assert db_contact.phone_number == "+1234567890"
    assert db_contact.birth_date == datetime(2000, 1, 1).date()

def test_update_contact(db_session):
    contact = Contact(first_name="Mia", last_name="Lee", email="mia@example.com", phone_number="+1234567890", birth_date="2000-01-01")
    db_session.add(contact)
    db_session.commit()

    db_contact = db_session.query(Contact).filter(Contact.email == "mia@example.com").first()
    db_contact.first_name = "Mia Updated"
    db_session.commit()

    db_contact_updated = db_session.query(Contact).filter(Contact.email == "mia@example.com").first()
    assert db_contact_updated.first_name == "Mia Updated"

def test_delete_contact(db_session):
    contact = Contact(first_name="Mia", last_name="Lee", email="mia@example.com", phone_number="+1234567890", birth_date="2000-01-01")
    db_session.add(contact)
    db_session.commit()

    db_contact = db_session.query(Contact).filter(Contact.email == "mia@example.com").first()
    db_session.delete(db_contact)
    db_session.commit()

    db_contact_deleted = db_session.query(Contact).filter(Contact.email == "mia@example.com").first()
    assert db_contact_deleted is None


def test_create_user(db_session):
    user = User(username="mia_lee", email="mia_lee@example.com", hashed_password="hashedpassword", avatar="http://example.com/avatar.jpg", is_verified=True)
    db_session.add(user)
    db_session.commit()

    db_user = db_session.query(User).filter(User.email == "mia_lee@example.com").first()
    assert db_user is not None
    assert db_user.username == "mia_lee"
    assert db_user.email == "mia_lee@example.com"
    assert db_user.avatar == "http://example.com/avatar.jpg"
    assert db_user.is_verified is True

def test_update_user(db_session):
    user = User(username="mia_lee", email="mia_lee@example.com", hashed_password="hashedpassword", avatar="http://example.com/avatar.jpg", is_verified=True)
    db_session.add(user)
    db_session.commit()

    db_user = db_session.query(User).filter(User.email == "mia_lee@example.com").first()
    db_user.username = "mia_lee_updated"
    db_session.commit()

    db_user_updated = db_session.query(User).filter(User.email == "mia_lee@example.com").first()
    assert db_user_updated.username == "mia_lee_updated"

def test_delete_user(db_session):
    user = User(username="mia_lee", email="mia_lee@example.com", hashed_password="hashedpassword", avatar="http://example.com/avatar.jpg", is_verified=True)
    db_session.add(user)
    db_session.commit()

    db_user = db_session.query(User).filter(User.email == "mia_lee@example.com").first()
    db_session.delete(db_user)
    db_session.commit()

    db_user_deleted = db_session.query(User).filter(User.email == "mia_lee@example.com").first()
    assert db_user_deleted is None
