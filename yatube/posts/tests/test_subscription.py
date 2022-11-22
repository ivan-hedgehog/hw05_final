from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from ..models import Group, Post, Follow

User = get_user_model()


class PostSubscriptionTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user3 = User.objects.create_user(username='shelmechina')
        cls.user2 = User.objects.create_user(username='bedolaga')
        cls.user = User.objects.create_user(username='hmiruok')
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
        cls.post2 = Post.objects.create(
            author=cls.user2,
            text='Тестовый пост2',
            group=cls.group
        )
        cls.post3 = Post.objects.create(
            author=cls.user3,
            text='Тестовый пост3',
            group=cls.group
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user2
        )
        cls.follow = Follow.objects.create(
            user=cls.user3,
            author=cls.user
        )

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.user)
        self.not_follower_client = Client()
        self.not_follower_client.force_login(self.user3)
        self.following_client = Client()
        self.following_client.force_login(self.user2)
        cache.clear()

    def test_follow_index_show_correct_post(self):
        """Новая запись пользователя появляется в ленте тех, кто
        на него подписан ."""
        Post.objects.create(
            text='test_new_post',
            author=self.user2
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual('test_new_post', first_object.text)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.user2,
            ).exists())

    def test_follow_index_show_correct_post2(self):
        """Новая запись не появляется в ленте тех, кто не подписан"""
        Post.objects.create(
            text='test_new_post',
            author=self.user2
        )
        response = self.not_follower_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        self.assertNotEqual('test_new_post', first_object.text)

    def test_sub(self):
        """Авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок."""
        check_count = Follow.objects.count()
        self.follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'shelmechina'},
            )
        )
        check_count_1 = Follow.objects.count()
        self.follower_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': 'bedolaga'},
            )
        )
        check_count_2 = Follow.objects.count()
        self.assertNotEqual(check_count, check_count_1)
        self.assertEqual(check_count, check_count_2)
        self.assertNotEqual(check_count_2, check_count_1)
