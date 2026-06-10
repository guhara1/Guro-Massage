#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
구글 Indexing API 제출 — 구글에 URL 색인/갱신을 즉시 통보한다.
(구글은 IndexNow에 참여하지 않으므로 구글용은 이 스크립트를 사용)

사전 준비
  1) Google Cloud 프로젝트에서 'Indexing API' 사용 설정
  2) 서비스 계정 생성 → JSON 키 발급
  3) Search Console 해당 사이트 속성에 그 서비스 계정 이메일을 '소유자'로 추가
  4) pip install google-auth requests

사용법
  GOOGLE_APPLICATION_CREDENTIALS=service-account.json \
    python3 tools/google_indexing.py URL1 URL2 ...
  GOOGLE_APPLICATION_CREDENTIALS=service-account.json \
    python3 tools/google_indexing.py --new        # 매거진 글 전체
  GOOGLE_APPLICATION_CREDENTIALS=service-account.json \
    python3 tools/google_indexing.py --sitemap     # 사이트맵 전체

참고: 구글 Indexing API는 공식적으로 JobPosting/BroadcastEvent 대상이지만,
일반 페이지 제출에도 널리 쓰인다. 핵심 색인은 Search Console 사이트맵 제출과 병행할 것.
"""
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import DOMAIN, ARTICLES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def sitemap_urls():
    p = os.path.join(ROOT, "sitemap.xml")
    return re.findall(r"<loc>(.*?)</loc>", open(p, encoding="utf-8").read())


def article_urls():
    return [f"{DOMAIN}/magazine/{a['slug']}/" for a in ARTICLES]


def publish(urls):
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        sys.exit("의존성 필요: pip install google-auth requests")

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        sys.exit("환경변수 GOOGLE_APPLICATION_CREDENTIALS 에 서비스 계정 JSON 경로를 지정하세요.")

    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    session = AuthorizedSession(creds)
    ok = 0
    for url in urls:
        if not url.startswith("http"):
            continue
        r = session.post(ENDPOINT, json={"url": url, "type": "URL_UPDATED"})
        if r.status_code == 200:
            ok += 1
        else:
            print(f"  실패 {r.status_code}: {url} — {r.text[:120]}")
    print(f"구글 Indexing API: {ok}/{len(urls)}개 URL 통보 완료")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--new"]:
        publish(article_urls())
    elif args == ["--sitemap"]:
        publish(sitemap_urls())
    elif args:
        publish(args)
    else:
        sys.exit("URL 인자 또는 --new / --sitemap 옵션이 필요합니다.")
