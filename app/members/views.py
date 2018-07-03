import json

import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.shortcuts import render, redirect

from .forms import SignupForm

# User클래스 자체를 가져올때는 get_user_model()
# ForeignKey에 User모델을 지정할때는 settings.AUTH_USER_MODEL
User = get_user_model()


def login_view(request):
    # 1. POST요청이 왔는데, 요청이 올바르면서 <- 코드에서 어느 위치인지 파악
    # 2.  GET paramter에 'next'값이 존재할 경우 <-- GET parameter는 request.GET으로 접근
    # 3.  해당 값(URL)으로 redirect <- redirect()함수는 URL문자열로도 이동 가능
    # 4.  next값이 존재하지 않으면 원래 이동하던 곳으로 그대로 redirect <- 문자열이 있는지 없는지는 if로 판단

    # 1. member.urls <- 'members/'로 include되도록 config.urls모듈에 추가
    # 2. path구현 (URL: '/members/login/')
    # 3. path와 이 view연결
    # 4. 일단 잘 나오는지 확인
    # 5. 잘 나오면 form을 작성 (username, password를 받는 input2개)
    #   templates/members/login.html에 작성

    # 6. form작성후에는 POST방식 요청을 보내서 이 뷰에서 request.POST에 요청이 잘 왔는지 확인
    # 7. 일단은 받은 username, password값을 HttpResponse에 보여주도록 한다.
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(request.user.is_authenticated)
        # 받은 username과 password에 해당하는 User가 있는지 인증
        user = authenticate(request, username=username, password=password)

        # 인증에 성공한 경우
        if user is not None:
            # 세션값을 만들어 DB에 저장하고, HTTP response의 Cookie에 해당값을 담아보내도록 하는
            # login()함수를 실행한다

            # session_id값을 django_sessions테이블에 저장, 데이터는 user와 연결됨
            # 이 함수 실행 후 돌려줄 HTTP Response에는 Set-Cookie헤더를 추가, 내용은 sessionid=<session값>
            login(request, user)
            print(request.GET)

            # GET parameter에 'next'값이 전달되면 해당 값으로 redirect
            next = request.GET.get('next')
            if next:
                return redirect(next)
            # next값이 전달되지 않았으면 post-list로 redirect
            return redirect('posts:post-list')

        # 인증에 실패한 경우 (username또는 password가 틀린 경우)
        else:
            # 다시 로그인 페이지로 redirect
            return redirect('members:login')
    # GET 요청일 경우
    else:
        # form이 있는 template을 보여준다
        return render(request, 'members/login.html')


def logout_view(request):
    logout(request)
    return redirect('index')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.signup()
            login(request, user)
            return redirect('index')
    else:
        form = SignupForm()

    context = {
        'form': form,
    }
    return render(request, 'members/signup.html', context)


def signup_bak(request):
    context = {
        'errors': [],
    }
    if request.method == 'POST':
        # username, email, password, password2에 대해서
        # 입력되지 않은 필드에 대한 오류를 추가
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # 반드시 내용이 채워져야 하는 form의 필드 (위 변수명)
        # hint: required_fields를 dict로
        # required_fields = ['username', 'email', 'password', 'password2']
        required_fields = {
            'username': {
                'verbose_name': '아이디',
            },
            'email': {
                'verbose_name': '이메일',
            },
            'password': {
                'verbose_name': '비밀번호',
            },
            'password2': {
                'verbose_name': '비밀번호 확인',
            },
        }
        for field_name in required_fields.keys():
            if not locals()[field_name]:
                context['errors'].append('{}을(를) 채워주세요'.format(
                    required_fields[field_name]['verbose_name'],
                ))

        # 입력데이터 채워넣기
        context['username'] = username
        context['email'] = email

        # form에서 전송된 데이터들이 올바른지 검사
        if User.objects.filter(username=username).exists():
            context['errors'].append('유저가 이미 존재함')
        if password != password2:
            context['errors'].append('패스워드가 일치하지 않음')

        # errors가 없으면 유저 생성 루틴 실행
        if not context['errors']:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
            )
            login(request, user)
            return redirect('index')
    return render(request, 'members/signup.html', context)


def follow_toggle(request):
    """
    * GET요청은 처리하지 않음
    * 로그인 된 상태에서만 작동

    POST요청일 때
        1. request.POST로 'user_pk'값을 전달받음
            pk가 user_pk인 User를 user에 할당
        2. request.user의 
    :param request:
    :return:
    """


def facebook_login(request):
    def get_access_token(code):
        """
        Authorization code를 사용해 액세스 토큰을 받아옴
        :param code: 유저의 페이스북 인증 후 전달되는 Authorization code
        :return: 액세스 토큰 문자열
        """
        # GET parameter의 'code'에 값이 전달됨 (authentication code)
        # 전달받은 인증코드를 사용해서 액세스토큰을 받음
        url = 'https://graph.facebook.com/v3.0/oauth/access_token'
        params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'redirect_uri': 'http://localhost:8000/members/facebook-login/',
            'client_secret': settings.FACEBOOK_APP_SECRET_CODE,
            'code': code,
        }
        response = requests.get(url, params)
        # 파이썬에 내장된 json모듈을 사용해서, JSON형식의 텍스트를 파이썬 Object로 변환
        response_dict = json.loads(response.text)
        # 위와 같은 결과
        response_dict = response.json()
        access_token = response_dict['access_token']
        return access_token

    def debug_token(token):
        """
        주어진 token을 Facebook의 debug_token API Endpoint를 사용해 검사
        :param token: 액세스 토큰
        :return: JSON응답을 파싱한 파이썬 Object
        """
        # 받은 액세스 토큰을 debug
        # 결과에서 해당 토큰의 user_id(사용자 고유값)를 가져올 수 있음
        url = 'https://graph.facebook.com/debug_token'
        params = {
            'input_token': token,
            'access_token': '{}|{}'.format(
                settings.FACEBOOK_APP_ID,
                settings.FACEBOOK_APP_SECRET_CODE,
            )
        }
        response = requests.get(url, params)
        return response.json()

    def get_user_info(token, fields=('id', 'name', 'first_name', 'last_name', 'picture')):
        """
        주어진 token에 해당하는 Facebook User의 정보를 리턴
        'id,name,first_name,last_name,picture'
        :param token: Facebook User토큰
        :param fields: join()을 사용해 문자열을 만들 Sequence객체
        :return: JSON응답을 파싱한 파이썬 Object
        """
        # GraphAPI의 'me'(User)를 이용해서 Facebook User정보 받아오기
        url = 'https://graph.facebook.com/v3.0/me'
        params = {
            'fields': ','.join(fields),
            # 'fields': 'id,name,first_name,last_name,picture',
            'access_token': token,
        }
        response = requests.get(url, params)
        return response.json()

    def create_user_from_facebook_user_info(user_info):
        """
        Facebook GraphAPI의 'User'에 해당하는 응답인 user_info로부터
        id, first_name, last_name, picture항목을 사용해서
        Django의 User를 가져오거나 없는경우 새로 만듬 (get_or_create)
        :param user_info: Facebook GraphAPI - User의 응답
        :return: get_or_create의 결과 tuple (User instance, Bool(created))
        """
        # 받아온 정보 중 회원가입에 필요한 요소들 꺼내기
        facebook_user_id = user_info['id']
        first_name = user_info['first_name']
        last_name = user_info['last_name']
        url_img_profile = user_info['picture']['data']['url']

        # facebook_user_id가 username인 User를 기준으로 가져오거나 새로 생성
        return User.objects.get_or_create(
            username=facebook_user_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
            },
        )

    code = request.GET.get('code')
    access_token = get_access_token(code)
    user_info = get_user_info(access_token)
    user, user_created = create_user_from_facebook_user_info(user_info)

    # 생성한 유저로 로그인
    login(request, user)
    return redirect('index')
