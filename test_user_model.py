"""User model tests."""

import os
from unittest import TestCase
from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):

        db.session.rollback()    

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test__repr__(self):
        """Testing User __repr__ method"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        
        db.session.add(u)
        db.session.commit()
        user = User.query.first()

        self.assertEqual(f"{user}", f"<User #{user.id}: testuser, test@test.com>")

    def test_is_followed_by(self):
        """Testing User if_followed_by method"""

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        
        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        
        db.session.add_all([user1, user2])
        db.session.commit()
        user1 = User.query.filter_by(username="testuser").first()
        user2 = User.query.filter_by(username="testuser2").first()
        user1.followers.append(user2)
        db.sesson.commit()
        self.assertTrue(user1.is_followed_by(user2)) 

    def test_is_followed_by(self):
        """Testing User if_followed_by method"""

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        
        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        
        db.session.add_all([user1, user2])
        db.session.commit()

        user1 = User.query.filter_by(username="testuser").first()
        user2 = User.query.filter_by(username="testuser2").first()
        
        user1.followers.append(user2)
        db.session.commit()    
        self.assertTrue(user1.is_followed_by(user2))
        
        user1.followers.remove(user2)
        db.session.commit()
        self.assertFalse(user1.is_followed_by(user2))

    def test_is_following(self):
        """Testing User if_followed_by method"""

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        
        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        
        db.session.add_all([user1, user2])
        db.session.commit()
        
        user1 = User.query.filter_by(username="testuser").first()
        user2 = User.query.filter_by(username="testuser2").first()
        
        user1.followers.append(user2)
        db.session.commit()
        
        self.assertTrue(user2.is_following(user1))
        user1.followers.remove(user2)
        
        db.session.commit()
        self.assertFalse(user2.is_following(user1))

    def test_signup(self):
        """Testing User signup method"""

        user = User.signup(
            username="testuser",
            email="test@test.com",
            password="testpassword",
            image_url="http://test.jpg"
        )
        db.session.commit()
        self.assertIsInstance(user, User)

        with self.assertRaises(IntegrityError):
            user = User.signup(
                username="",
                email="test@test.com",
                password="testpassword",
                image_url="http://test.jpg"
                )   
            db.session.commit() 

    def test_authenticate(self):
        """Testing User authenticate method"""

        user = User.signup(
            username="testuser",
            email="test@test.com",
            password="testpassword",
            image_url="http://test.jpg"
        )
        db.session.commit()
        user = User.authenticate("testuser", "testpassword")
        self.assertIsInstance(user, User)
        
        user2 = User.authenticate("tsgvsett", "testpassword")
        self.assertIs(user2)

        user3 = User.authenticate("testuser", "sdfdsafdsg")
        self.assertFalse(user3)    