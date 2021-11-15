# '에어비앤비' 웹사이트 구현 프로젝트

## 프로젝트 설명
- '에어비앤비' 커머스 사이트를 모티브로 하여 기능 구현 하였습니다.
- 프로젝트 초기 단계부터 팀원과 협의하여 기획하였습니다.
- 모든 기능은 직접 구현하였습니다.

## 구현한 기능
- **Social 로그인** (내가 구현한 기능)
    - 회원가입 : Social login 카카오, 구글 API를 이용하여 회원가입 기능 구현 
    - 로그인 : Social login 카카오, 구글 API를 이용하여 회원가입 기능 구현
    - 로그아웃 : 카카오 API를 활용하여 기능 구현 
    - Decorator를 활용한 회원 인증 여부 기능 구현
    - JWT를 이용하여 로그인 기능 구현
    - Social API 관련하여 모듈화
- **숙소**
    - 검색어 리스트
    - 숙소 리스트 조회
    - 숙소 상세
    - 숙소 댓글
    - 숙소 항목별 평점 조회
- **위시리스트(rooms)**
    - 위시리스트 조회, 삭제, 추가
- **예약**
    - 예약 & 수정

## 프로젝트 환경
- Python 3.8
- Django 3.2
- MySQL

## 백엔드 사용기술
- Python
- Django
- MySQL
- JWT

## 프로젝트 형상관리 tool
- Git(Github)

## 협업 tool
- trello
- slack

## 프로젝트 사용법
1. Git repository 에서 clone을 받습니다.
<a href="https://github.com/SSABOODA/21-2nd-GroundBnB-backend">프로젝트 Github 링크</a>

```
$ git clone https://github.com/SSABOODA/21-2nd-GroundBnB-backend.git
```

## 백엔드 API 명세
<a href="https://trello.com/b/0U1JaFTF/ground-bnb">백엔드 API 명세</a>

## ERD (modeling)
![groundbnb erd](https://user-images.githubusercontent.com/69753846/129717794-83eba5db-ef72-47c2-b6b7-c773f671598a.png)



## 프로젝트 구조
```
├── groundbnb
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── local.py
│   │   ├── prod.py
│   │   └── test.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── my_settings.py
├── requirements.txt
├── rooms
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   ├── models.py
│   ├── tests.py
│   ├── urls
│   │   ├── rooms_urls.py
│   │   └── wishes_urls.py
│   └── views.py
└── users
    ├── admin.py
    ├── apps.py
    ├── migrations
    ├── models.py
    ├── tests.py
    ├── urls.py
    ├── utils.py
    └── views.py
```
- groundbnb : 프로젝트 이름입니다.(최상위 폴더)
    - groundbnb/settings.py : 프로젝트의 기반이 되는 파일들이 설정되어있습니다.(공통/개발환경/배포환경으로 나누어져있습니다)
- my_settings.py : github에 push되면 안되는 내용들이 있습니다. (DATABASE 설정, SECERT_KEY, ALGORITHM)
- requirements.txt : 프로젝트를 실행하기 위해 가상환경에 설치해줘야 할 프레임워크, 라이브러리 목록입니다. ex)django, mysqlclient...
- rooms : 숙소 예약, 검색, 조회, 숙소 정보 상세, 댓글, 평점 등 모든 숙소 관련 API를 구현하기 위한 프로젝트 app 폴더입니다.
- users : User 회원가입, 로그인, 회원인증 관련 데이코레이터 API를 구현하기 위한 프로젝트 app 폴더입니다.



