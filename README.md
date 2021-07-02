## CATCH FABRIC 프로젝트 Front-end/Back-end 소개

- 세계 최대 숙소 예약 포털 사이트 [에어비앤비](https://www.airbnb.co.kr/) 클론 프로젝트

- 짧은 프로젝트 기간동안 개발에 집중해야 하므로 디자인/기획 부분만 클론하였으며, 저희의 아이디어가 담기도록 원단 판매 사이트로 변경하였습니다.

- 개발은 초기 세팅부터 전부 직접 구현했으며, 아래 데모 영상에서 보이는 부분은 모두 백앤드와 연결하여 실제 사용할 수 있는 서비스 수준으로 개발한 것입니다.

### 개발 인원 및 기간

- 개발기간 : 2021/6/21 ~ 2021/7/2
- 개발 인원
  - 프론트엔드
    - 백진수
    - 박현찬
  - 백엔드
    - 유병건
    - 황복실
    - 한성봉
 
- GitHub
  - [프론트엔드 GitHub URL](https://github.com/wecode-bootcamp-korea/21-2nd-GroundBnB-frontend.git)
  - [백엔드 GitHub URL](https://github.com/wecode-bootcamp-korea/21-2nd-GroundBnB-backend.git)

### 프로젝트 선정이유

- Google Map Api를 활용한 여러 사이트 중, 에어비앤비의 Google Map 기능을 클론해보고 싶었습니다.
- 일반적인 커머스 사이트와는 다른 다소 복잡해 보이는 모델링과 다양한 기능(예약기능, 댓글기능, 소셜로그인 등등)이 적절하게 조합이 되어져 있어서 선정하게 되었습니다.

### 데모 영상

## 적용 기술 및 구현 기능

### 적용 기술

> - Front-End : React.js, StyledComponent, html, JavaScript, 
> - Back-End  : Python, Django web framework, Bcrypt, JWT, My SQL, Redis
> - Common    : AWS(EC2, RDS, S3, Docker), RESTful API

### 협업 Tool
> trello, slack

### 구현 기능
#### 메인페이지
 - 검색(연관 검색어), Calendar

#### 회원가입 / 로그인
 - Kakao Social Login

#### 검색 결과 페이지
 - Google Map Api를 활용한 숙소 리스트

#### 상세 페이지
 - 숙소 평점별 표시
 - 예약하기
 - 댓글

## Reference
- 이 프로젝트는 [에어비앤비](https://www.airbnb.co.kr/) 사이트를 참조하여 학습목적으로 만들었습니다.
- 실무수준의 프로젝트이지만 학습용으로 만들었기 때문에 이 코드를 활용하여 이득을 취하거나 무단 배포할 경우 법적으로 문제될 수 있습니다.
- 이 프로젝트에서 사용하고 있는 사진 대부분은 위코드에서 구매한 것이므로 해당 프로젝트 외부인이 사용할 수 없습니다.
