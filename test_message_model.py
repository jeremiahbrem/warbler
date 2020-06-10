import os
from unittest import TestCase
from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError
from datetime import datetime

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        self.client = app.test_client()
        self.user = User.query.filter_by(username="testuser").first()

    def tearDown(self):

        db.session.rollback()    

    def test_message_model(self):
        """Does basic model work?"""
        
        user = User.query.get(self.user.id)
        m = Message(
            text="This a test.",
            user_id=user.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertIsInstance(m, Message)
        self.assertEqual(m.user, user)
        self.assertIn(m, user.messages)
        self.assertEqual(m.text, "This a test.") 
        self.assertEqual(m.user_id, self.user.id)
        self.assertIsInstance(m.timestamp, datetime)  

    def test_invalid_message_text(self):
        """Testing invalid message text parameter"""

        with self.assertRaises(IntegrityError):
            m2 = Message(
                text= None,
                user_id=1
            )

            db.session.add(m2)
            db.session.commit()

    def test_invalid_message_user_id(self):
        """Testing invalid message user_id parameter"""        
        
        with self.assertRaises(IntegrityError):
            m3 = Message(
                text= "Testing",
                user_id=None
            )

            db.session.add(m3)
            db.session.commit()