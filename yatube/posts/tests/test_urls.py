from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post
from http import HTTPStatus
from django.core.cache import cache


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, 200)


User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def guest_client_urls(self):
        """Страницы доступна любому пользователю."""
        url_names = (
            '/',
            '/group/test-slug/',
            '/profile/auth/',
            '/posts/1/',
        )

        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                error_acces = f'address{address}, dont have access'
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    error_acces
                )

    # Проверяем доступность страниц для авторизованного пользователя
    def test_post_create_url(self):
        """Страница create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем доступность страниц для автора-пользователя
    def test_post_edit_url(self):
        author = User.objects.create_user(username='test')
        post = Post.objects.create(
            author=author,
            text='abc',
            group=self.group
        )
        self.authorized_client.force_login(author)
        response = self.authorized_client.get(f'/posts/{post.id}/edit/')
        self.assertEquals(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы для неавторизованного пользователя
    def test_post_edit_url_redirect_anonymous(self):
        """Страница posts/<int:post_id>/edit/
        перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/posts/1/edit/'))

    def test_post_create_url_redirect_anonymous(self):
        """Страница create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/'))

    def unexisting_page(self):
        """Несуществующая страница."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_404_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        response = self.authorized_client.get('/creato/')
        self.assertTemplateUsed(response, 'core/404.html')
