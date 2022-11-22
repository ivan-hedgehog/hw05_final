from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from ..models import Group, Post

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user2 = User.objects.create_user(username='bedolaga')
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'}):
                        'posts/post_detail.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
                'posts/profile.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': '1'}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_creat_show_correct_context(self):
        """Шаблон creat сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон creat сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id': '1'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        # что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_detail_page_show_correct_context_1(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_object = response.context['post']
        author_0 = first_object.author.username
        text_0 = first_object.text
        group_0 = first_object.group
        self.assertEqual(author_0, 'auth')
        self.assertEqual(text_0, 'Тестовый пост')
        self.assertEqual(group_0, self.group)

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Тестовый текст проверка как добавился',
            author=self.user,
            group=self.group)
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index, 'поста нет на главной')
        self.assertIn(post, group, 'поста нет в профиле')
        self.assertIn(post, profile, 'поста нет в группе')

    def test_post_added_correctly_user2(self):
        """Пост при создании не добавляется другому пользователю
           Но виден на главной и в группе"""
        group2 = Group.objects.create(title='Тестовая группа 2',
                                      slug='test_group2')
        posts_count = Post.objects.filter(group=self.group).count()
        post = Post.objects.create(
            text='Тестовый пост от другого автора',
            author=self.user2,
            group=group2)
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        group = Post.objects.filter(group=self.group).count()
        profile = response_profile.context['page_obj']
        self.assertEqual(group, posts_count, 'поста нет в другой группе')
        self.assertNotIn(post, profile,
                         'поста нет в группе другого пользователя')

    def assistant_test_page_show_correct_context(self, first_object):
        author_0 = first_object.author.username
        text_0 = first_object.text
        group_0 = first_object.group
        self.assertEqual(author_0, self.user.username)
        self.assertEqual(text_0, 'Тестовый пост')
        self.assertEqual(group_0, self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'})
        )
        first_object = response.context['post']
        self.assistant_test_page_show_correct_context(first_object)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assistant_test_page_show_correct_context(first_object)

    def test_group_list_page_show_correct_context(self):
        """Шаблон post_list сформирован с правильным контекстом."""
        group2 = Group.objects.create(title='Тестовая группа 2',
                                      slug='test_group2')
        Post.objects.create(
            text='Тестовый пост от другого автора',
            author=self.user2,
            group=group2)
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test_group2'})
        )
        first_object = response.context['page_obj'][0]
        author_0 = first_object.author.username
        text_0 = first_object.text
        group_0 = first_object.group
        self.assertEqual(author_0, 'bedolaga')
        self.assertEqual(text_0, 'Тестовый пост от другого автора')
        self.assertEqual(group_0, group2)
