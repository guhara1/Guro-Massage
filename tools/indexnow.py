#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexNow 제출 — 빙·네이버·얀덱스·Seznam에 URL 색인을 즉시 통보한다.
(구글은 IndexNow 미참여 → tools/google_indexing.py 사용)

공유 엔드포인트(api.indexnow.org) 한 번 제출로 참여 검색엔진 전체에 전파된다.

사용법
  python3 tools/indexnow.py                # sitemap.xml의 전체 URL 제출
  python3 tools/indexnow.py URL1 URL2 ...   # 지정한 URL만 제출(새 글 발행 시 권장)
  python3 tools/indexnow.py --new           # 매거진 글 URL만 제출

키 파일은 빌드 시 루트에 `<INDEXNOW_KEY>.txt`로 생성된다(반드시 배포되어 접근 가능해야 함).
"""
import sys
import os
import re
import json
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import DOMAIN, INDEXNOW_KEY, ARTICLES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = DOMAIN.split("://", 1)[-1].rstrip("/")
ENDPOINT = "https://api.indexnow.org/indexnow"


def sitemap_urls():
    p = os.path.join(ROOT, "sitemap.xml")
    return re.findall(r"<loc>(.*?)</loc>", open(p, encoding="utf-8").read())


def article_urls():
    return [f"{DOMAIN}/magazine/{a['slug']}/" for a in ARTICLES]


def submit(urls):
    urls = [u for u in urls if u.startswith("http")]
    if not urls:
        print("제출할 URL이 없습니다.")
        return
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{DOMAIN}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow OK: HTTP {r.status} · {len(urls)}개 URL 제출")
            print("  (200/202 = 정상 접수, 빙·네이버·얀덱스로 전파)")
    except urllib.error.HTTPError as e:
        print(f"IndexNow 응답: HTTP {e.code} — {e.read().decode(errors='ignore')[:200]}")
    except Exception as e:
        print("IndexNow 제출 실패:", e)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--new"]:
        submit(article_urls())
    elif args:
        submit(args)
    else:
        submit(sitemap_urls())
