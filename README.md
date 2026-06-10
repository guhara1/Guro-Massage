# 구로88마사지 — 구로 출장마사지·홈타이 안내 사이트

구로구 전지역 방문 건강관리(출장마사지·홈타이) 예약 안내 정적 사이트입니다.
순수 HTML + 인라인 CSS/JS(외부 의존성 0)로, `tools/build.py` 단일 생성기가 모든 페이지를 만듭니다.

- **상호**: 구로88마사지
- **전화 예약**: 0508-202-4719 (`tel:+825082024719`) · 연중무휴 24시간 상담
- **도메인**: `https://guro-massage.pages.dev` (Cloudflare Pages)

## 빌드 방법

```bash
python3 tools/build.py
```

표준 라이브러리만 사용하며, 실행 시 모든 `index.html`과 `sitemap.xml`,
`robots.txt`, `site.webmanifest`, `favicon.svg`, `assets/og-cover.svg`를 생성합니다.
실행 끝에 **noindex 처리된 페이지 목록**(본문이 짧은 유틸리티 상세 페이지)을 출력합니다.

## SEO 설계 원칙 (Google 가이드 준수)

이 사이트는 도어웨이·중복·키워드 반복을 피하도록 설계되었습니다.

- **대표 키워드는 분산**: 상단 메뉴/카드에는 지명만 노출하고,
  `출장마사지·홈타이` 키워드는 각 페이지의 `H1`·`title`·본문에서만 사용합니다.
- **지역·역·테마 분리**: `구로역 스웨디시`처럼 **지역+역+테마 조합 페이지는 만들지 않습니다.**
  지역/역 페이지에서는 관련 테마로 *링크만* 연결합니다.
- **숫자 행정동 통합**: 구로1~5동→구로동, 고척1~2동→고척동, 개봉1~3동→개봉동,
  오류1~2동→오류동. 숫자 동 단위 페이지는 만들지 않습니다.
- **환승역 URL 1개**: 신도림·대림·온수역 등은 여러 노선 메뉴에 보여도 주소는 하나입니다.
- **고유 콘텐츠 + noindex 안전장치**: 페이지마다 본문·FAQ·메타를 개별 작성합니다.
  본문 글자수가 하한(`NOINDEX_MIN`, 기본 950자) 미만인 얇은 유틸리티 상세 페이지는
  자동으로 `noindex` 처리되어 색인에서 제외됩니다. 콘텐츠 핵심 페이지(메인·지역 동 10곳)는
  모두 2,000자 이상으로 색인됩니다.
- **구조화 데이터**: 메인은 `HealthAndBeautyBusiness`(LocalBusiness),
  모든 안내 페이지에 `BreadcrumbList` + `FAQPage` JSON-LD를 삽입합니다.

## 사이트 구조

| 경로 | 내용 | 색인 |
|---|---|---|
| `/` | 구로 출장마사지·홈타이 메인 허브 | ✅ |
| `/guro/` | 구로 출장마사지 안내 허브 (+ `/guro/faq/`) | ✅ |
| `/guro-gu/` | 지역별 안내 허브 | ✅ |
| `/guro-gu/<dong>/` | 대표 동 10곳 (신도림·구로·가리봉·고척·개봉·오류·천왕·항·궁·온수) | ✅ |
| `/guro-gu/stations/` | 지하철역 허브 (1·2·7호선 구로권) | ✅ |
| `/guro-gu/stations/<station>/` | 역 11곳 (환승역 URL 1개) | ✅ |
| `/theme/` + `/theme/<slug>/` | 테마 허브 + 14종 | ✅ |
| `/course/` + `/course/<slug>/` | 코스 허브 + 8종 | 허브만 |
| `/reservation/`·`/guide/`·`/customer/` | 예약·가이드·고객센터 허브(+ 하위) | 허브만 |
| `/reviews/` | 후기 | ✅ |
| `/magazine/` + `/magazine/category/<slug>/` + `/magazine/<slug>/` | 매거진(블로그) 허브 + 카테고리 4종 + 글 10편 | ✅ |
| `/privacy/`·`/terms/`·`/youth/` | 정책 | ✅ |

생성 페이지 총 83개 중 63개 색인 / 20개 noindex(얇은 하위 페이지).
매거진 글은 `tools/articles.py`에 분리해 손으로 작성한 고유 편집 콘텐츠이며,
글마다 본문(리드+섹션+FAQ, 공백 포함) **2,000~2,500자**로 작성했습니다(도어웨이·스팸·복사·중복 금지).
카테고리: 이용가이드 · 코스·테마 · 지역·역세권 · 활용팁.
글마다 `BlogPosting` + `BreadcrumbList` + `FAQPage` JSON-LD를 삽입합니다.

## 코스·요금 (기본 기준)

| 코스 | 시간 | 기본 요금 |
|---|---|---|
| 60분 | 60분 | 90,000원 |
| 90분 | 90분 | 150,000원 |
| 120분 | 120분 | 180,000원 |

> 표시 요금은 기본 기준이며 지역·시간대·인원에 따라 달라질 수 있습니다.

## 배포 (Cloudflare Pages 등 정적 호스팅)

빌드 산출물이 곧 배포물입니다. 저장소를 정적 호스팅에 연결하고
빌드 명령으로 `python3 tools/build.py`를 지정하면 됩니다.

## 검색 등록 · 빠른 인덱싱

빌드 시 자동 생성되는 색인 자산:

| 파일 | 용도 |
|---|---|
| `sitemap.xml` | 색인 대상 전 페이지(`lastmod` 포함, noindex 제외) |
| `rss.xml` | 매거진 RSS 2.0 피드(새 글 발행 채널, `<head>`에 자동발견 링크) |
| `robots.txt` | 네이버(Yeti)·구글(Googlebot)·빙(bingbot)·다음(Daumoa) 허용 + Sitemap·RSS |
| `<INDEXNOW_KEY>.txt` | IndexNow 키 파일(루트 게시) |

### 1) 검색엔진 소유확인 + 사이트맵 제출 (최초 1회)
- **네이버 서치어드바이저**: 사이트 등록 → (메인 `<head>`의 `naver-site-verification` 메타로) 소유확인 → `sitemap.xml`·`rss.xml` 제출.
- **구글 서치콘솔**: 속성 등록 → 소유확인 → `sitemap.xml` 제출.
- **빙 웹마스터**: 사이트 추가 → `sitemap.xml` 제출(구글 서치콘솔에서 가져오기 가능).

### 2) IndexNow — 빙·네이버·얀덱스 즉시 통보
글을 올리거나 페이지를 바꾼 직후 실행하면 됩니다.
```bash
python3 tools/indexnow.py            # 사이트맵 전체 제출
python3 tools/indexnow.py --new      # 매거진 글 URL만 제출
python3 tools/indexnow.py https://도메인/magazine/새글/   # 특정 URL
```
공유 엔드포인트(`api.indexnow.org`) 한 번 제출로 **빙·네이버·얀덱스**에 전파됩니다.
키 파일(`/<INDEXNOW_KEY>.txt`)이 실제 도메인에서 접근 가능해야 합니다.

### 3) 구글 Indexing API (구글은 IndexNow 미참여)
```bash
# 사전: Indexing API 사용설정 + 서비스계정 JSON + Search Console 속성에 소유자 추가
pip install google-auth requests
GOOGLE_APPLICATION_CREDENTIALS=service-account.json \
  python3 tools/google_indexing.py --new
```

### 4) 자동화 (GitHub Actions)
`.github/workflows/indexing.yml` — `main`에 콘텐츠가 push되면 자동으로
IndexNow 제출(+시크릿 `GOOGLE_INDEXING_CREDENTIALS`가 있으면 구글 Indexing API)까지 실행합니다.

> **sitemap ping 관련**: 구글은 sitemap ping(`/ping?sitemap=`)을 2023년 6월,
> 빙도 유사하게 폐기했습니다. 현재 표준은 **서치콘솔/웹마스터 사이트맵 제출 + IndexNow**이며,
> 이 저장소는 그 방식으로 구성되어 있습니다.

## 새 사이트로 복제 / 값 교체

`tools/build.py` 상단 **설정 블록**만 바꾸면 전 페이지에 반영됩니다.

- `DOMAIN` — 실제 운영 도메인 (canonical·OG·sitemap·robots 일괄 반영)
- `SITE_NAME` / `BRAND_MARK` / `TAGLINE` — 브랜드
- `PHONE_DISPLAY` / `PHONE_TEL` — 전화(표시용 / `tel:` 국제표기)
- `BIZ` — 상호·대표·사업자등록번호·주소·개인정보책임자
  (※ `reg`·`addr` 등 미정 값은 운영자가 확정 후 교체)
- `PRICES` — 코스·시간·요금
- `NOINDEX_MIN` — 색인 본문 하한

## 매거진 콘텐츠 추가/수정

매거진 글과 카테고리는 `tools/articles.py`의 `ARTICLES`·`MAG_CATS`에 정의되어 있습니다.
글 1편 = `{slug, cat, title, h1, desc, lead, secs[(소제목, HTML)], faq[(질문, 답)], related}`.
글마다 본문을 2,000~2,500자(공백 포함)로 고유하게 작성하고 `python3 tools/build.py`를
실행하면 글 페이지·허브·카테고리·sitemap이 갱신됩니다.

## 참고 문서

- `docs/SITE-SPEC.md` — 원본 디자인·메뉴·SEO 전체 사양서
- `docs/starter-README.md` — 스타터 킷 사용 가이드
