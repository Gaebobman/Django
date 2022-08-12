from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag


class TestView(TestCase):
    def setUp(self):
        # 테스트를 위한 가상의 사용자
        self.client = Client()
        self.user_naver = User.objects.create_user(username='naver', password='passwooord')
        self.user_kakao = User.objects.create_user(username='kakao', password='passwooord')

        self.category_law = Category.objects.create(name='law', slug='law')
        self.category_engineering = Category.objects.create(name='engineering', slug='engineering')

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트 입니다.',
            content='Heeeeellllloooooo World',
            category=self.category_law,
            author=self.user_naver
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트 입니다.',
            content='Byeeeeeeee Worrrrrllllldddddd',
            category=self.category_engineering,
            author=self.user_kakao
        )
        self.post_003 = Post.objects.create(
            title='세 번째 포스트 입니다.',
            content='Byeeeeeeee Worrrrrllllldddddd',
            author=self.user_kakao
        )
        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)

    def navbar_test(self, soup):
        # 네비게이션 바를 가져옴
        navbar = soup.nav
        # 네비게이션 바 안의 컨텐츠 들을 확인한다
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        # 버튼 클릭시 의도한 페이지로 이동하는가?
        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_law.name} ({self.category_law.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_engineering.name} ({self.category_engineering.post_set.count()})',
                      categories_card.text)
        self.assertIn(f'미분류 ({Post.objects.filter(category=None).count()})', categories_card.text)

    def test_post_list(self):
        # 포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(), post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
        # 1.1 포스트가 하나 있음
        post_000 = Post.objects.create(
            title='첫 번째 포스트 입니다.',
            content='Heeeeellllloooooo World',
            author=self.user_naver,
        )
        # 1.2 포스트의 url은 /blog/1/ 임.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1')
        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2.1. 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다. (Code:200)
        response = self.client.get(self.post_001.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2. 네비게이션 바 테스트
        self.navbar_test(soup)

        self.category_card_test(soup)

        # 2.3. 첫 번째 포스트의 제목이 타이틀
        self.assertIn(self.post_001.title, soup.title.text)

        # 2.4. 포스트 영역에 제목이 있음
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_law.name, post_area.text)

        # 2.5. 작성자가 포스트 영역에 있음
        self.assertIn(self.user_naver.username.upper(), post_area.text)
        # 2.6. 포스트의 내용이 포스트 영역에 있음
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_law.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_law.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_law.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        # 로그인 하지 않은 상태 로는 글쓰기 접근 불가능 해야 함 (Status Code Not equal to 200)
        response = self.client.get('/blog/create_post/', follow=True)
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='naver', password='passwooord')

        response = self.client.get('/blog/create_post/', follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)
        
        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': "Post Form 페이지를 만듭시다.",
            }
        )
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username,'naver')
