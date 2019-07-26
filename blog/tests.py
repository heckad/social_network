from django.contrib.auth.models import User
from rest_framework.test import APITestCase

# Create your tests here.
from blog.models import Post, LikeDislike


class TestUserSubsystem(APITestCase):
    def test_user_signup(self):
        res = self.client.post("/api-auth/signup/", {
            "username": "same_user",
            "email": "hello@hello.ru",
            "password": "1234"})
        self.assertEqual(res.status_code, 201)

    def test_user_login(self):
        User.objects.create_superuser('admin', '', '1234')

        res = self.client.post("/api-auth/jwt/", {"username": "admin", "password": "1234"})
        self.assertIn("token", res.json())


class TestPostSubsystem(APITestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create_superuser('admin', '', '1234')
        self.client.force_authenticate(self.admin)

    def test_post_creation(self):
        test_date = {
            "title": "hello world",
            "content": "bla bla"
        }

        self.assertEqual(self.client.post('/posts/', test_date).status_code, 201)

        posts = Post.objects.all()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].content, test_date["content"])


class TestLikeSubsystem(APITestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create_superuser('admin', '', '1234')
        self.post = Post.objects.create(title="hello world",
                                        author=self.admin,
                                        content="bla bla")
        self.client.force_authenticate(self.admin)

    def test_add_like(self):
        test_date = {
            "post": 1,
            "vote": '+'
        }

        self.assertEqual(self.client.post('/likes/', test_date).status_code, 201)

        likes = LikeDislike.objects.all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].post.id, test_date["post"])
        self.assertEqual(likes[0].vote, test_date["vote"])

    def test_double_add_like(self):
        test_data = {
            "post": 1,
            "vote": '+'
        }

        self.assertEqual(self.client.post('/likes/', test_data).status_code, 201)

        likes = LikeDislike.objects.all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].post.id, test_data["post"])
        self.assertEqual(likes[0].vote, test_data["vote"])

        self.assertEqual(self.client.post('/likes/', test_data).status_code, 201)

        likes = LikeDislike.objects.all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].post.id, test_data["post"])
        self.assertEqual(likes[0].vote, test_data["vote"])

    def test_remove_like(self):
        l = LikeDislike.objects.create(user=self.admin, post=self.post, vote=1)

        self.assertEqual(self.client.delete('/likes/{}/'.format(l.id)).status_code, 204)

        self.assertEqual(LikeDislike.objects.count(), 0)
