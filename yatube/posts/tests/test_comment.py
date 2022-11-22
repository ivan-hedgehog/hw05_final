from django.contrib.auth import get_user_model
from posts.forms import PostForm
from posts.models import Post
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Group, Post, Comment
from http import HTTPStatus
from django.core.cache import cache


User = get_user_model()


class PostCreateFormTests(TestCase):
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
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий',
            post=cls.post
        )
        cls.form = PostForm()
        # Создаем форму, если нужна проверка атрибутов

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_no_edit_post(self):
        '''Проверка запрета написания коммента
        не авторизованного пользователя'''
        comment_count = Comment.objects.count()
        form_data = {'text': 'Тестовый комментарий',
                     'post': self.post.id}
        response = self.guest_client.post(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name2 = 'Коммент добавлен в базу данных по ошибке'
        self.assertNotEqual(Comment.objects.count(),
                            comment_count + 1,
                            error_name2)

    def test_comment_added_correctly(self):
        """коммент при создании добавлен корректно"""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id})
        )
        post_detail = response.context['comments']
        self.assertIn(self.comment, post_detail, 'коммента нет')

    def test_create_post(self):
        """Валидная форма создает запись в коммент."""
        comment_count = Comment.objects.count()
        form_data = {'text': 'Тестовый комментарий',
                     'post': self.post.id}
        self.guest_client.post(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                text='Тестовый комментарий',
                post=self.post
            ).exists()
        )
