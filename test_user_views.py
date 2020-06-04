"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

# os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler_test'

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
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

    def test_list_users(self):
        """Testing if list of all users shows"""

        with self.client as c:
            resp = c.get("/users")        
            html = resp.get_data(as_text=True)   

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)

    def test_users_show(self):
        """Testing if user profile page displays"""

        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", html)

    def test_show_following(self):
        """Testing if current user can view who user follows"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
            user = User.query.filter_by(username="testuser2").first()
        
            self.testuser.following.append(user)
            db.session.commit()

            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(self.testuser.is_following(user))
            self.assertIn('<h4 id="sidebar-username">@testuser</h4>', html)
            self.assertIn("testuser2", html)

    def test_show_following_other(self):
        """Testing if logged in user can view who other user follows"""  

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
            user = User.query.filter_by(username="testuser2").first()
        
            user.following.append(self.testuser)
            db.session.commit()

            resp = c.get(f"/users/{user.id}/following", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(user.is_following(self.testuser))
            self.assertIn("@testuser", html)
            self.assertIn('<h4 id="sidebar-username">@testuser2</h4>', html)

    def test_show_followers(self):
        """Testing if current user can view followers"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
            user = User.query.filter_by(username="testuser2").first()
        
            self.testuser.followers.append(user)
            db.session.commit()

            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(self.testuser.is_followed_by(user))
            self.assertIn('<h4 id="sidebar-username">@testuser</h4>', html)
            self.assertIn("testuser2", html)

    def test_show_followers_other(self):
        """Testing if logged in user can view other user's followers"""  

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
            user = User.query.filter_by(username="testuser2").first()
        
            user.followers.append(self.testuser)
            db.session.commit()

            resp = c.get(f"/users/{user.id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(user.is_followed_by(self.testuser))
            self.assertIn("@testuser", html)
            self.assertIn('<h4 id="sidebar-username">@testuser2</h4>', html)                

    def test_show_following_logged_out(self):
        """Testing that user is prohibited from viewing who user follows"""

        with self.client as c:
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
            user = User.query.filter_by(username="testuser2").first()
        
            user.following.append(self.testuser)
            db.session.commit()

            resp = c.get(f"/users/{user.id}/following", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)

    def test_show_followers_logged_out(self):
        """Testing that user is prohibited from viewing who user follows"""

        with self.client as c:
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
            user = User.query.filter_by(username="testuser2").first()
        
            user.followers.append(self.testuser)
            db.session.commit()

            resp = c.get(f"/users/{user.id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)

    def test_users_likes(self):
        """Testing view of user likes"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

                
            db.session.add_all([user2, self.testuser])
            user = User.query.filter_by(username="testuser2").first()
            message = Message(text="testing",
                              user_id=user.id)

            db.session.add(message)
            get_message = Message.query.filter_by(user_id=user.id).first()                  
            self.testuser.likes.append(get_message)
            db.session.commit()

            resp = c.get(f"/users/{self.testuser.id}/likes", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">@testuser</h4>', html)
            self.assertIn("testing", html)
            self.assertIn("@testuser2", html)
    
    def test__other_users_likes(self):
        """Testing view of other user's likes"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
            user = User.query.filter_by(username="testuser2").first()
            message = Message(text="testing2",
                              user_id=self.testuser.id)

            db.session.add(message)
            get_message = Message.query.filter_by(user_id=self.testuser.id).first()                  
            user.likes.append(get_message)
            db.session.commit()

            resp = c.get(f"/users/{user.id}/likes", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">@testuser2</h4>', html)
            self.assertIn("testing2", html)
            self.assertIn("@testuser", html)

    def test_add_like(self):
        """Testing if like click is added and displayed on user likes page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
            user = User.query.filter_by(username="testuser2").first()
            message = Message(text="testing2",
                              user_id=user.id)

            db.session.add(message)
            get_message = Message.query.filter_by(user_id=user.id).first()                  

            db.session.commit()
            data = {"page": f"/users/{self.testuser.id}/likes"}
            resp = c.post(f"/users/add_like/{get_message.id}", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">@testuser</h4>', html)
            self.assertIn("testing2", html)
            self.assertIn("@testuser2", html)
    
    def test_add_like(self):
        """Testing if like click is deleted and removed from user likes page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
            user = User.query.filter_by(username="testuser2").first()
            message = Message(text="testing2",
                              user_id=user.id)

            db.session.add(message)
            get_message = Message.query.filter_by(user_id=user.id).first()                  
            self.testuser.likes.append(get_message)    

            db.session.commit()
            data = {"page": f"/users/{self.testuser.id}/likes"}
            resp = c.post(f"/users/add_like/{get_message.id}", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">@testuser</h4>', html)
            self.assertNotIn("testing2", html)
            self.assertNotIn("@testuser2", html)

    def test_add_like_unauthorized(self):
        """Testing if logged out user is unauthorized from liking"""

        with self.client as c:
            data = {"page": f"/users/{self.testuser.id}/likes"}
            resp = c.post(f"/users/add_like/1", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)

    def test_add_follow(self):
        """Testing if logged in user can add follow"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
     
            user = User.query.filter_by(username="testuser2").first()  
            db.session.commit()
        
            resp = c.post(f"/users/follow/{user.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
     
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">@testuser</h4>', html)
            self.assertIn("@testuser2", html)  

    def test_add_follow_unauthorized(self):
        """Testing if logged out user is prohibited from following"""

        with self.client as c:
            
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
     
            user = User.query.filter_by(username="testuser2").first()  
            db.session.commit()
        
            resp = c.post(f"/users/follow/{user.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
     
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)

    def test_stop_following(self):
        """Testing user unfollowing"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(username="testuser2",
                         email="test2@test.com",
                         password="testuser2",
                        )

            db.session.add_all([user2, self.testuser])
     
            user = User.query.filter_by(username="testuser2").first()  
            db.session.commit()
            self.testuser.following.append(user)
        
            resp = c.post(f"/users/stop-following/{user.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
        
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h4 id="sidebar-username">@testuser</h4>', html)
            self.assertNotIn("@testuser2", html)

    def test_show_profile(self):
        """Testing display of edit profile page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
            resp = c.get(f"/users/profile", follow_redirects=True)
            html = resp.get_data(as_text=True)
        
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit Your Profile', html)

    def test_edit_profile(self):
        """Testing if user profile is updated and redirected"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
            data = {"username": "othertestuser",
                    "email": "test@test.com",
                    "bio": "Check out my story",
                    "password": "testuser"}

            resp = c.post(f"/users/profile", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
        
            self.assertEqual(resp.status_code, 200)
            self.assertIn('@othertestuser', html)
            self.assertIn('Check out my story', html)

    def test_edit_profile_unauthorized(self):
        """Testing if logged user is prohibited from editing profile"""

        with self.client as c:
        
            data = {"username": "othertestuser",
                    "email": "test@test.com",
                    "bio": "Check out my story",
                    "password": "testuser"}

            resp = c.post(f"/users/profile", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
        
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized', html) 

    def test_delete_user(self):
        """Testing user delete"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
        
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(User.query.all(), [])
            self.assertIn('Join Warbler today', html)
            self.assertIn('Sign me up!', html)

    def test_delete_user_unauthorized(self):
        """Testing prohibition of logged out user to delete"""

        with self.client as c:

            resp = c.post(f"/users/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
        
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)