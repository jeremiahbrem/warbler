"""Message View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
            self.assertIn("Hello", html)
            self.assertIn(self.testuser.username, html)

    def test_add_message_not_user(self):
        """Testing new message attempt without logged in user"""

        with self.client as c:
            resp = c.get("/messages/new", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_show_add_message(self):
        """Testing display of add message form"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/messages/new", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Add my message!", html)

    def test_messages_show(self):
        """Testing display of single message"""

        with self.client as c:
            m = Message(text="Testing", user_id=self.testuser.id)
            db.session.add(m)
            db.session.commit()
            message = Message.query.one()
            
            resp = c.get(f"/messages/{message.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Testing", html)
            self.assertIn("testuser", html)

    def test_messages_destroy(self):
        """Testing message deletion"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(text="Testing", user_id=self.testuser.id)
            db.session.add(m)
            db.session.commit()
            message = Message.query.one()  

            resp = c.post(f"/messages/{message.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)
            self.assertNotIn("Testing", html)
            self.assertEqual(Message.query.all(), [])

    def test_messages_destroy_unauthorized(self):
        """Testing unauthorized access of message delete"""

        with self.client as c:
            m = Message(text="Testing", user_id=self.testuser.id)
            db.session.add(m)
            db.session.commit()
            message = Message.query.one()

            resp = c.post(f"/messages/{message.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)


                    