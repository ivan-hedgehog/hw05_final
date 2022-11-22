from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group
from django.core.cache import cache

TEST_OF_POST: int = 13
User = get_user_model()


class PaginatorViewsTest(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        bilk_post: list = []
        for i in range(TEST_OF_POST):
            bilk_post.append(Post(text=f'Тестовый текст {i}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(bilk_post)
        cache.clear()

    def assistant_test_first_page_contains_ten_records(self, args):
        response = self.client.get(args)
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get((args) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_contains_ten_records(self):
        pages: tuple = (reverse('posts:index'),
                        reverse('posts:profile',
                                kwargs={'username': f'{self.user.username}'}),
                        reverse('posts:group_list',
                                kwargs={'slug': f'{self.group.slug}'}))
        for page in pages:
            self.assistant_test_first_page_contains_ten_records(page)
