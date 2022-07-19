from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

class TestView(TestCase):
    def setUp(self):
        # 테스트를 위한 가상의 사용자
        self.client = Client()

    def test_post_list(self):
        # 포스트 목록을 가져옴
        # 사용자가 127.0.0.1:8000/blog/ 에 접근하는 상황을 가정, 이를 response에 저장
        response = self.client.get('/blog/')

        # 페이지가 정상적으로 로드 되었는지 확인
        # 성공적인 결과를 돌려줄 때 코드 200를 반환함
        self.assertEqual(response.status_code, 200)

        # 페이지 타이틀이 Blog인지 확인
        # HTML 요소에 접근하기 쉽게 하기 위해 Beautifulsoup 으로 읽어옴
        # html.parser 명령어로 파싱한 결과를 soup에 담음.
        # 그 후 텍스트만 가져와서 텍스트가 Blog 인지 확인
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')

        # 네비게이션 바를 가져옴
        navbar = soup.nav
        # 네비게이션 바 안의 컨텐츠 들을 확인한다
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        # 작성된 포스트가 0개 인지 확인
        # 테스트 시작시 테스트용 데이터 베이스를 생성함, 단 setUp() 함수 에서 설정한 요소는 포함 시킴
        # 그런데 setUp() 함수에서 데이터베이스 관련 조작을 하지 않았으므로 DB 에는 아무것도 없음
        self.assertEqual(Post.objects.count(), 0)

        # main area 에 아직 게시물이 없습니다 라는 문구가 나타남
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)
        
        # 포스트가 두 개 있다면
        post_001 = Post.objects.create(
            title='첫 번째 포스트 입니다.',
            content='Heeeeellllloooooo World',
        )
        post_002 = Post.objects.create(
            title='두 번째 포스트 입니다.',
            content='Byeeeeeeee Worrrrrllllldddddd',
        )
        self.assertEqual(Post.objects.count(), 2)

        # 포스트 목록 페이지를 새로고침 했을 때를 확인
        # 페이지를 새로고침하는 코드임
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        # main area에 포스트 2개의 제목이 존재함을 확인
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        # 게시물이 2개 존재하므로 아직 게시물이 없습니다 라는 문구가 나타나지 않음
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)