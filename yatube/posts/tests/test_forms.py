import tempfile
import shutil

from django.contrib.auth import get_user_model
from posts.forms import PostForm
from posts.models import Post
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Group, Post
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый пост',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text='Тестовый пост',
                author=self.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_post_edit_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый пост',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text='Тестовый пост',
                author=self.user,
            ).exists()
        )
