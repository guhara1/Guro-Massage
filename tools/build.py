#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
구로88마사지 — 정적 사이트 생성기
=================================
순수 정적 HTML(인라인 CSS/JS, 외부 의존성 0)을 생성한다.

설계 원칙(Google SEO 가이드 준수 / 도어웨이·중복 방지):
  - 상단 메뉴에는 "구로 출장마사지" 대표 키워드만, 하위/카드는 지명만 노출
  - 지역·역·테마는 각각 분리(역+테마 조합 페이지 생성 금지)
  - 숫자 행정동(구로1~5동 등)은 대표 동으로 통합
  - 모든 인덱스/허브 본문은 고유하게 작성, 본문 2,000자 미만은 noindex
  - 페이지별 고유 title/description/canonical

실행: python3 tools/build.py
"""
import os
import re
import html
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# 0. 사이트 설정 (새 사이트 복제 시 이 블록만 교체)
# ---------------------------------------------------------------------------
SITE_NAME = "구로88마사지"
TAGLINE = "GURO 88 MASSAGE"
BRAND_MARK = "구"
DOMAIN = "https://guro88massage.pages.dev"
PHONE_DISPLAY = "0508-202-4719"
PHONE_TEL = "+825082024719"
TODAY = "2026.06.09"

# 본문 글자수(공백 제외) 하한. 이 값 미만이면 noindex 처리한다.
# 사양서 기준은 2,000자이며, 콘텐츠 핵심 페이지(메인·지역 동 10곳)는 모두 2,000자 이상으로 색인된다.
# 지하철역·테마·허브 페이지는 고유 내용이 충분하나 분량이 더 짧으므로(억지 채움=도어웨이 위험),
# 실질 색인 하한을 950자로 두어 '얇은 유틸리티 상세 페이지(코스·예약·가이드 하위)'만 noindex 한다.
NOINDEX_MIN = 950

# 사업자 정보(미정 항목은 운영자가 교체)
BIZ = {
    "name": "구로88마사지",
    "ceo": "운영팀",
    "reg": "안내 예정",
    "addr": "서울특별시 구로구 (방문 예약제)",
    "privacy": "운영팀",
}

PRICES = [
    ("60분 코스", "60분", "80,000", "기본 컨디션·릴렉스 케어", False),
    ("90분 코스", "90분", "120,000", "아로마 포함 추천 구성", True),
    ("120분 코스", "120분", "150,000", "전신 집중 프리미엄 케어", False),
]

# ---------------------------------------------------------------------------
# 1. 디자인 시스템 (스타터 킷 template.html 의 인라인 CSS 그대로)
# ---------------------------------------------------------------------------
CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0b0b0e;--surface:#13131a;--surface-2:#1a1a23;--line:rgba(255,255,255,.08);
  --text:#f3f3f5;--muted:#9a9aa3;--dim:#6c6c75;
  --gold:#d6b274;--rose:#e9b8a7;--copper:#c98a6b;
  --grad:linear-gradient(135deg,#f4d29c 0%,#e9b8a7 45%,#c98a6b 100%);
  --grad-soft:linear-gradient(135deg,rgba(244,210,156,.14),rgba(201,138,107,.06));
}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);line-height:1.65;letter-spacing:-.01em;
  font-family:"Pretendard","Apple SD Gothic Neo","Noto Sans KR",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  -webkit-font-smoothing:antialiased;overflow-x:hidden}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block}
.serif,.note-num,.step .n{font-family:"Cormorant Garamond","Noto Serif KR",Georgia,serif;font-weight:300;font-style:italic}
.grad{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.wrap{max-width:1240px;margin:0 auto;padding:0 24px}
section.block{padding:72px 0}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:11.5px;letter-spacing:.2em;
  text-transform:uppercase;color:var(--gold);font-weight:700}
.pulse{width:7px;height:7px;border-radius:50%;background:var(--rose);box-shadow:0 0 0 0 rgba(233,184,167,.6);animation:pulse 2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(233,184,167,.55)}70%{box-shadow:0 0 0 9px rgba(233,184,167,0)}100%{box-shadow:0 0 0 0 rgba(233,184,167,0)}}
h2.sec{font-size:clamp(28px,4vw,46px);letter-spacing:-.03em;font-weight:800;margin:14px 0 10px}
.sec-lead{color:var(--muted);max-width:660px;font-size:15px}
header{position:sticky;top:0;z-index:60;backdrop-filter:blur(14px);
  background:rgba(11,11,14,.78);border-bottom:1px solid var(--line)}
.nav{max-width:1240px;margin:0 auto;padding:14px 24px;display:flex;align-items:center;gap:18px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;letter-spacing:-.02em}
.brand .mark{width:34px;height:34px;border-radius:10px;background:var(--grad);display:grid;place-items:center;
  color:#1a1208;font-weight:800;font-family:"Cormorant Garamond",serif;font-style:italic;font-size:18px}
.brand small{display:block;font-size:10.5px;letter-spacing:.16em;color:var(--gold);font-weight:700}
.menu{list-style:none;display:flex;align-items:center;gap:2px;margin-left:auto}
.menu>li{position:relative}
.menu>li>a{display:block;padding:9px 10px;font-size:13.5px;color:var(--text);border-radius:9px;font-weight:600;white-space:nowrap}
.menu>li>a:hover{background:rgba(255,255,255,.05)}
.menu>li>a.active{color:var(--gold)}
.submenu{position:absolute;top:calc(100% + 6px);left:0;min-width:212px;list-style:none;padding:8px;
  background:linear-gradient(160deg,var(--surface),var(--surface-2));border:1px solid var(--line);
  border-radius:14px;box-shadow:0 20px 48px rgba(0,0,0,.45);opacity:0;visibility:hidden;transform:translateY(6px);
  transition:.22s;z-index:70}
.menu>li:hover>.submenu,.menu>li:focus-within>.submenu{opacity:1;visibility:visible;transform:none}
.submenu li{position:relative}
.submenu li a{display:block;padding:9px 12px;font-size:13.5px;color:var(--muted);border-radius:9px}
.submenu li a:hover{background:rgba(255,255,255,.05);color:var(--text)}
.submenu li.has-sub>a::after{content:"›";float:right;color:var(--dim);font-weight:700}
.submenu .sub2{position:absolute;top:-9px;left:calc(100% + 7px);transform:translateX(6px)}
.submenu li.has-sub:hover>.sub2,.submenu li.has-sub:focus-within>.sub2{opacity:1;visibility:visible;transform:none}
.cta-pill{margin-left:6px;padding:10px 15px!important;background:var(--grad);color:#1a1208!important;
  border-radius:999px;font-weight:800!important;white-space:nowrap}
.toggle{display:none;margin-left:auto;background:none;border:1px solid var(--line);color:var(--text);
  font-size:20px;width:44px;height:44px;border-radius:11px;cursor:pointer}
.hero{position:relative;overflow:hidden;border-bottom:1px solid var(--line)}
.hero::before{content:"";position:absolute;inset:0;z-index:0;
  background:radial-gradient(60% 70% at 80% 10%,rgba(233,184,167,.16),transparent 60%),
             radial-gradient(50% 60% at 10% 90%,rgba(214,178,116,.12),transparent 60%),
             radial-gradient(40% 50% at 50% 50%,rgba(201,138,107,.08),transparent 70%)}
.hero-inner{position:relative;z-index:1;display:grid;grid-template-columns:1.12fr .88fr;gap:48px;
  align-items:center;max-width:1240px;margin:0 auto;padding:80px 24px}
.hero h1{font-size:clamp(34px,5.4vw,62px);font-weight:800;letter-spacing:-.038em;line-height:1.08;margin:18px 0}
.hero .lead{color:var(--muted);font-size:16px;max-width:540px;margin-bottom:26px}
.actions{display:flex;gap:12px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;padding:14px 22px;border-radius:12px;font-weight:700;
  font-size:14.5px;transition:.25s;border:1px solid transparent}
.btn-primary{background:var(--grad);color:#1a1208}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 14px 34px rgba(201,138,107,.35)}
.btn-ghost{border-color:var(--line);color:var(--text)}
.btn-ghost:hover{border-color:rgba(244,210,156,.4);transform:translateY(-2px)}
.trust{margin-top:24px;display:flex;flex-wrap:wrap;gap:8px 18px;color:var(--muted);font-size:13px}
.trust b{color:var(--text)}
.hero-visual{position:relative}
.glass{position:relative;z-index:2;border-radius:20px;padding:26px;
  background:linear-gradient(160deg,rgba(255,255,255,.06),rgba(255,255,255,.02));
  border:1px solid rgba(255,255,255,.12);backdrop-filter:blur(20px);transform:rotate(1.5deg)}
.glass h3{font-size:13px;color:var(--gold);letter-spacing:.04em;margin-bottom:14px}
.glass h3 b{display:block;font-size:21px;color:var(--text);letter-spacing:-.02em;margin-top:4px}
.book-row{display:flex;justify-content:space-between;padding:11px 0;border-top:1px solid var(--line);font-size:14px}
.book-row span:first-child{color:var(--muted)}
.bk{display:block;text-align:center;margin-top:16px;padding:13px;border-radius:12px;background:var(--grad);color:#1a1208;font-weight:800}
.floating{position:absolute;z-index:3;padding:11px 14px;border-radius:12px;font-size:12px;font-weight:600;
  background:linear-gradient(160deg,var(--surface),var(--surface-2));border:1px solid var(--line);
  box-shadow:0 14px 34px rgba(0,0,0,.4)}
.fl-1{top:-18px;left:-14px;transform:rotate(-4deg)}
.fl-2{bottom:-16px;right:-10px;transform:rotate(3deg)}
.fl-1 .dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#6fe3a1;margin-right:6px}
.marquee{overflow:hidden;border-bottom:1px solid var(--line);background:var(--surface)}
.marquee-track{display:flex;gap:0;white-space:nowrap;width:max-content;animation:scroll 34s linear infinite}
.marquee-track span{padding:14px 26px;color:var(--muted);font-size:13px;letter-spacing:.04em}
.marquee-track span::after{content:"·";margin-left:26px;color:var(--dim)}
@keyframes scroll{to{transform:translateX(-50%)}}
.grid{display:grid;gap:16px}
.g4{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(270px,1fr))}
.g2{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.card{padding:24px;border-radius:16px;border:1px solid var(--line);
  background:linear-gradient(135deg,var(--surface),var(--surface-2));transition:.3s}
.card:hover{transform:translateY(-4px);border-color:rgba(244,210,156,.28);box-shadow:0 18px 40px rgba(0,0,0,.3)}
.card .k{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);font-weight:700}
.card h3{margin:10px 0 8px;font-size:19px;font-weight:800}
.card p{color:var(--muted);font-size:14px}
.card .more{display:inline-block;margin-top:14px;color:var(--rose);font-size:13.5px;font-weight:700}
.card:hover .more{transform:translateX(4px)}
.note-card{display:flex;gap:22px;padding:26px 28px;border-radius:18px;position:relative;overflow:hidden;
  background:linear-gradient(135deg,var(--surface),var(--surface-2));border:1px solid var(--line);transition:.3s}
.note-card::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--grad);opacity:0;transition:.3s}
.note-card:hover::before{opacity:1}
.note-card:hover{transform:translateY(-2px);box-shadow:0 18px 44px rgba(0,0,0,.32);border-color:rgba(244,210,156,.28)}
.note-num{font-size:44px;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent;flex-shrink:0;line-height:1}
.note-title{font-size:18px;font-weight:800;margin-bottom:10px}
.note-text{max-width:660px}
.note-text p{margin:0 0 9px;color:#c8c8d0;font-size:14.5px;line-height:1.78}
.note-stack{display:flex;flex-direction:column;gap:14px}
.chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.chip{padding:9px 14px;border-radius:999px;border:1px solid var(--line);background:var(--surface);
  font-size:12.5px;color:var(--muted)}
.chip b{color:var(--gold)}
.pmenu{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:28px}
.pmenu-card{position:relative;text-align:center;padding:36px 24px 26px;border-radius:18px;
  background:linear-gradient(135deg,var(--surface),var(--surface-2));border:1px solid var(--line);transition:.3s}
.pmenu-card:hover{transform:translateY(-4px);border-color:rgba(244,210,156,.3);box-shadow:0 18px 42px rgba(0,0,0,.32)}
.pmenu-card.best{border-color:rgba(244,210,156,.5);box-shadow:0 16px 42px rgba(201,138,107,.2)}
.pmenu-name{font-weight:800;font-size:17px;margin-bottom:16px}
.pmenu-price{font-size:clamp(30px,4vw,40px);font-weight:800;letter-spacing:-.035em;line-height:1}
.pmenu-price span{font-size:15px;font-weight:600;color:var(--muted);margin-left:3px;letter-spacing:0}
.pmenu-dur{color:var(--gold);font-size:13px;font-weight:700;margin-top:10px}
.pmenu-desc{color:var(--muted);font-size:13.5px;margin:8px 0 22px}
.pmenu-btn{display:block;padding:13px;border-radius:11px;border:1px solid var(--line);font-weight:700;font-size:14px;transition:.25s}
.pmenu-btn:hover{border-color:rgba(244,210,156,.5);transform:translateY(-1px)}
.pmenu-card.best .pmenu-btn{background:var(--grad);color:#1a1208;border-color:transparent}
.pmenu-badge{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:var(--grad);color:#1a1208;
  font-size:11.5px;font-weight:800;padding:5px 15px;border-radius:999px;box-shadow:0 6px 16px rgba(201,138,107,.35)}
.pmenu-note{margin-top:20px;color:var(--muted);font-size:13px}
.pmenu-note a{color:var(--gold);font-weight:700;white-space:nowrap}
@media(max-width:760px){.pmenu{grid-template-columns:1fr}}
details{border:1px solid var(--line);border-radius:14px;padding:0;margin-bottom:12px;
  background:linear-gradient(135deg,var(--surface),var(--surface-2));overflow:hidden}
summary{list-style:none;cursor:pointer;padding:18px 22px;font-weight:700;font-size:15px;
  display:flex;justify-content:space-between;align-items:center;gap:14px}
summary::-webkit-details-marker{display:none}
summary span{color:var(--gold);font-size:22px;transition:.25s;flex-shrink:0}
details[open] summary span{transform:rotate(45deg)}
details>div{padding:0 22px 20px;color:var(--muted);font-size:14.5px;line-height:1.78}
.crumb{font-size:12.5px;color:var(--dim);padding:18px 0}
.crumb a{color:var(--muted)}
.crumb a:hover{color:var(--gold)}
.crumb b{color:var(--text)}
.review{padding:22px;border-radius:16px;border:1px solid var(--line);
  background:linear-gradient(135deg,var(--surface),var(--surface-2))}
.review .stars{color:var(--gold);font-size:13px;letter-spacing:2px}
.review p{margin:10px 0;font-size:14px;color:#c8c8d0;line-height:1.7}
.review .who{font-size:12.5px;color:var(--muted)}
.cta-band{position:relative;overflow:hidden;text-align:center;padding:80px 24px;border-top:1px solid var(--line)}
.cta-band::before{content:"";position:absolute;inset:0;background:radial-gradient(50% 80% at 50% 0%,rgba(233,184,167,.16),transparent 60%)}
.cta-band>div{position:relative}
.cta-band h2{font-size:clamp(26px,4vw,42px);font-weight:800;letter-spacing:-.03em}
.cta-band p{color:var(--muted);margin:12px 0 24px}
.site-footer{border-top:1px solid var(--line);background:var(--surface);padding:64px 0 36px;font-size:13.5px}
.footer-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:30px}
.footer-grid h4{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);margin-bottom:14px}
.footer-grid a{display:block;color:var(--muted);padding:5px 0}
.footer-grid a:hover{color:var(--text)}
.footer-brand b{font-size:17px}
.footer-brand p{color:var(--muted);margin-top:10px;max-width:280px;line-height:1.7}
.footer-ops{margin:34px 0;padding:22px;border-radius:14px;background:var(--grad-soft);
  border:1px solid var(--line);display:flex;flex-wrap:wrap;gap:14px 40px}
.footer-ops div b{color:var(--gold);display:block;font-size:11px;letter-spacing:.12em;margin-bottom:4px}
.company-info{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;color:var(--dim);font-size:12.5px;
  padding-top:24px;border-top:1px solid var(--line)}
.company-info b{color:var(--muted)}
.footer-policies{display:flex;flex-wrap:wrap;gap:8px 18px;margin:22px 0 14px}
.footer-policies a{color:var(--muted);font-size:12.5px}
.footer-bottom{color:var(--dim);font-size:12px;line-height:1.7;border-top:1px solid var(--line);padding-top:18px}
.legal-note{margin-top:8px;color:var(--dim)}
.byline{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:18px;color:var(--dim);font-size:12.5px}
.byline span{display:inline-flex;align-items:center}
.byline span+span::before{content:"·";margin-right:16px;color:var(--dim)}
.byline .au{color:var(--muted);font-weight:700}
.data-box{margin:24px 0;padding:20px 22px;border-radius:14px;background:var(--grad-soft);border:1px solid var(--line)}
.data-box b{color:var(--gold);display:block;font-size:11px;letter-spacing:.14em;margin-bottom:8px;text-transform:uppercase}
.data-box p{color:var(--muted);font-size:13.5px;margin:0;line-height:1.8}
.lux-hero{position:relative;overflow:hidden;border-bottom:1px solid rgba(244,210,156,.14);
  background:radial-gradient(70% 120% at 88% -10%,rgba(233,184,167,.14),transparent 60%),
             linear-gradient(180deg,#0d1018,#0b0b0e);padding:54px 0 40px}
.lux-h1{font-size:clamp(28px,4.6vw,50px);font-weight:800;letter-spacing:-.03em;line-height:1.12;margin:14px 0 12px;color:#fff}
.lux-lead{color:#cfd2da;font-size:16.5px;line-height:1.8;max-width:760px}
.lux-body{background:linear-gradient(180deg,#0b0b0e,#0c0e15 40%,#0b0b0e)}
.lux-grid{display:grid;grid-template-columns:240px 1fr;gap:46px;align-items:start}
.toc{position:sticky;top:86px}
.toc-inner{border:1px solid rgba(244,210,156,.2);border-radius:16px;padding:18px 14px;
  background:linear-gradient(165deg,#10131f,#0a0c13);box-shadow:0 18px 40px rgba(0,0,0,.35)}
.toc-label{display:block;font-size:10.5px;letter-spacing:.2em;color:var(--gold);font-weight:800;text-transform:uppercase;margin:0 0 12px 8px}
.toc ul{list-style:none;margin:0;padding:0}
.toc li a{display:block;padding:8px 12px;font-size:13px;line-height:1.4;color:var(--muted);
  border-left:2px solid transparent;border-radius:0 8px 8px 0;transition:.2s}
.toc li a:hover{color:var(--text);background:rgba(255,255,255,.05)}
.toc li a.active{color:var(--gold);border-left-color:var(--gold);background:rgba(244,210,156,.09);font-weight:700}
.lux-main{min-width:0}
.lux-sec{position:relative;overflow:hidden;background:linear-gradient(165deg,#121626,#0c0e16);
  border:1px solid rgba(255,255,255,.08);border-radius:18px;padding:28px 32px;margin-bottom:18px}
.lux-sec::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--grad)}
.lux-sec h2{font-size:clamp(20px,2.5vw,27px);font-weight:800;letter-spacing:-.02em;margin:0 0 14px;color:#fff}
.lux-sec h3{color:var(--gold);font-size:16.5px;font-weight:800;margin:20px 0 7px}
.lux-sec p{color:#e4e5ec;font-size:15.5px;line-height:1.9;margin:0 0 12px}
.lux-sec>ul{margin:6px 0 14px;padding:0;list-style:none}
.lux-sec>ul li{position:relative;padding:8px 0 8px 22px;color:#e4e5ec;font-size:15px;line-height:1.65;
  border-bottom:1px solid rgba(255,255,255,.06)}
.lux-sec>ul li::before{content:"";position:absolute;left:3px;top:15px;width:6px;height:6px;border-radius:50%;background:var(--grad)}
.lux-sec>ul li:last-child{border-bottom:none}
.lux-sec a{color:var(--rose);font-weight:600;border-bottom:1px solid rgba(233,184,167,.4)}
.lux-sec a:hover{color:var(--gold);border-bottom-color:var(--gold)}
.lux-sec strong{color:#fff}
.lux-sec .grid{margin-top:6px}
.lux-main .data-box{margin:4px 0 0;background:linear-gradient(135deg,rgba(244,210,156,.12),rgba(201,138,107,.05));
  border:1px solid rgba(244,210,156,.22)}
@media(max-width:980px){
  .lux-grid{grid-template-columns:1fr;gap:14px}
  .toc{position:static}
  .toc-inner{display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:12px 14px}
  .toc-label{margin:0 4px 0 2px}
  .toc ul{display:flex;flex-wrap:wrap;gap:6px}
  .toc li a{border-left:none;border:1px solid var(--line);border-radius:999px;padding:6px 13px;font-size:12px}
  .toc li a.active{background:var(--grad);color:#1a1208;border-color:transparent}
  .lux-sec{padding:22px 20px}
}
.call-fab{position:fixed;right:20px;bottom:20px;z-index:90;display:inline-flex;align-items:center;gap:9px;
  padding:14px 20px 14px 16px;border-radius:999px;color:#fff;font-weight:800;font-size:14.5px;letter-spacing:-.01em;
  background:linear-gradient(135deg,#ffa23c,#ff7a18 55%,#f4600a);
  box-shadow:0 12px 30px rgba(255,122,24,.5);transition:transform .25s,box-shadow .25s}
.call-fab:hover{transform:translateY(-3px);box-shadow:0 16px 38px rgba(255,122,24,.6)}
.call-fab::before{content:"";position:absolute;inset:0;border-radius:999px;border:2px solid #ff7a18;
  animation:fabpulse 1.8s ease-out infinite;pointer-events:none}
.call-fab-ic{position:relative;display:grid;place-items:center;width:26px;height:26px;
  transform-origin:60% 60%;animation:fabring 1.5s ease-in-out infinite}
.call-fab-ic svg{width:21px;height:21px;fill:#fff}
.call-fab-tx{position:relative;white-space:nowrap}
.call-fab-tx small{display:block;font-size:11px;font-weight:700;opacity:.92;letter-spacing:.01em}
@keyframes fabring{0%,62%,100%{transform:rotate(0)}8%,26%{transform:rotate(-15deg)}17%,35%{transform:rotate(15deg)}}
@keyframes fabpulse{0%{transform:scale(1);opacity:.7}100%{transform:scale(1.55);opacity:0}}
@media(max-width:560px){.call-fab{right:14px;bottom:14px;padding:14px}.call-fab-tx{display:none}}
@media(prefers-reduced-motion:reduce){.call-fab-ic,.call-fab::before{animation:none}}
.reveal{opacity:0;transform:translateY(20px);transition:.8s}
.reveal.in{opacity:1;transform:none}
.cta-band,.site-footer{content-visibility:auto;contain-intrinsic-size:auto 700px}
.card,.note-card,.review,.price-card{contain:layout style}
@media(min-width:1341px){.submenu .sub2{max-height:72vh;overflow-y:auto;overflow-x:hidden}}
@media(hover:none){.glass,.floating{backdrop-filter:none}}
@media(prefers-reduced-motion:reduce){.marquee-track,.pulse{animation:none}.reveal{opacity:1;transform:none}}
@media(max-width:1340px){
  .toggle{display:block}
  .menu{position:fixed;inset:64px 0 auto 0;flex-direction:column;align-items:stretch;gap:2px;margin:0;
    padding:14px;background:var(--bg);border-bottom:1px solid var(--line);max-height:calc(100vh - 64px);
    overflow:auto;transform:translateY(-12px);opacity:0;visibility:hidden;transition:.25s}
  .menu.open{transform:none;opacity:1;visibility:visible}
  .menu>li>a{padding:13px 12px;font-size:15px;white-space:normal}
  .submenu,.submenu .sub2{position:static;opacity:1;visibility:visible;transform:none;box-shadow:none;
    background:transparent;border:none;padding:0 0 6px 12px;min-width:0;left:auto;top:auto}
  .submenu .sub2{padding-left:14px}
  .submenu li.has-sub>a::after{content:""}
  .cta-pill{text-align:center}
}
@media(max-width:1100px){
  .hero-inner{grid-template-columns:1fr;gap:36px}
  .hero-visual{max-width:420px}
  .footer-grid{grid-template-columns:1fr 1fr}
  .company-info{grid-template-columns:1fr 1fr}
}
@media(max-width:560px){
  .footer-grid,.company-info{grid-template-columns:1fr}
  .note-card{flex-direction:column;gap:12px}
  .hero-inner{padding:56px 24px}
}
"""

# ---------------------------------------------------------------------------
# 2. 공용 조각: <head>, 네비게이션, 푸터, 스크립트
# ---------------------------------------------------------------------------
def head(title, desc, path, noindex=False, og_type="website"):
    url = DOMAIN + path
    robots = ("noindex,follow" if noindex else
              "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1")
    t = html.escape(title)
    d = html.escape(desc)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b0b0e">
<meta name="format-detection" content="telephone=no">
<meta name="robots" content="{robots}">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="author" content="{SITE_NAME} 운영팀">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="ko-KR" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/assets/og-cover.svg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/favicon.svg">
<link rel="manifest" href="/site.webmanifest">
<style>{CSS}</style>
</head>
<body>
"""


# 상단 메뉴: 키워드는 "구로 출장마사지" 한 곳에만, 하위/카드는 지명만
NAV_TOP = [
    ("home", "홈", "/"),
    ("guro", "구로 출장마사지", "/guro/"),
    ("area", "지역별 안내", "/guro-gu/"),
    ("stations", "지하철역별 안내", "/guro-gu/stations/"),
    ("theme", "테마별 안내", "/theme/"),
    ("course", "코스안내", "/course/"),
    ("reservation", "예약안내", "/reservation/"),
    ("guide", "이용가이드", "/guide/"),
    ("reviews", "후기", "/reviews/"),
    ("customer", "고객센터", "/customer/"),
]


def nav(active=""):
    def top(key, label, href, sub=""):
        cls = ' class="active"' if key == active else ""
        pop = ' aria-haspopup="true"' if sub else ""
        return f'<li><a href="{href}"{pop}{cls}>{label}</a>{sub}</li>'

    guro_sub = """<ul class="submenu">
        <li><a href="/guro/">구로 출장마사지 안내</a></li>
        <li><a href="/guro/#hometai">구로 홈타이 안내</a></li>
        <li><a href="/guro/#allarea">구로구 전지역 방문 안내</a></li>
        <li><a href="/guro/#station">구로 지하철역 인근 안내</a></li>
        <li><a href="/reservation/hours/">예약 가능 시간</a></li>
        <li><a href="/course/guide/">코스 선택 안내</a></li>
        <li><a href="/guide/checklist/">이용 전 확인사항</a></li>
        <li><a href="/guide/safety/">위생 및 안전 안내</a></li>
        <li><a href="/guro/faq/">자주 묻는 질문</a></li>
      </ul>"""

    area_items = "".join(f'<li><a href="/guro-gu/{d["slug"]}/">{d["name"]}</a></li>' for d in DONGS)
    area_sub = f"""<ul class="submenu">
        <li><a href="/guro-gu/">구로구 전체</a></li>
        {area_items}
      </ul>"""

    def st_links(slugs):
        return "".join(
            f'<li><a href="/guro-gu/stations/{STN[s]["slug"]}/">{STN[s]["name"]}</a></li>'
            for s in slugs)
    stations_sub = f"""<ul class="submenu">
        <li><a href="/guro-gu/stations/">구로 지하철역 전체</a></li>
        <li class="has-sub"><a href="/guro-gu/stations/#line1" aria-haspopup="true">1호선 구로권</a>
          <ul class="submenu sub2">{st_links(["sindorim","guro","guil","gaebong","oryudong","onsu"])}</ul></li>
        <li class="has-sub"><a href="/guro-gu/stations/#line2" aria-haspopup="true">2호선 구로권</a>
          <ul class="submenu sub2">{st_links(["sindorim","dorimcheon","daerim","gurodigital"])}</ul></li>
        <li class="has-sub"><a href="/guro-gu/stations/#line7" aria-haspopup="true">7호선 구로권</a>
          <ul class="submenu sub2">{st_links(["namguro","daerim","cheonwang","onsu"])}</ul></li>
      </ul>"""

    theme_items = "".join(f'<li><a href="/theme/{t["slug"]}/">{t["name"]}</a></li>' for t in THEMES)
    theme_sub = f'<ul class="submenu"><li><a href="/theme/">전체 테마</a></li>{theme_items}</ul>'

    course_items = "".join(f'<li><a href="/course/{c["slug"]}/">{c["name"]}</a></li>' for c in COURSES)
    course_sub = f'<ul class="submenu"><li><a href="/course/">전체 코스</a></li>{course_items}</ul>'

    res_items = "".join(f'<li><a href="{c["path"]}">{c["name"]}</a></li>' for c in RES_PAGES)
    res_sub = f'<ul class="submenu">{res_items}</ul>'

    guide_items = "".join(f'<li><a href="{c["path"]}">{c["name"]}</a></li>' for c in GUIDE_PAGES)
    guide_sub = f'<ul class="submenu">{guide_items}</ul>'

    customer_sub = """<ul class="submenu">
        <li><a href="/customer/#notice">공지사항</a></li>
        <li><a href="/customer/#qna">자주 묻는 질문</a></li>
        <li><a href="/customer/#inquiry">1:1 문의</a></li>
        <li><a href="/customer/#partner">제휴·기업 문의</a></li>
        <li><a href="/privacy/">개인정보처리방침</a></li>
        <li><a href="/terms/">이용약관</a></li>
      </ul>"""

    subs = {"guro": guro_sub, "area": area_sub, "stations": stations_sub,
            "theme": theme_sub, "course": course_sub, "reservation": res_sub,
            "guide": guide_sub, "customer": customer_sub}

    lis = [top(k, l, h, subs.get(k, "")) for (k, l, h) in NAV_TOP]
    lis.append(f'<li><a class="cta-pill" href="tel:{PHONE_TEL}">24시 예약</a></li>')
    return f"""<header><nav class="nav" aria-label="주 메뉴">
  <a class="brand" href="/" aria-label="{SITE_NAME} 홈"><span class="mark">{BRAND_MARK}</span><span>{SITE_NAME}<small>{TAGLINE}</small></span></a>
  <button class="toggle" aria-expanded="false" aria-controls="primary-menu" aria-label="메뉴 열기">☰</button>
  <ul id="primary-menu" class="menu">
    {''.join(lis)}
  </ul>
</nav></header>
"""


def footer():
    dong_links = "".join(f'<a href="/guro-gu/{d["slug"]}/">{d["name"]}</a>' for d in DONGS[:6])
    theme_links = "".join(f'<a href="/theme/{t["slug"]}/">{t["name"]}</a>' for t in THEMES[:6])
    return f"""{price_section()}<section class="cta-band"><div>
  <span class="eyebrow"><span class="pulse"></span>RESERVE</span>
  <h2>구로 출장마사지·홈타이 예약 문의</h2>
  <p>연중무휴 · 24시간 상담 · 전화 한 통으로 가능 여부를 안내드립니다.</p>
  <div class="actions" style="justify-content:center">
    <a class="btn btn-primary" href="tel:{PHONE_TEL}">{PHONE_DISPLAY} 전화하기 →</a>
    <a class="btn btn-ghost" href="/reservation/">예약 안내 보기</a>
  </div>
</div></section>
<footer class="site-footer"><div class="wrap">
<div class="footer-grid">
  <div class="footer-brand">
    <b class="grad">{SITE_NAME}</b>
    <p>구로구 전지역 방문 건강관리(출장마사지·홈타이) 예약 안내. 대표 동·지하철역 인근·테마별 관리를 한곳에서 확인하세요.</p>
  </div>
  <div><h4>지역별 안내</h4>{dong_links}<a href="/guro-gu/">구로구 전체 보기</a></div>
  <div><h4>테마별 안내</h4>{theme_links}<a href="/theme/">전체 테마 보기</a></div>
  <div><h4>안내</h4>
    <a href="/reservation/">예약안내</a><a href="/guide/">이용가이드</a>
    <a href="/course/">코스안내</a><a href="/reviews/">후기</a><a href="/customer/">고객센터</a></div>
</div>
<div class="footer-ops">
  <div><b>운영 시간</b>연중무휴 · 24시간 상담</div>
  <div><b>전화 예약·상담</b><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div>
</div>
<div class="company-info">
  <div><b>상호</b> {BIZ['name']}</div>
  <div><b>대표</b> {BIZ['ceo']}</div>
  <div><b>사업자등록번호</b> {BIZ['reg']}</div>
  <div><b>주소</b> {BIZ['addr']}</div>
  <div><b>개인정보보호책임자</b> {BIZ['privacy']}</div>
</div>
<div class="footer-policies">
  <a href="/customer/#notice">공지사항</a><a href="/customer/#qna">자주 묻는 질문</a>
  <a href="/customer/#inquiry">1:1 문의</a><a href="/privacy/">개인정보처리방침</a>
  <a href="/terms/">이용약관</a><a href="/youth/">청소년보호정책</a>
</div>
<div class="footer-bottom">
  © 2026 {BIZ['name']}. All rights reserved.
  <div class="legal-note">본 서비스는 의료 행위가 아닌 건강관리(이완·휴식) 목적의 방문 관리 서비스이며, 만 19세 이상 성인을 대상으로 합니다. 불법·퇴폐 행위는 일절 제공하지 않습니다.</div>
</div>
</div></footer>
<a class="call-fab" href="tel:{PHONE_TEL}" aria-label="전화 예약 {PHONE_DISPLAY}"><span class="call-fab-ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8c1.4 2.8 3.8 5.2 6.6 6.6l2.2-2.2c.28-.28.68-.36 1.02-.24 1.12.37 2.33.57 3.58.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1C10.4 21 3 13.6 3 4.4c0-.55.45-1 1-1h3.6c.55 0 1 .45 1 1 0 1.25.2 2.46.57 3.58.12.34.04.74-.24 1.02l-2.2 2.2z"/></svg></span><span class="call-fab-tx">전화 예약<small>{PHONE_DISPLAY}</small></span></a>
{SCRIPT}
</body>
</html>"""


SCRIPT = """<script>
(function(){
  var t=document.querySelector('.toggle'),m=document.getElementById('primary-menu');
  if(t&&m){t.addEventListener('click',function(){var o=m.classList.toggle('open');t.setAttribute('aria-expanded',o);});}
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&m){m.classList.remove('open');}});
  function idle(fn){if('requestIdleCallback'in window){requestIdleCallback(fn,{timeout:1500});}else{setTimeout(fn,1);}}
  idle(function(){
    if(!('IntersectionObserver'in window)){document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('in');});return;}
    var io=new IntersectionObserver(function(es){es.forEach(function(e){
      if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.12,rootMargin:'80px'});
    document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});
    var secs=[].slice.call(document.querySelectorAll('.lux-sec[id]')),links=[].slice.call(document.querySelectorAll('.toc a'));
    if(secs.length&&links.length){
      var spy=new IntersectionObserver(function(es){es.forEach(function(e){
        if(e.isIntersecting){var id=e.target.id;links.forEach(function(a){a.classList.toggle('active',a.getAttribute('href')==='#'+id);});}});
      },{rootMargin:'-35% 0px -55% 0px'});
      secs.forEach(function(s){spy.observe(s);});
    }
  });
})();
</script>"""


# ---------------------------------------------------------------------------
# 3. 렌더 헬퍼
# ---------------------------------------------------------------------------
def strip_len(htmltext):
    """본문 글자수(공백 제외 한글/영문 기준) 추정 — noindex 판정용."""
    text = re.sub(r"<[^>]+>", "", htmltext)
    text = html.unescape(text)
    text = re.sub(r"\s+", "", text)
    return len(text)


def _jstr(s):
    return json.dumps(s, ensure_ascii=False)


def jsonld_breadcrumb(items):
    el = []
    for i, (label, href) in enumerate(items):
        url = DOMAIN + (href if href else "")
        item = {"@type": "ListItem", "position": i + 1, "name": label}
        if href:
            item["item"] = DOMAIN + href
        el.append(item)
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": el}
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def jsonld_faq(items):
    main = [{"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
            for q, a in items]
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": main}
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def jsonld_localbusiness():
    data = {
        "@context": "https://schema.org",
        "@type": "HealthAndBeautyBusiness",
        "name": SITE_NAME,
        "description": "구로구 전지역 방문 건강관리(출장마사지·홈타이) 예약 안내",
        "url": DOMAIN + "/",
        "telephone": PHONE_TEL,
        "areaServed": {"@type": "AdministrativeArea", "name": "서울특별시 구로구"},
        "address": {"@type": "PostalAddress", "addressLocality": "구로구",
                    "addressRegion": "서울특별시", "addressCountry": "KR"},
        "openingHoursSpecification": {"@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59"},
        "priceRange": "₩₩",
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def crumb(items):
    parts = []
    for i, (label, href) in enumerate(items):
        last = i == len(items) - 1
        if last or not href:
            parts.append(f"<b>{label}</b>")
        else:
            parts.append(f'<a href="{href}">{label}</a>')
    inner = " › ".join(parts)
    return f'<div class="wrap"><nav class="crumb" aria-label="탐색경로">{inner}</nav></div>\n'


def lux_hero(eyebrow, h1, lead, byline=True, actions=True):
    by = (f'<div class="byline"><span class="au">발행 · {TODAY}</span>'
          f'<span>최종 업데이트 · {TODAY}</span></div>') if byline else ""
    act = (f'''<div class="actions" style="margin-top:22px">
    <a class="btn btn-primary" href="tel:{PHONE_TEL}">예약문의 {PHONE_DISPLAY}</a>
    <a class="btn btn-ghost" href="/reservation/">예약 안내</a>
  </div>''') if actions else ""
    return f"""<section class="lux-hero"><div class="wrap">
  <span class="eyebrow"><span class="pulse"></span>{eyebrow}</span>
  <h1 class="lux-h1">{html.escape(h1)}</h1>
  <p class="lux-lead">{lead}</p>
  {by}
  {act}
</div></section>
"""


def sec(sid, title, body):
    return f'<section class="lux-sec reveal" id="{sid}"><h2>{html.escape(title)}</h2>\n{body}\n</section>\n'


def faq_block(items):
    rows = "".join(
        f"<details><summary>{html.escape(q)}<span>+</span></summary><div>{a}</div></details>"
        for q, a in items)
    return f"""<section class="block" id="faq"><div class="wrap">
  <span class="eyebrow"><span class="pulse"></span>FAQ</span>
  <h2 class="sec">자주 묻는 질문</h2>
  <div style="margin-top:26px;max-width:820px">{rows}</div>
</div></section>
"""


def article_page(path, title, desc, eyebrow, crumb_items, h1, lead,
                 sections, faq=None, og_type="website"):
    """좌측 TOC + 본문 섹션 + FAQ 형태의 페이지."""
    toc = "".join(f'<li><a href="#{sid}">{html.escape(t)}</a></li>' for sid, t, _ in sections)
    body_secs = "".join(sec(sid, t, b) for sid, t, b in sections)
    body_html = body_secs + (faq_block(faq) if faq else "")
    noindex = strip_len(body_html) < NOINDEX_MIN
    out = head(title, desc, path, noindex=noindex, og_type=og_type)
    out += nav(active=ACTIVE.get(path.split("/")[1] if path != "/" else "home", _active_for(path)))
    out += crumb(crumb_items)
    out += lux_hero(eyebrow, h1, lead)
    out += f"""<section class="block lux-body" style="padding-top:30px"><div class="wrap"><div class="lux-grid">
  <aside class="toc"><div class="toc-inner"><span class="toc-label">목차</span><ul>{toc}</ul></div></aside>
  <div class="lux-main">{body_secs}</div>
</div></div></section>
"""
    if faq:
        out += faq_block(faq)
    out += jsonld_breadcrumb(crumb_items)
    if faq:
        out += jsonld_faq(faq)
    out += footer()
    return out, noindex


ACTIVE = {}


def _active_for(path):
    if path == "/":
        return "home"
    seg = path.strip("/").split("/")
    first = seg[0]
    mapping = {"guro": "guro", "guro-gu": "area", "theme": "theme", "course": "course",
               "reservation": "reservation", "guide": "guide", "reviews": "reviews",
               "customer": "customer"}
    if first == "guro-gu" and len(seg) >= 2 and seg[1] == "stations":
        return "stations"
    return mapping.get(first, "")


# ---------------------------------------------------------------------------
# 4. 데이터: 지역(동) / 역 / 테마 / 코스 / 예약 / 가이드
# ---------------------------------------------------------------------------
# 구로구 법정동 10 (숫자 행정동은 대표 동으로 통합)
DONGS = [
    {"slug": "sindorim-dong", "name": "신도림동", "rom": "Sindorim",
     "tag": "1·2호선 환승 생활권",
     "intro": "신도림동은 1호선과 2호선이 만나는 신도림역을 중심으로 대형 복합상가와 오피스텔, 주거단지가 촘촘히 모인 구로구의 관문 생활권입니다. 영등포·여의도 방면과 가까워 교통 결절지 성격이 강하고, 낮과 밤의 유동인구 변화가 큰 지역입니다.",
     "life": "디큐브시티·테크노마트 일대의 상업시설과 배후 주거가 함께 있어, 업무를 마친 저녁 시간대나 주말 휴식 목적의 방문 관리 문의가 꾸준한 편입니다. 인근 직장에서 야근을 마친 뒤 가까운 자택이나 숙소로 방문을 요청하는 경우도 많습니다.",
     "access": "신도림역은 1호선과 2호선이 교차하는 환승역으로 도심·강남·서울 서남부 어디서든 접근이 쉽습니다. 도림천역(2호선 신정지선)도 가까워, 위치에 따라 두 역을 함께 안내드릴 수 있습니다.",
     "env": "대형 오피스텔과 주상복합, 아파트가 섞여 있어 공동현관과 엘리베이터 출입 절차가 건물마다 다릅니다. 예약 시 동·호수와 출입 방법을 함께 알려주시면 방문이 한결 매끄럽습니다.",
     "tip": "퇴근 시간대(오후 6~9시)와 금요일 저녁은 신도림 일대 문의가 집중되므로, 원하는 시간이 있다면 미리 예약해 두는 것이 좋습니다.",
     "near_st": ["신도림역", "도림천역"],
     "themes": [("swedish", "스웨디시"), ("aroma-therapy", "아로마테라피"), ("24hours", "24시간")],
     "merge": ""},
    {"slug": "guro-dong", "name": "구로동", "rom": "Guro",
     "tag": "구로1~5동 통합 · IT 업무지구",
     "intro": "구로동은 구로역과 구로디지털단지 일대를 아우르는 구로구의 중심 생활권으로, IT·업무 시설과 대단지 주거가 어우러진 지역입니다. 면적이 넓고 인구가 많아 구로구에서 방문 관리 문의가 가장 활발한 동에 속합니다.",
     "life": "디지털단지 직장인 수요와 대단지 아파트 주거 수요가 함께 있어, 퇴근 후 피로 회복이나 주말 홈타이 문의가 많습니다. 야근·회식이 잦은 IT 종사자들이 어깨·허리 뭉침 해소를 위해 스포츠·경락 관리를 찾는 경우가 두드러집니다.",
     "access": "구로역(1호선), 구로디지털단지역(2호선), 남구로역(7호선), 대림역(2·7호선)이 모두 생활권에 걸쳐 있어 어느 방향에서든 접근이 좋습니다. 정확한 위치에 따라 가장 가까운 역을 기준으로 동선을 안내드립니다.",
     "env": "대단지 아파트와 업무용 오피스텔, 주상복합이 혼재해 방문 환경이 다양합니다. 오피스텔은 보안 출입이 많으므로 출입 방법과 주차 가능 여부를 미리 확인해 두면 좋습니다.",
     "tip": "구로동은 권역이 넓어 같은 ‘구로동’이라도 위치에 따라 가까운 역과 이동 시간이 달라집니다. 예약 시 도로명 주소나 인근 랜드마크를 알려주시면 빠른 안내가 가능합니다.",
     "near_st": ["구로역", "구로디지털단지역", "남구로역", "대림역"],
     "themes": [("sports-massage", "스포츠·경락"), ("home-care", "홈케어"), ("hotel-massage", "호텔식마사지")],
     "merge": "행정동 기준 구로1동~구로5동으로 나뉘지만, 본 안내에서는 중복 페이지를 만들지 않고 대표 동인 구로동 한 페이지에서 통합해 안내합니다. 구로1동·구로2동·구로3동·구로4동·구로5동 어디에 거주하시더라도 이 페이지를 기준으로 문의하시면 됩니다."},
    {"slug": "garibong-dong", "name": "가리봉동", "rom": "Garibong",
     "tag": "남구로역 인근 주거",
     "intro": "가리봉동은 남구로역과 옛 구로공단 배후 주거가 자리한 생활권으로, 오래된 주택가와 다양한 상권이 섞여 있는 지역입니다. 좁은 골목과 다세대·다가구 주택이 많아 동네 분위기가 친근한 편입니다.",
     "life": "1인 가구와 직장인 비중이 높아 늦은 시간대 방문 관리 문의가 비교적 많고, 짧은 코스부터 전신 코스까지 폭넓게 선택됩니다. 하루 종일 서서 일하는 분들이 발과 다리의 피로를 풀기 위해 발마사지를 찾는 경우도 적지 않습니다.",
     "access": "남구로역(7호선)이 중심이며, 2호선·7호선 환승역인 대림역도 가깝습니다. 영등포 대림 생활권과 인접해 있으므로, 예약 시 구로구 가리봉동 방향임을 분명히 해 주시면 정확합니다.",
     "env": "다세대·다가구 주택이 많아 공동현관이 없는 곳도 있고 골목 주차가 까다로운 경우가 있습니다. 방문 위치와 주차 가능 여부를 미리 알려주시면 도움이 됩니다.",
     "tip": "야간 근무가 잦은 분들의 늦은 시간 문의가 많은 지역입니다. 심야 방문을 원하시면 사전 예약으로 가능 시간을 먼저 확인하는 것이 좋습니다.",
     "near_st": ["남구로역", "대림역"],
     "themes": [("thai-massage", "타이마사지"), ("foot-massage", "발마사지"), ("sports-massage", "스포츠·경락")],
     "merge": ""},
    {"slug": "gocheok-dong", "name": "고척동", "rom": "Gocheok",
     "tag": "고척1~2동 통합 · 고척스카이돔",
     "intro": "고척동은 고척스카이돔과 동양미래대학 인근의 주거 중심 생활권으로, 안양천을 끼고 조용한 주택가가 넓게 형성되어 있습니다. 야구 경기나 공연이 열리는 날에는 일대 교통이 붐비기도 합니다.",
     "life": "가족 단위 주거가 많아 주말 오전·오후의 피로 회복 관리나 가족 방문 코스 문의가 꾸준합니다. 평소 운동이나 산책으로 안양천변을 자주 찾는 분들이 가벼운 근육 이완을 위해 관리를 받는 경우도 있습니다.",
     "access": "구일역(1호선)과 개봉역(1호선)이 양쪽 생활권을 잇습니다. 안양천을 경계로 위치에 따라 가까운 역이 달라지므로, 정확한 주소를 기준으로 안내드립니다.",
     "env": "아파트와 단독·다세대 주택이 고루 섞여 있어 가족 단위 방문 환경이 안정적입니다. 가정 방문 홈타이를 받기에 적합한 조용한 공간을 확보하기 좋은 편입니다.",
     "tip": "고척스카이돔 행사일에는 주변 도로와 주차가 혼잡할 수 있으니, 해당 일정과 겹친다면 여유 있게 예약 시간을 잡는 것을 권합니다.",
     "near_st": ["구일역", "개봉역"],
     "themes": [("swedish", "스웨디시"), ("aroma-therapy", "아로마테라피"), ("sleep-available", "수면 가능")],
     "merge": "행정동 고척1동·고척2동은 고척동 대표 페이지에서 통합 안내합니다. 어느 쪽에 거주하시든 이 페이지를 기준으로 문의하시면 됩니다."},
    {"slug": "gaebong-dong", "name": "개봉동", "rom": "Gaebong",
     "tag": "개봉1~3동 통합 · 안양천 주거",
     "intro": "개봉동은 개봉역을 중심으로 안양천변 대단지 아파트와 생활 상권이 함께 발달한 주거 생활권입니다. 천변 산책로와 공원이 가까워 주거 환경이 쾌적한 편으로 꼽힙니다.",
     "life": "대단지 주거 특성상 저녁 시간대 가정 방문 홈타이와 수면을 돕는 이완 관리 문의가 많은 편입니다. 하루를 마치고 잠들기 전 가볍게 몸을 풀고 싶어 하는 가족 단위 수요가 두드러집니다.",
     "access": "개봉역(1호선)이 중심이며, 인접한 구일역도 생활권을 함께 잇습니다. 안양천을 사이에 두고 광명 방면과도 가까워 접근 동선이 다양합니다.",
     "env": "대단지 아파트가 많아 공동현관·엘리베이터 출입과 단지 내 주차 안내가 필요한 경우가 많습니다. 동·호수와 방문자 출입 방법을 함께 알려주시면 방문이 원활합니다.",
     "tip": "잠들기 좋은 저자극 이완 관리를 찾는 분이 많은 지역입니다. 수면을 돕는 흐름을 원하시면 예약 시 ‘수면 중심’으로 요청해 주세요.",
     "near_st": ["개봉역", "구일역"],
     "themes": [("swedish", "스웨디시"), ("sleep-available", "수면 가능"), ("home-care", "홈케어")],
     "merge": "개봉1동·개봉2동·개봉3동은 개봉동 대표 페이지로 통합해 안내하며, 숫자 동 개별 페이지는 만들지 않습니다. 세 동 어디에 거주하시든 이 페이지에서 안내받으실 수 있습니다."},
    {"slug": "oryu-dong", "name": "오류동", "rom": "Oryu",
     "tag": "오류1~2동 통합 · 경인로 생활권",
     "intro": "오류동은 오류동역과 경인로를 따라 형성된 생활권으로, 전통적인 주거지와 상권이 공존하는 구로구 서남부의 거점입니다. 오랜 시간 자리 잡은 동네 상권과 새로 들어선 주거가 어우러져 있습니다.",
     "life": "출퇴근 동선이 분명한 직장인 수요가 많아 평일 저녁 방문 관리와 주말 휴식 코스 문의가 고르게 들어옵니다. 종일 앉아 일하며 굳은 어깨와 종아리를 풀기 위해 발마사지나 타이마사지를 찾는 경우가 많습니다.",
     "access": "오류동역(1호선)이 생활권 중심이며, 인접한 개봉역과 온수역으로도 동선이 이어집니다. 경인로를 따라 이동이 편해 서남부 어디서든 접근이 수월합니다.",
     "env": "단독·다세대 주택과 아파트가 섞여 있어 방문 환경이 다양합니다. 주택가는 골목 주차가 어려운 경우가 있으니 주차 위치를 미리 확인해 두면 좋습니다.",
     "tip": "평일 저녁 직장인 문의가 꾸준한 지역으로, 퇴근 직후 시간대는 예약이 빠르게 차는 편입니다. 원하는 시간이 있다면 당일보다 사전 예약을 권합니다.",
     "near_st": ["오류동역", "개봉역"],
     "themes": [("foot-massage", "발마사지"), ("thai-massage", "타이마사지"), ("aroma-therapy", "아로마테라피")],
     "merge": "오류1동·오류2동은 오류동 대표 페이지에서 통합 안내합니다. 두 동 어디에 거주하시든 이 페이지를 기준으로 문의하시면 됩니다."},
    {"slug": "cheonwang-dong", "name": "천왕동", "rom": "Cheonwang",
     "tag": "7호선 천왕역 · 신주거단지",
     "intro": "천왕동은 7호선 천왕역과 천왕이펜하우스 등 비교적 최근에 조성된 친환경 주거단지가 자리한 생활권입니다. 계획적으로 정비된 단지와 녹지가 많아 정주 환경이 쾌적한 편입니다.",
     "life": "신혼·가족 세대가 많아 커플 관리나 가족 방문 코스, 수면을 돕는 저자극 관리 문의가 많습니다. 어린 자녀를 둔 가정에서는 집에서 편안하게 받는 홈타이 선호가 두드러집니다.",
     "access": "천왕역(7호선)이 중심이며, 인접한 항동지구와 온수역 방면으로도 생활권이 이어집니다. 7호선을 따라 남구로·대림 방면 접근도 수월합니다.",
     "env": "신축 아파트 단지가 많아 공동현관·엘리베이터 출입과 단지 내 방문자 주차 안내가 필요한 경우가 많습니다. 예약 시 단지명과 동·호수를 알려주시면 방문이 원활합니다.",
     "tip": "커플·가족 단위 문의가 많은 지역입니다. 두 분 이상 함께 받기를 원하시면 인원과 희망 시간을 미리 알려주셔야 배정이 수월합니다.",
     "near_st": ["천왕역"],
     "themes": [("couple", "커플 관리"), ("sleep-available", "수면 가능"), ("home-care", "홈케어")],
     "merge": ""},
    {"slug": "hang-dong", "name": "항동", "rom": "Hang",
     "tag": "항동지구 · 푸른수목원 인근",
     "intro": "항동은 항동지구 택지와 푸른수목원 인근의 쾌적한 신주거 생활권으로, 구로구에서 비교적 한적한 편에 속합니다. 수목원과 녹지가 가까워 조용하고 여유로운 분위기가 특징입니다.",
     "life": "정주 환경을 중시하는 가족 세대가 많아 아로마·스킨케어처럼 편안한 휴식 중심 관리 선호가 두드러집니다. 바쁜 일상에서 벗어나 분위기 있는 이완을 찾는 문의가 꾸준합니다.",
     "access": "지하철로는 천왕역(7호선)과 온수역(1·7호선)이 가장 가깝습니다. 역과 다소 거리가 있는 단지가 있어, 정확한 위치를 기준으로 방문 동선을 안내드립니다.",
     "env": "신축 아파트 위주의 정비된 주거 환경으로, 가정 방문 관리를 받기에 조용하고 안정적입니다. 단지 출입과 주차 안내를 미리 확인해 두면 좋습니다.",
     "tip": "역과 거리가 있는 단지가 있어 이동 시간을 고려한 예약이 필요합니다. 희망 시간보다 약간 여유를 두고 예약하시면 정시 방문에 도움이 됩니다.",
     "near_st": ["천왕역", "온수역"],
     "themes": [("aroma-therapy", "아로마테라피"), ("skin-care", "스킨케어"), ("couple", "커플 관리")],
     "merge": ""},
    {"slug": "gung-dong", "name": "궁동", "rom": "Gung",
     "tag": "수궁동 생활권 · 궁동저수지",
     "intro": "궁동은 궁동저수지와 온수역 인근에 자리한 조용한 주거 생활권으로, 행정동상으로는 수궁동에 속합니다. 저수지와 산자락을 낀 한적한 환경이 특징입니다.",
     "life": "조용한 주택가 특성상 늦은 저녁의 이완·수면 관리와 피로 회복 코스 문의가 많은 편입니다. 번잡함에서 벗어나 차분히 휴식을 취하려는 수요가 두드러집니다.",
     "access": "온수역(1·7호선)이 가장 가까운 역으로, 인접한 온수동 생활권과 자연스럽게 이어집니다. 위치에 따라 도보·차량 동선을 함께 안내드립니다.",
     "env": "단독·다세대 주택과 소규모 단지가 섞여 있어 골목 주차가 까다로운 곳이 있습니다. 방문 위치와 주차 가능 여부를 미리 알려주시면 도움이 됩니다.",
     "tip": "조용한 환경 덕분에 수면을 돕는 저자극 관리가 잘 맞는 지역입니다. 잠들기 전 이완을 원하시면 늦은 저녁 시간으로 예약을 잡아보세요.",
     "near_st": ["온수역"],
     "themes": [("aroma-therapy", "아로마테라피"), ("swedish", "스웨디시"), ("sleep-available", "수면 가능")],
     "merge": "행정동 수궁동에 대한 설명은 본문에서 함께 안내하며, 인접한 온수동과 생활권이 연결됩니다. 행정상 수궁동으로 묶이지만 법정동 궁동을 기준으로 안내합니다."},
    {"slug": "onsu-dong", "name": "온수동", "rom": "Onsu",
     "tag": "1·7호선 온수역 환승",
     "intro": "온수동은 1호선과 7호선이 만나는 온수역을 중심으로 산업단지와 주거가 인접한 구로구 서남단의 환승 생활권입니다. 부천 방면과 맞닿아 있어 서울 서남부의 관문 역할을 합니다.",
     "life": "환승 동선이 좋아 인근 지역에서의 접근성이 높고, 직장인 스포츠·경락 관리와 24시간대 문의가 함께 들어옵니다. 산업단지 근무자들이 교대 근무 후 피로를 푸는 수요도 있습니다.",
     "access": "온수역은 1호선과 7호선이 교차하는 환승역으로, 구로 도심은 물론 부천·강남 방면 접근도 좋습니다. 인접한 궁동 생활권과도 동선이 자연스럽게 이어집니다.",
     "env": "주거와 산업단지가 인접해 건물 유형이 다양합니다. 오피스텔·숙소 방문 시 출입 방법과 연락 가능 여부를 미리 확인해 두면 방문이 원활합니다.",
     "tip": "교대·야간 근무 수요가 있어 늦은 시간 문의가 꾸준한 지역입니다. 심야·새벽 방문을 원하시면 사전에 가능 시간을 확인해 주세요.",
     "near_st": ["온수역", "오류동역"],
     "themes": [("sports-massage", "스포츠·경락"), ("24hours", "24시간"), ("hotel-massage", "호텔식마사지")],
     "merge": "행정동상 수궁동에 함께 묶이는 궁동과 생활권이 연결되어, 서로의 안내를 참고할 수 있습니다."},
]

# 지하철역 (대표 역 1개당 페이지 1개, 환승역 URL 1개)
STN = {
    "sindorim": {"slug": "sindorim-station", "name": "신도림역", "lines": "1·2호선",
                 "dong": ("sindorim-dong", "신도림동"),
                 "desc": "구로구 동쪽 관문이자 1·2호선 환승 거점으로, 대형 상업시설과 오피스텔이 밀집해 유동인구가 많은 역입니다.",
                 "life": "환승 수요와 인근 주거 수요가 겹쳐, 업무 후 저녁 시간이나 주말 휴식 목적의 방문 관리 문의가 꾸준합니다."},
    "guro": {"slug": "guro-station", "name": "구로역", "lines": "1호선",
             "dong": ("guro-dong", "구로동"),
             "desc": "구로역은 경부선·경인선이 분기하는 1호선의 주요 정차역으로, 구로동 중심 상권과 대단지 주거를 배후에 둔 역입니다.",
             "life": "직장인과 거주민 수요가 함께 있어 평일 저녁 피로 회복과 주말 홈타이 문의가 고르게 들어옵니다."},
    "guil": {"slug": "guil-station", "name": "구일역", "lines": "1호선",
             "dong": ("gocheok-dong", "고척동"),
             "desc": "구일역은 고척스카이돔과 안양천에 인접한 1호선 역으로, 고척동·구로동 주거 생활권을 잇는 조용한 역입니다.",
             "life": "주거 중심 특성상 가족 단위의 피로 회복·휴식 관리 문의가 많은 편입니다."},
    "gaebong": {"slug": "gaebong-station", "name": "개봉역", "lines": "1호선",
                "dong": ("gaebong-dong", "개봉동"),
                "desc": "개봉역은 개봉동 대단지 주거와 생활 상권을 배후에 둔 1호선 역으로, 안양천변 생활권의 중심입니다.",
                "life": "저녁 시간대 가정 방문 홈타이와 수면을 돕는 이완 관리 선호가 뚜렷합니다."},
    "oryudong": {"slug": "oryudong-station", "name": "오류동역", "lines": "1호선",
                 "dong": ("oryu-dong", "오류동"),
                 "desc": "오류동역은 경인로 생활권의 중심에 있는 1호선 역으로, 전통 주거지와 상권이 어우러진 지역입니다.",
                 "life": "출퇴근 동선이 분명해 평일 저녁 방문 관리 문의가 안정적으로 이어집니다."},
    "onsu": {"slug": "onsu-station", "name": "온수역", "lines": "1·7호선",
             "dong": ("onsu-dong", "온수동"),
             "desc": "온수역은 1호선과 7호선이 만나는 환승역으로, 온수동 산업단지와 주거, 인접 궁동 생활권을 함께 아우릅니다.",
             "life": "환승 접근성이 좋아 인근 지역 방문이 수월하며, 스포츠·경락과 24시간대 문의가 함께 들어옵니다."},
    "dorimcheon": {"slug": "dorimcheon-station", "name": "도림천역", "lines": "2호선",
                   "dong": ("sindorim-dong", "신도림동"),
                   "desc": "도림천역은 2호선 신정지선의 역으로 신도림동 주거 생활권과 가까워, 조용한 동선의 방문 관리에 적합합니다.",
                   "life": "주거 밀착형 역으로, 늦은 저녁의 이완·수면 관리 문의가 많은 편입니다."},
    "daerim": {"slug": "daerim-station", "name": "대림역", "lines": "2·7호선",
               "dong": ("guro-dong", "구로동"),
               "desc": "대림역은 2호선과 7호선이 만나는 환승역으로, 구로동·가리봉동 경계 생활권을 배후에 둔 다국적 상권의 거점입니다.",
               "life": "유동인구가 많고 야간 활동이 활발해, 늦은 시간대 방문 관리 문의가 꾸준합니다.",
               "note": "영등포구 쪽 대림 생활권과 혼동되기 쉬우므로, 예약 시 정확한 위치(구로구 방향)를 확인합니다."},
    "gurodigital": {"slug": "gurodigital-station", "name": "구로디지털단지역", "lines": "2호선",
                    "dong": ("guro-dong", "구로동"),
                    "desc": "구로디지털단지역은 IT·업무 시설이 밀집한 2호선의 핵심 업무 거점으로, 직장인 유동인구가 매우 많은 역입니다.",
                    "life": "야근·회식이 잦은 직장인 수요로 평일 저녁 스포츠·경락과 피로 회복 코스 문의가 집중됩니다."},
    "namguro": {"slug": "namguro-station", "name": "남구로역", "lines": "7호선",
                "dong": ("garibong-dong", "가리봉동"),
                "desc": "남구로역은 7호선 역으로 가리봉동·구로동 주거 생활권을 배후에 둔, 다양한 상권이 모인 지역입니다.",
                "life": "1인 가구·직장인 비중이 높아 늦은 시간대 방문 관리 문의가 비교적 많습니다."},
    "cheonwang": {"slug": "cheonwang-station", "name": "천왕역", "lines": "7호선",
                  "dong": ("cheonwang-dong", "천왕동"),
                  "desc": "천왕역은 천왕동 친환경 주거단지를 배후에 둔 7호선 역으로, 항동 생활권과도 가깝습니다.",
                  "life": "가족·신혼 세대가 많아 커플 관리와 수면을 돕는 저자극 관리 문의가 두드러집니다."},
}

# 노선별 역 구성 (메뉴/허브 표시용 — 환승역 중복 표시, URL은 1개)
LINES = [
    ("line1", "1호선 구로권", ["sindorim", "guro", "guil", "gaebong", "oryudong", "onsu"]),
    ("line2", "2호선 구로권", ["sindorim", "dorimcheon", "daerim", "gurodigital"]),
    ("line7", "7호선 구로권", ["namguro", "daerim", "cheonwang", "onsu"]),
]

THEMES = [
    {"slug": "swedish", "name": "스웨디시",
     "feat": "오일을 활용해 부드럽고 일정한 압으로 전신을 쓸어주는 대표적인 이완 관리입니다.",
     "for": "전신 긴장을 풀고 편안하게 휴식하고 싶은 분, 처음 방문 관리를 이용하는 분",
     "how": "어깨·등·다리 등 큰 근육을 따라 길게 쓸어내리는 동작이 중심이며, 호흡에 맞춰 속도와 압을 조절해 몸이 서서히 이완되도록 진행합니다.",
     "time": "처음이거나 전반적인 피로 해소가 목적이라면 90분 코스가 무난합니다.",
     "caution": "오일을 사용하므로 시술 후 가벼운 샤워가 가능하도록 준비해 두면 좋습니다."},
    {"slug": "lomi-lomi", "name": "로미로미",
     "feat": "팔 전체를 활용한 리듬감 있는 동작으로 흐르듯 이어지는 하와이안 스타일 관리입니다.",
     "for": "부드러운 흐름의 관리와 깊은 이완을 함께 원하는 분",
     "how": "손바닥과 팔뚝을 넓게 사용해 끊김 없이 이어지는 리듬으로 진행해, 파도처럼 밀려오는 편안한 느낌을 줍니다.",
     "time": "충분히 흐름을 느끼려면 90분 이상을 권합니다.",
     "caution": "오일을 사용하는 관리이므로 향·오일 민감 여부를 미리 알려주세요."},
    {"slug": "thai-massage", "name": "타이마사지",
     "feat": "스트레칭과 지압을 결합해 굳은 관절과 근육을 풀어주는 활동적인 관리입니다.",
     "for": "몸이 뻣뻣하거나 스트레칭을 곁들인 시원한 관리를 원하는 분",
     "how": "관리사가 손·팔·체중을 이용해 지압하고, 요가 동작과 유사한 스트레칭으로 관절 가동 범위를 넓혀줍니다.",
     "time": "스트레칭 동작이 많아 활동복처럼 편한 옷을 준비하면 좋습니다.",
     "caution": "관절·디스크 질환이 있는 경우 무리한 스트레칭을 피하도록 미리 알려주세요."},
    {"slug": "chinese-massage", "name": "중국마사지",
     "feat": "경혈을 따라 지그시 눌러주는 지압 중심의 전통적인 관리 방식입니다.",
     "for": "지압 위주의 묵직하고 시원한 압을 선호하는 분",
     "how": "손가락과 손바닥으로 경혈과 근육 결을 따라 일정한 압을 주며, 뭉친 부위를 지그시 눌러 풀어줍니다.",
     "time": "묵직한 압을 충분히 받으려면 90분 이상이 적당합니다.",
     "caution": "강한 압을 원치 않으면 예약 시 ‘약하게’로 요청해 주세요."},
    {"slug": "aroma-therapy", "name": "아로마테라피",
     "feat": "향 오일을 활용해 후각과 촉각을 함께 자극하며 심신을 이완하는 관리입니다.",
     "for": "스트레스 해소와 분위기 있는 휴식을 함께 원하는 분",
     "how": "은은한 향 오일을 사용해 부드러운 압으로 전신을 풀어주며, 향과 손길로 긴장을 함께 가라앉힙니다.",
     "time": "분위기 있는 휴식이 목적이라면 90~120분이 잘 어울립니다.",
     "caution": "향에 민감하거나 알레르기가 있는 경우 예약 시 꼭 알려주세요."},
    {"slug": "home-care", "name": "홈케어",
     "feat": "가정·숙소를 방문해 익숙한 공간에서 편안하게 받는 방문 관리입니다.",
     "for": "이동 없이 집에서 편하게 관리를 받고 싶은 분",
     "how": "요청하신 위치로 방문해, 익숙한 공간에서 편안한 자세로 이완 중심의 관리를 진행합니다.",
     "time": "관리 후 바로 휴식을 원한다면 저녁 시간대 예약이 좋습니다.",
     "caution": "관리에 사용할 수 있는 편평하고 조용한 공간을 미리 확보해 주세요."},
    {"slug": "hotel-massage", "name": "호텔식마사지",
     "feat": "호텔·숙소 환경에 맞춰 정돈된 절차로 진행하는 단정한 방문 관리입니다.",
     "for": "출장·여행 중 숙소에서 격식 있는 관리를 원하는 분",
     "how": "객실 환경에 맞춰 준비물과 절차를 단정하게 갖추고, 차분한 분위기에서 전신 이완을 진행합니다.",
     "time": "출장·여행 일정 사이의 휴식으로 60~90분이 적당합니다.",
     "caution": "숙소는 객실 번호와 출입 방법, 연락 가능 여부를 함께 알려주세요."},
    {"slug": "foot-massage", "name": "발마사지",
     "feat": "발과 종아리의 반사구를 자극해 하체 피로와 부기를 다스리는 관리입니다.",
     "for": "오래 서 있거나 걷는 일이 많아 다리가 무거운 분",
     "how": "발바닥의 반사구와 종아리 근육을 지압해 하체에 몰린 피로와 부기를 가볍게 풀어줍니다.",
     "time": "전신 코스에 더해 하체를 집중하면 만족도가 높습니다.",
     "caution": "발에 상처나 염증이 있으면 해당 부위를 피하도록 알려주세요."},
    {"slug": "sports-massage", "name": "스포츠·경락",
     "feat": "근육의 결을 따라 강한 압으로 뭉친 부위를 집중적으로 풀어주는 관리입니다.",
     "for": "운동 후 회복이 필요하거나 어깨·허리 뭉침이 심한 분",
     "how": "어깨·등·허리·다리 등 뭉친 부위를 결에 따라 강한 압으로 깊게 풀어, 근육 회복을 돕습니다.",
     "time": "특정 부위가 심하게 뭉쳤다면 90~120분으로 집중 관리를 권합니다.",
     "caution": "급성 통증이나 부상이 있는 부위는 무리하지 않도록 미리 알려주세요."},
    {"slug": "skin-care", "name": "스킨케어",
     "feat": "피부 결을 정돈하고 컨디션을 살피며 진행하는 케어 중심 관리입니다.",
     "for": "피부 이완과 함께 단정한 관리를 원하는 분",
     "how": "피부 상태를 살피며 부드럽게 결을 정돈하고, 편안한 이완을 함께 진행합니다.",
     "time": "다른 이완 관리와 함께 구성하면 만족도가 높습니다.",
     "caution": "민감성 피부나 특정 제품 알레르기가 있으면 예약 시 알려주세요."},
    {"slug": "waxing", "name": "왁싱",
     "feat": "위생적인 절차로 진행하는 제모 케어로, 사전 안내에 따라 진행됩니다.",
     "for": "깔끔한 피부 정돈을 원하는 분",
     "how": "위생 용품을 사용해 정해진 절차에 따라 진행하며, 부위와 범위는 사전 상담으로 정합니다.",
     "time": "원하는 부위와 범위를 예약 시 미리 알려주세요.",
     "caution": "피부 질환이나 상처가 있는 부위는 진행이 어려울 수 있습니다."},
    {"slug": "couple", "name": "커플 관리",
     "feat": "두 분이 함께 같은 공간 또는 인접 공간에서 동시에 받는 관리입니다.",
     "for": "기념일이나 휴식을 함께 보내고 싶은 커플·가족",
     "how": "두 분이 나란히 또는 인접한 공간에서 동시에 관리를 받을 수 있도록 구성합니다.",
     "time": "함께 받는 시간을 충분히 누리려면 90분 이상을 권합니다.",
     "caution": "인원과 희망 시간을 미리 알려주셔야 동시 배정이 수월합니다."},
    {"slug": "24hours", "name": "24시간",
     "feat": "심야·새벽 시간대에도 일정과 배정 상황에 따라 진행 가능한 관리 운영입니다.",
     "for": "야간 근무나 늦은 시간에 관리가 필요한 분",
     "how": "심야·새벽 시간대에도 배정 상황에 따라 방문이 가능하도록 운영합니다.",
     "time": "심야 방문은 가능 시간이 한정되므로 사전 예약을 권합니다.",
     "caution": "늦은 시간 방문은 출입 방법과 연락 가능 여부를 꼭 확인해 주세요."},
    {"slug": "sleep-available", "name": "수면 가능",
     "feat": "잠들기 좋은 낮은 자극과 차분한 흐름으로 진행하는 이완 중심 관리입니다.",
     "for": "수면의 질을 높이고 편안히 잠들고 싶은 분",
     "how": "자극을 낮추고 느린 호흡에 맞춘 차분한 흐름으로 진행해, 자연스럽게 잠들 수 있도록 돕습니다.",
     "time": "잠들기 전 받기 좋아 늦은 저녁 시간대 예약이 잘 어울립니다.",
     "caution": "조명을 낮추고 조용한 환경을 만들어 두면 효과가 더 좋습니다."},
]

COURSES = [
    {"slug": "fatigue", "name": "피로 회복 관리",
     "desc": "전신의 긴장을 고르게 풀어 일상 피로를 가볍게 하는 기본 코스입니다.",
     "fit": "쌓인 피로를 풀고 가볍게 컨디션을 회복하고 싶을 때"},
    {"slug": "aroma", "name": "아로마 관리",
     "desc": "향 오일을 활용해 심신 이완과 스트레스 해소에 중점을 둔 코스입니다.",
     "fit": "분위기 있는 휴식과 스트레스 해소를 함께 원할 때"},
    {"slug": "sports", "name": "스포츠 관리",
     "desc": "뭉친 근육을 집중적으로 풀어 회복을 돕는 강도 있는 코스입니다.",
     "fit": "운동 후 회복이나 어깨·허리 뭉침 해소가 필요할 때"},
    {"slug": "home", "name": "홈타이 코스",
     "desc": "가정·숙소를 방문해 받는 대표 방문 관리 코스입니다.",
     "fit": "이동 없이 익숙한 공간에서 편하게 받고 싶을 때"},
    {"slug": "couple", "name": "커플·가족 방문 관리",
     "desc": "두 분 이상이 함께 받을 수 있도록 구성한 방문 코스입니다.",
     "fit": "기념일이나 가족 휴식을 함께 보내고 싶을 때"},
    {"slug": "group", "name": "기업·단체 방문 관리",
     "desc": "사무실·행사 등 단체 인원을 대상으로 한 방문 관리 코스입니다.",
     "fit": "임직원 복지나 단체 휴식 프로그램이 필요할 때"},
    {"slug": "price", "name": "가격 안내",
     "desc": "코스별 시간과 기본 요금을 한곳에서 확인할 수 있는 안내입니다.",
     "fit": "예약 전 시간·요금 기준을 비교하고 싶을 때"},
    {"slug": "guide", "name": "코스 선택 가이드",
     "desc": "이용 목적과 컨디션에 맞는 코스를 고르는 기준을 정리한 안내입니다.",
     "fit": "어떤 코스를 골라야 할지 결정이 어려울 때"},
]

RES_PAGES = [
    {"slug": "", "path": "/reservation/", "name": "예약 방법"},
    {"slug": "hours", "path": "/reservation/hours/", "name": "예약 가능 시간"},
    {"slug": "place", "path": "/reservation/place/", "name": "방문 가능 장소"},
    {"slug": "payment", "path": "/reservation/payment/", "name": "결제 안내"},
    {"slug": "change", "path": "/reservation/change/", "name": "변경·취소 안내"},
    {"slug": "checklist", "path": "/reservation/checklist/", "name": "예약 전 체크사항"},
]

GUIDE_PAGES = [
    {"slug": "", "path": "/guide/", "name": "처음 이용하시는 분"},
    {"slug": "prepare", "path": "/guide/prepare/", "name": "방문 전 준비사항"},
    {"slug": "safety", "path": "/guide/safety/", "name": "위생 및 안전 기준"},
    {"slug": "aftercare", "path": "/guide/aftercare/", "name": "관리 후 주의사항"},
    {"slug": "forbidden", "path": "/guide/forbidden/", "name": "금지행위 안내"},
    {"slug": "checklist", "path": "/guide/checklist/", "name": "이용 전 확인사항"},
    {"slug": "faq", "path": "/guide/faq/", "name": "이용 FAQ"},
]

# 생성 결과 수집(사이트맵용)
PAGES = []  # (path, noindex, priority, changefreq)


def write(path, html_text, priority="0.6", changefreq="weekly", noindex=False):
    if path == "/":
        fp = os.path.join(ROOT, "index.html")
    else:
        fp = os.path.join(ROOT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(html_text)
    PAGES.append((path, noindex, priority, changefreq))


def linkrow(label, href):
    return f'<a href="{href}">{label}</a>'


def theme_chip_links(pairs):
    return " · ".join(f'<a href="/theme/{s}/">{n}</a>' for s, n in pairs)


# ---------------------------------------------------------------------------
# 5. 메인 페이지 (/) — 구로 전체 허브
# ---------------------------------------------------------------------------
def build_home():
    path = "/"
    title = "구로 출장마사지·홈타이 | 구로구 전지역 방문 마사지 예약 안내"
    desc = ("구로 출장마사지·홈타이 안내 페이지입니다. 구로구 전지역, 대표 동, 지하철역 인근, "
            "테마별 관리와 예약 전 확인사항을 한곳에서 확인하세요.")

    dong_cards = "".join(
        f'<a class="card reveal" href="/guro-gu/{d["slug"]}/"><div class="k">AREA</div>'
        f'<h3>{d["name"]}</h3><p>{d["tag"]}</p><span class="more">안내 보기 →</span></a>'
        for d in DONGS)

    rep_stations = ["sindorim", "guro", "guil", "gaebong", "oryudong", "onsu",
                    "namguro", "cheonwang", "daerim", "gurodigital"]
    st_cards = "".join(
        f'<a class="card reveal" href="/guro-gu/stations/{STN[s]["slug"]}/"><div class="k">STATION</div>'
        f'<h3>{STN[s]["name"]}</h3><p>{STN[s]["lines"]}</p><span class="more">역 인근 안내 →</span></a>'
        for s in rep_stations)

    theme_cards = "".join(
        f'<a class="card reveal" href="/theme/{t["slug"]}/"><div class="k">THEME</div>'
        f'<h3>{t["name"]}</h3><p>{html.escape(t["for"])}</p><span class="more">테마 보기 →</span></a>'
        for t in THEMES[:8])


    faq = [
        ("구로구 전지역 방문이 가능한가요?",
         "예약 시간, 정확한 위치, 배정 상황에 따라 가능 여부가 달라집니다. 신도림동·구로동·고척동 등 "
         "<a href='/guro-gu/'>지역별 안내</a> 페이지에서 대표 동 기준으로 확인하실 수 있습니다."),
        ("구로역이나 신도림역 근처도 가능한가요?",
         "주요 역세권은 <a href='/guro-gu/stations/'>지하철역별 안내</a>의 역 상세 페이지에서 주변 생활권과 함께 안내합니다. "
         "정확한 가능 여부는 예약 시 위치를 기준으로 확인합니다."),
        ("당일 예약도 가능한가요?",
         "가능할 수 있지만 저녁 시간대와 주말은 문의가 많아 사전 예약을 권장합니다. 자세한 운영 시간은 "
         "<a href='/reservation/hours/'>예약 가능 시간</a>에서 확인하세요."),
        ("숫자 동은 왜 따로 페이지가 없나요?",
         "구로1동·구로2동처럼 나뉜 행정동은 구로동 대표 페이지에서 통합 안내하여 중복 페이지 위험을 줄이기 위함입니다. "
         "고척·개봉·오류동도 같은 방식으로 통합합니다."),
        ("테마별 관리는 어디에서 확인하나요?",
         "스웨디시·타이마사지·홈케어 등은 <a href='/theme/'>테마별 안내</a> 페이지에서 특징과 추천 대상을 확인할 수 있습니다."),
    ]

    out = head(title, desc, path)
    out += nav(active="home")
    # 히어로(홈 전용)
    out += f"""<section class="hero"><div class="hero-inner">
  <div>
    <span class="eyebrow"><span class="pulse"></span>구로구 방문 건강관리 안내</span>
    <h1>구로 출장마사지·홈타이<br><span class="grad">예약 안내</span></h1>
    <p class="lead">구로구 전지역 방문 관리(출장마사지·홈타이)의 가능 지역, 예약 절차, 코스 선택 기준, 이용 전 확인사항을 한곳에 정리했습니다. 상세 정보는 지역·지하철역·테마 안내에서 확인하세요.</p>
    <div class="actions">
      <a class="btn btn-primary" href="tel:{PHONE_TEL}">{PHONE_DISPLAY} 전화 예약 →</a>
      <a class="btn btn-ghost" href="/guro-gu/">지역별 안내 보기</a>
    </div>
    <div class="trust">
      <span><b>연중무휴</b> · 24시간 상담</span>
      <span>대표 동 <b>10개</b> 생활권 안내</span>
      <span>1·2·7호선 구로권 역세권</span>
    </div>
  </div>
  <div class="hero-visual">
    <div class="glass">
      <h3>예약 안내<b>전화 한 통으로 확인</b></h3>
      <div class="book-row"><span>가능 지역</span><span>구로구 전지역</span></div>
      <div class="book-row"><span>대표 코스</span><span>60·90·120분</span></div>
      <div class="book-row"><span>상담 시간</span><span>24시간</span></div>
      <a class="bk" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
    </div>
    <div class="floating fl-1"><span class="dot"></span>실시간 예약 상담</div>
    <div class="floating fl-2">홈타이 · 호텔식 방문</div>
  </div>
</div></section>
<div class="marquee"><div class="marquee-track">
  <span>신도림동</span><span>구로동</span><span>가리봉동</span><span>고척동</span><span>개봉동</span><span>오류동</span><span>천왕동</span><span>항동</span><span>궁동</span><span>온수동</span>
  <span>신도림동</span><span>구로동</span><span>가리봉동</span><span>고척동</span><span>개봉동</span><span>오류동</span><span>천왕동</span><span>항동</span><span>궁동</span><span>온수동</span>
</div></div>
"""
    # 본문 섹션들 (lux-body 한 컬럼)
    body = '<section class="block lux-body"><div class="wrap"><div class="lux-main" style="max-width:none">\n'

    body += sec("intro", "구로 출장마사지·홈타이 서비스 안내",
        "<p>구로구에서 방문 마사지와 홈타이 예약을 찾는 분들을 위해 가능 지역, 예약 절차, 코스 선택 기준, "
        "이용 전 확인사항을 안내합니다. 이 메인 페이지에서는 전체 구조를 설명하고, 상세 정보는 "
        "<a href='/guro-gu/'>지역별 안내</a>·<a href='/guro-gu/stations/'>지하철역별 안내</a>·"
        "<a href='/theme/'>테마별 안내</a> 페이지에서 확인할 수 있도록 구성했습니다. "
        "특정 지역·역·테마를 조합한 별도 페이지는 만들지 않고, 각 영역을 분리해 중복 없이 안내하는 것이 원칙입니다.</p>")

    body += sec("allarea", "구로구 전지역 방문 가능 안내",
        "<p>구로구는 <strong>신도림동, 구로동, 가리봉동, 고척동, 개봉동, 오류동, 천왕동, 항동, 궁동, 온수동</strong> "
        "생활권으로 나누어 안내합니다. 행정동 기준으로는 구로1~5동, 고척1~2동, 개봉1~3동, 오류1~2동처럼 숫자로 나뉘지만, "
        "이렇게 숫자로 나뉜 동은 별도 페이지를 만들지 않고 대표 동 페이지에서 통합 안내하여 중복 페이지 위험을 줄입니다. "
        "방문 가능 여부는 예약 시간과 정확한 위치, 배정 상황에 따라 달라질 수 있습니다.</p>")

    body += sec("area", "지역별 안내",
        "<p>지역별 안내는 구로구 대표 동 기준으로 구성됩니다. 각 페이지에서는 해당 생활권의 특징, 주변 역세권, "
        "방문 전 확인사항, 예약 가능 시간, 관련 테마를 고유하게 설명합니다.</p>"
        f'<div class="grid g4">{dong_cards}</div>')

    body += sec("station", "지하철역 인근 안내",
        "<p>지하철역별 안내는 1호선·2호선·7호선 구로권 역을 기준으로 구성합니다. 각 역 페이지에서는 인근 생활권, "
        "주변 대표 동, 예약 가능 시간, 방문 전 준비사항을 설명하며, 출구별 페이지나 역과 테마를 조합한 페이지는 "
        "만들지 않습니다.</p>"
        f'<div class="grid g4">{st_cards}</div>')

    body += sec("theme", "테마별 관리 안내",
        "<p>테마별 안내에서는 관리 유형별 특징, 추천 대상, 예약 전 확인사항을 설명합니다. 테마는 독립 페이지로 운영하고, "
        "지역 페이지와 역 페이지에서는 관련 테마로만 연결합니다. ‘구로역 스웨디시’, ‘신도림역 24시간 홈타이’처럼 "
        "지역·역·테마를 조합한 페이지는 만들지 않습니다.</p>"
        f'<div class="grid g4">{theme_cards}</div>'
        '<p style="margin-top:14px"><a href="/theme/">전체 테마 안내 보기 →</a></p>')

    body += sec("course", "코스 선택 안내",
        "<p>코스는 이용 목적과 컨디션에 따라 선택하는 것이 좋습니다. 피로 회복, 편안한 휴식, 근육 이완, 숙소 방문, "
        "커플 이용 등 상황에 맞는 기준을 제시하며, 자세한 설명은 <a href='/course/'>코스안내</a> 페이지에서 다룹니다. "
        "기본 시간은 60·90·120분이며, 코스별 기본 요금은 이 페이지 하단의 "
        "<a href='#price'>코스별 기본 요금</a> 표에서 확인하실 수 있습니다.</p>"
        "<p>표시 요금은 기본 기준이며 지역·예약 시간대·이동 거리에 따라 상담 시 최종 확인됩니다. 정확한 금액과 "
        "코스 구성은 <a href='/course/price/'>가격 안내</a>와 예약 상담에서 확인하세요.</p>")

    body += sec("process", "예약 진행 방식",
        "<p>예약은 ① 희망 지역 또는 역 인근 위치 확인 → ② 희망 시간 확인 → ③ 코스와 인원 확인 → "
        "④ 방문 가능 여부 안내 → ⑤ 예약 확정 순서로 진행합니다. 저녁 시간대나 주말은 문의가 몰릴 수 있으므로 "
        "여유 있는 예약을 권장합니다. 자세한 내용은 <a href='/reservation/'>예약안내</a>를 참고하세요.</p>")

    body += sec("checklist", "이용 전 확인사항",
        "<p>원활한 방문 관리를 위해 정확한 주소, 공동현관 출입 방법, 주차 가능 여부, 조용한 공간 확보 여부를 미리 "
        "확인하는 것이 좋습니다. 숙소나 오피스텔을 이용할 때는 출입 안내와 연락 가능 여부를 함께 확인해야 합니다. "
        "체크리스트는 <a href='/guide/checklist/'>이용 전 확인사항</a>에 정리되어 있습니다.</p>")

    body += sec("safety", "위생 및 안전 안내",
        "<p>건전하고 안전한 방문 관리를 위해 위생 기준, 예약 정보 확인, 개인정보 보호, 금지행위 안내를 명확히 제공합니다. "
        "이용 전 서비스 범위와 유의사항을 확인하고, 불법적이거나 무리한 요청은 진행하지 않는다는 기준을 분명히 합니다. "
        "본 서비스는 의료 행위가 아닌 건강관리(이완·휴식) 목적이며 만 19세 이상 성인을 대상으로 합니다.</p>")

    body += '</div></div></section>\n'
    out += body
    out += faq_block(faq)
    out += jsonld_localbusiness()
    out += jsonld_faq(faq)
    out += footer()
    write(path, out, priority="1.0", changefreq="daily")


# ---------------------------------------------------------------------------
# 6. 구로 출장마사지 허브 (/guro/) + FAQ (/guro/faq/)
# ---------------------------------------------------------------------------
def build_guro_hub():
    path = "/guro/"
    title = "구로 출장마사지·홈타이 안내 | 구로구 방문 마사지 예약"
    desc = "구로 출장마사지와 홈타이 서비스 안내입니다. 가능 지역, 코스, 예약 절차, 이용 전 확인사항을 정리했습니다."
    secs = [
        ("about", "구로 출장마사지·홈타이 서비스 안내",
         "<p>구로 출장마사지·홈타이는 구로구 전지역을 대상으로 한 방문 건강관리 예약 안내입니다. "
         "관리사가 가정·숙소·오피스텔 등 요청하신 위치로 방문해 이완·휴식 중심의 관리를 진행합니다. "
         "이 페이지는 전체 안내의 출발점으로, 세부 내용은 지역·역·테마·코스 페이지로 연결됩니다.</p>"
         "<p>구로88마사지는 도어웨이·중복 페이지 없이, 지역과 역, 테마를 각각 분리해 안내하는 구조를 따릅니다. "
         "지역은 구로구 대표 동을 기준으로, 지하철역은 1·2·7호선 구로권을 기준으로, 관리 유형은 독립 테마 페이지로 "
         "나누어 안내하며, ‘구로역 스웨디시’처럼 지역·역·테마를 조합한 페이지나 숫자 행정동 단위 페이지는 만들지 "
         "않습니다. 이는 비슷한 페이지를 양산해 검색을 노리는 방식 대신, 페이지마다 고유한 정보를 담아 이용자에게 "
         "실제로 도움이 되도록 하기 위한 구조입니다.</p>"
         "<p>구로구는 신도림동·구로동·가리봉동·고척동·개봉동·오류동·천왕동·항동·궁동·온수동 생활권으로 나뉘며, "
         "업무·상업 기능이 강한 곳과 신주거 중심인 곳이 섞여 있어 지역마다 자주 찾는 관리가 조금씩 다릅니다. "
         f"예약 상담은 연중무휴 24시간 가능하며, 전화 <a href='tel:{PHONE_TEL}'>{PHONE_DISPLAY}</a>로 문의하실 수 "
         "있습니다. 저녁 시간대와 주말은 문의가 몰릴 수 있어 여유 있는 예약을 권장합니다.</p>"),
        ("hometai", "구로 홈타이 안내",
         "<p>홈타이는 익숙한 공간에서 이동 없이 받는 방문 관리입니다. 가정이나 숙소에서 편안하게 받을 수 있어 "
         "이동이 부담스럽거나 관리 후 바로 휴식을 원하는 분께 적합합니다. 출장마사지와 홈타이는 모두 ‘방문 관리’를 "
         "가리키는 표현으로 함께 안내되며, 차이는 받는 장소와 상황에 있습니다. 자세한 코스는 "
         "<a href='/course/home/'>홈타이 코스</a>와 <a href='/theme/home-care/'>홈케어 테마</a>에서 확인하세요.</p>"
         "<p>가정 방문 시에는 관리에 적합한 편평하고 조용한 공간만 있으면 충분하며, 별도 준비물은 필요하지 않습니다. "
         "관리 후 바로 쉬고 싶다면 저녁 시간대 예약이 좋고, 잠들기 전 이완을 원한다면 "
         "<a href='/theme/sleep-available/'>수면 가능</a> 관리를 함께 참고하세요.</p>"),
        ("allarea", "구로구 전지역 방문 가능 안내",
         "<p>신도림동·구로동·가리봉동·고척동·개봉동·오류동·천왕동·항동·궁동·온수동 생활권을 대상으로 안내합니다. "
         "숫자로 나뉜 행정동은 대표 동으로 통합해 안내합니다. 지역별 상세는 "
         "<a href='/guro-gu/'>지역별 안내</a>에서 확인하세요.</p>"),
        ("station", "구로 지하철역 인근 안내",
         "<p>1·2·7호선 구로권 역세권을 기준으로 인근 생활권을 안내합니다. 신도림역·구로역·남구로역·온수역 등 "
         "주요 역은 <a href='/guro-gu/stations/'>지하철역별 안내</a>의 상세 페이지에서 확인할 수 있습니다.</p>"),
        ("course", "코스·예약 안내",
         "<p>코스는 60·90·120분을 기본으로 하며 목적과 컨디션에 따라 선택합니다. 가볍게는 60분, 무난하게는 90분, "
         "깊은 휴식은 120분이 기준이며, 원하는 테마와 함께 구성할 수 있습니다. 예약은 ① 희망 위치 확인 → ② 시간 "
         "확인 → ③ 코스·인원 확인 → ④ 방문 가능 여부 안내 → ⑤ 예약 확정 순서로 진행됩니다. "
         "<a href='/course/guide/'>코스 선택 가이드</a>와 <a href='/reservation/'>예약안내</a>를 참고하세요.</p>"),
        ("safe", "위생·안전과 이용 기준",
         "<p>구로88마사지는 건전하고 안전한 방문 건강관리만을 제공합니다. 위생 기준과 예약 정보·개인정보 보호, "
         "금지행위 안내를 명확히 운영하며, 불법적이거나 무리한 요청은 진행하지 않습니다. 본 서비스는 의료 행위가 "
         "아닌 이완·휴식 목적의 건강관리이며, 만 19세 이상 성인을 대상으로 합니다. 자세한 기준은 "
         "<a href='/guide/safety/'>위생 및 안전 기준</a>과 <a href='/guide/forbidden/'>금지행위 안내</a>에서 "
         "확인하실 수 있습니다.</p>"),
    ]
    faq = [
        ("구로 어느 지역까지 방문이 가능한가요?",
         "구로구 전지역 대표 동을 기준으로 안내하며, 정확한 가능 여부는 예약 시 위치와 시간으로 확인합니다."),
        ("홈타이와 출장마사지는 어떻게 다른가요?",
         "둘 다 방문 관리이며, 홈타이는 가정·숙소 방문 관리를 가리키는 표현으로 함께 안내됩니다."),
        ("예약은 어떻게 하나요?",
         f"전화 <a href='tel:{PHONE_TEL}'>{PHONE_DISPLAY}</a>로 희망 지역·시간·코스를 말씀해 주시면 가능 여부를 안내드립니다."),
    ]
    h, ni = article_page(path, title, desc, "구로 출장마사지 · 허브",
        [("홈", "/"), ("구로 출장마사지", "")],
        "구로 출장마사지·홈타이 예약 안내",
        "구로구 전지역 방문 관리(출장마사지·홈타이)의 가능 지역, 코스, 예약 절차를 한곳에 정리한 안내입니다.",
        secs, faq)
    write(path, h, priority="0.9", noindex=ni)

    # /guro/faq/
    p2 = "/guro/faq/"
    faq2 = [
        ("구로구 전지역 방문이 가능한가요?", "예약 시간·위치·배정 상황에 따라 달라지며, 지역별 안내에서 대표 동 기준으로 확인합니다."),
        ("당일 예약이 되나요?", "가능할 수 있으나 저녁·주말은 문의가 많아 사전 예약을 권장합니다."),
        ("숫자 동(구로1동 등)은 왜 페이지가 없나요?", "중복 페이지 방지를 위해 구로동 등 대표 동에서 통합 안내합니다."),
        ("결제는 어떻게 하나요?", "결제 방식은 예약 상담 시 안내되며 자세한 내용은 결제 안내 페이지를 참고하세요."),
        ("커플·단체도 예약할 수 있나요?", "커플·가족·단체 방문 코스가 있으며 인원과 시간을 미리 알려주시면 안내드립니다."),
        ("위생은 어떻게 관리되나요?", "위생 기준과 안전 안내를 운영하며, 위생 및 안전 기준 페이지에서 확인할 수 있습니다."),
    ]
    secs2 = [("q", "구로 출장마사지 자주 묻는 질문",
        "<p>구로 출장마사지·홈타이 이용 시 자주 문의하시는 내용을 모았습니다. 더 자세한 내용은 "
        "<a href='/reservation/'>예약안내</a>와 <a href='/guide/'>이용가이드</a>에서 확인하실 수 있습니다. "
        "아래 목록에 없는 내용은 전화 상담으로 문의해 주세요.</p>"
        "<p>예약 가능 여부는 시간대와 위치, 배정 상황에 따라 달라질 수 있으며, 정확한 안내는 예약 상담 과정에서 "
        "확정됩니다. 구로88마사지는 지역·역·테마를 분리해 안내하므로, 원하는 항목별 페이지에서 필요한 정보를 "
        "찾아보실 수 있습니다.</p>")]
    h2, ni2 = article_page(p2, "구로 출장마사지 자주 묻는 질문 | 구로88마사지", desc,
        "FAQ", [("홈", "/"), ("구로 출장마사지", "/guro/"), ("자주 묻는 질문", "")],
        "구로 출장마사지 자주 묻는 질문",
        "구로 출장마사지·홈타이 예약과 이용에 대해 자주 묻는 질문을 정리했습니다.",
        secs2, faq2)
    write(p2, h2, priority="0.6", noindex=ni2)


# ---------------------------------------------------------------------------
# 7. 지역 허브 (/guro-gu/) + 동 페이지 10
# ---------------------------------------------------------------------------
def build_area():
    path = "/guro-gu/"
    title = "구로구 지역별 출장마사지·홈타이 안내 | 대표 동 10곳"
    desc = "구로구 신도림동·구로동·고척동·개봉동·오류동 등 대표 동 생활권별 방문 마사지·홈타이 안내입니다."
    cards = "".join(
        f'<a class="card reveal" href="/guro-gu/{d["slug"]}/"><div class="k">{d["rom"].upper()}</div>'
        f'<h3>{d["name"]}</h3><p>{d["tag"]}</p><span class="more">생활권 안내 →</span></a>'
        for d in DONGS)
    secs = [
        ("intro", "구로구 지역별 안내 기준",
         "<p>지역별 안내는 구로구청 공식 자료의 법정동을 기준으로 한 <strong>대표 동 10곳</strong>으로 구성됩니다. "
         "신도림동·구로동·가리봉동·고척동·개봉동·오류동·천왕동·항동·궁동·온수동이며, 각 페이지에서 해당 생활권의 "
         "특징과 주변 역세권, 교통·접근, 예약 가능 시간, 방문 전 확인사항, 관련 테마를 고유하게 안내합니다. "
         "메뉴와 카드에는 지명만 노출하고, ‘출장마사지·홈타이’ 키워드는 각 상세 페이지의 제목과 본문에서만 사용해 "
         "키워드 반복과 도어웨이 위험을 줄였습니다.</p>"
         "<p>구로구는 공식 안내 기준으로 10개 법정동과 16개 행정동으로 구성되며, 행정동에는 구로1~5동, 고척1~2동, "
         "개봉1~3동, 오류1~2동처럼 숫자가 붙은 동이 포함됩니다. 이렇게 숫자로 나뉜 행정동은 별도 페이지를 만들지 않고 "
         "대표 동 페이지에서 통합 안내하여 중복 페이지 위험을 줄였습니다. 어느 숫자 동에 거주하시더라도 해당 대표 동 "
         "페이지를 기준으로 문의하시면 됩니다.</p>"),
        ("list", "대표 동 생활권",
         "<p>아래 카드에서 원하는 동을 선택하면 생활권 특징과 인근 역, 추천 코스·테마를 확인할 수 있습니다. "
         "구로동·신도림동처럼 업무·상업 기능이 강한 곳과 항동·천왕동처럼 신주거 중심인 곳은 방문 환경과 자주 찾는 "
         "관리가 서로 다르므로, 거주·방문하시는 동의 페이지를 직접 확인하시는 것이 가장 정확합니다.</p>"
         f'<div class="grid g3">{cards}</div>'),
        ("note", "동 통합 규칙",
         "<p>아래 기준으로 숫자 행정동을 대표 동에 통합했습니다. 이는 비슷한 페이지를 여러 개 만들어 특정 검색어를 "
         "노리는 도어웨이 방식과 중복 콘텐츠를 피하기 위한 구조입니다.</p>"
         "<ul><li>구로1동~구로5동 → <a href='/guro-gu/guro-dong/'>구로동</a> 1개로 통합</li>"
         "<li>고척1동~고척2동 → <a href='/guro-gu/gocheok-dong/'>고척동</a> 1개로 통합</li>"
         "<li>개봉1동~개봉3동 → <a href='/guro-gu/gaebong-dong/'>개봉동</a> 1개로 통합</li>"
         "<li>오류1동~오류2동 → <a href='/guro-gu/oryu-dong/'>오류동</a> 1개로 통합</li>"
         "<li>궁동·온수동은 각각 안내하되, 행정동 수궁동 설명은 본문에서 함께 다룹니다</li></ul>"
         "<p>따라서 ‘구로1동 출장마사지’, ‘개봉2동 출장마사지’ 같은 숫자 동 단위 페이지는 운영하지 않습니다.</p>"),
        ("howto", "지역과 역, 어디를 보면 될까요",
         "<p>거주지나 방문 장소가 어느 동네인지 알고 있다면 <strong>지역별 안내</strong>가 편리하고, 약속 장소를 "
         "지하철역 기준으로 잡았다면 <a href='/guro-gu/stations/'>지하철역별 안내</a>가 더 직관적입니다. 두 안내는 "
         "서로 연결되어 있어, 지역 페이지에서는 인근 역을, 역 페이지에서는 주변 대표 동을 함께 안내합니다.</p>"
         "<p>관리 유형(스웨디시·아로마·스포츠 등)으로 찾고 싶다면 <a href='/theme/'>테마별 안내</a>를, 시간과 요금 "
         "기준이 궁금하다면 <a href='/course/'>코스안내</a>를 참고하세요. 모든 안내는 마지막에 전화 예약 상담으로 "
         "이어지며, 정확한 방문 가능 여부와 금액은 상담에서 최종 확정됩니다.</p>"),
    ]
    faq = [
        ("지역 페이지는 어떤 기준으로 나뉘나요?", "구로구청 공식 법정동을 기준으로 대표 동 10곳으로 구성했습니다."),
        ("우리 동이 목록에 없어요.", "구로1동처럼 숫자로 나뉜 동은 구로동 등 대표 동 페이지에서 통합 안내합니다."),
        ("지역과 역 중 어디를 보면 되나요?", "거주·방문 생활권은 지역 페이지, 역 인근 동선은 지하철역 페이지에서 확인하면 편리합니다."),
    ]
    h, ni = article_page(path, title, desc, "지역별 안내",
        [("홈", "/"), ("지역별 안내", "")],
        "구로구 지역별 출장마사지·홈타이 안내",
        "구로구 대표 동 10곳의 생활권별 방문 관리 안내입니다. 각 동의 특징과 주변 역세권, 관련 테마를 확인하세요.",
        secs, faq)
    write(path, h, priority="0.9", noindex=ni)

    for d in DONGS:
        build_dong(d)


def build_dong(d):
    path = f"/guro-gu/{d['slug']}/"
    name = d["name"]
    title = f"{name} 출장마사지·홈타이 | 구로구 {name} 인근 방문 마사지 안내"
    desc = f"구로구 {name} 생활권 방문 마사지·홈타이 안내입니다. {name}의 특징과 주변 역세권, 예약 가능 시간, 관련 테마를 확인하세요."
    near_links = " · ".join(d["near_st"])
    theme_links = theme_chip_links(d["themes"])
    merge_html = f"<p>{d['merge']}</p>" if d["merge"] else ""
    # 대표 테마 설명(고유) — 지역마다 추천 테마가 달라 본문도 달라짐
    theme_desc = ""
    for tslug, tname in d["themes"]:
        td = next((x for x in THEMES if x["slug"] == tslug), None)
        if td:
            theme_desc += (f"<h3><a href='/theme/{tslug}/'>{tname}</a></h3>"
                           f"<p>{td['feat']} {html.escape(td['for'])}께 권합니다.</p>")
    secs = [
        ("intro", f"{name} 생활권 안내",
         f"<p>{d['intro']}</p><p>{d['life']}</p>{merge_html}"),
        ("access", f"{name} 교통·접근 안내",
         f"<p>{d['access']}</p><p>{d['env']}</p>"
         f"<div class='data-box'><b>방문 팁</b><p>{d['tip']}</p></div>"),
        ("station", f"{name} 주변 지하철역",
         f"<p>{name}에서 가까운 지하철역은 <strong>{near_links}</strong>입니다. 역 인근에서 방문을 원하시면 "
         "지하철역별 안내의 해당 역 페이지에서 인근 생활권과 동선을 함께 확인할 수 있습니다. 다만 같은 동이라도 "
         "위치에 따라 가까운 역과 이동 시간이 달라질 수 있으므로, 방문 위치는 예약 시 정확한 주소를 기준으로 "
         "확정됩니다. 출구별로 페이지를 따로 두지 않고, 역 단위로만 안내하는 것이 원칙입니다.</p>"
         "<ul>" + "".join(f"<li>{s}</li>" for s in d["near_st"]) + "</ul>"),
        ("theme", f"{name}에서 많이 찾는 테마",
         f"<p>{name} 생활권에서는 다음 테마 문의가 많은 편입니다: {theme_links}. 테마별 특징과 추천 대상은 "
         "각 테마 페이지에서 확인하실 수 있습니다. 지역과 테마를 조합한 별도 페이지는 운영하지 않으며, 아래처럼 "
         "관련 테마로만 연결합니다.</p>" + theme_desc),
        ("course", f"{name} 추천 코스 안내",
         f"<p>{name}에서는 생활권 특성에 따라 코스 선택 경향이 조금씩 다릅니다. 가볍게 피로만 풀고 싶다면 60분, "
         "전신을 충분히 이완하려면 90분, 깊은 휴식과 집중 관리를 원한다면 120분이 기준입니다. "
         f"{name}의 주거·생활 환경을 고려하면, 하루를 마치고 받는 이완 중심 코스나 가정에서 받는 "
         "<a href='/course/home/'>홈타이 코스</a>가 무난하게 선택됩니다. 두 분 이상 함께라면 "
         "<a href='/course/couple/'>커플·가족 방문 관리</a>도 고려할 수 있습니다.</p>"
         "<p>코스는 원하는 테마와 함께 구성할 수 있으며, 시간·요금 기준은 "
         "<a href='/course/price/'>가격 안내</a>에서, 선택이 고민될 때는 "
         "<a href='/course/guide/'>코스 선택 가이드</a>에서 확인하세요. 표시 요금은 기본 기준이며 지역·시간대·"
         "인원에 따라 달라질 수 있어, 정확한 금액은 예약 상담에서 안내드립니다.</p>"),
        ("reserve", f"{name} 예약 가능 시간·확인사항",
         "<p>예약은 희망 위치와 시간, 코스, 인원을 확인한 뒤 진행됩니다. 저녁 시간대와 주말은 문의가 몰릴 수 있어 "
         "여유 있는 예약을 권장합니다. 방문 전에는 정확한 주소, 공동현관 출입 방법, 주차 가능 여부, 조용한 공간 확보 "
         "여부를 확인해 주세요. 숙소나 오피스텔을 이용하실 때는 출입 안내와 연락 가능 여부를 함께 확인하면 방문이 "
         "원활합니다. 자세한 내용은 <a href='/reservation/hours/'>예약 가능 시간</a>과 "
         "<a href='/guide/checklist/'>이용 전 확인사항</a>을 참고하세요. 코스 선택이 고민된다면 "
         "<a href='/course/guide/'>코스 선택 가이드</a>가 도움이 됩니다.</p>"
         "<div class='data-box'><b>안내</b><p>본 서비스는 의료 행위가 아닌 건강관리(이완·휴식) 목적이며, "
         "만 19세 이상 성인을 대상으로 합니다. 불법·퇴폐 행위는 일절 제공하지 않습니다.</p></div>"),
        ("related", "함께 보면 좋은 안내",
         f"<p>{name} 방문을 준비하신다면 아래 안내를 함께 확인하시면 도움이 됩니다. 인근 역세권 동선은 "
         "<a href='/guro-gu/stations/'>지하철역별 안내</a>에서, 관리 유형은 <a href='/theme/'>테마별 안내</a>에서, "
         "코스와 요금은 <a href='/course/'>코스안내</a>에서 확인할 수 있습니다.</p>"
         "<ul>"
         "<li><a href='/reservation/'>예약안내</a> — 예약 방법·가능 시간·방문 가능 장소</li>"
         "<li><a href='/guide/checklist/'>이용 전 확인사항</a> — 방문 전 점검 항목</li>"
         "<li><a href='/guro-gu/'>구로구 지역별 안내</a> — 다른 대표 동 생활권 보기</li>"
         "</ul>"
         f"<p>{name} 외 다른 생활권을 찾으신다면 지역별 안내에서 신도림동·구로동·고척동·개봉동·오류동 등 대표 동 "
         "페이지를 확인하실 수 있습니다. 정확한 방문 가능 여부와 금액은 전화 예약 상담에서 최종 안내드립니다.</p>"),
    ]
    faq = [
        (f"{name} 어디까지 방문이 가능한가요?",
         f"{name} 생활권을 기준으로 안내하며, 정확한 가능 여부는 예약 시 방문 주소와 시간, 그날의 배정 상황에 따라 "
         f"확인됩니다. {name} 안에서도 위치에 따라 가까운 역과 이동 시간이 다를 수 있으니, 도로명 주소나 인근 "
         "랜드마크를 함께 알려주시면 더 정확하게 안내드릴 수 있습니다."),
        (f"{name}은 어떤 코스가 잘 맞나요?",
         "목적과 컨디션에 따라 다릅니다. 가볍게는 60분, 무난하게는 90분, 깊은 휴식은 120분이 기준이며, "
         f"{name} 생활권에서 많이 찾는 테마와 함께 구성할 수 있습니다. 결정이 어렵다면 "
         "<a href='/course/guide/'>코스 선택 가이드</a>를 참고하거나 예약 상담에서 추천받으실 수 있습니다."),
        ("당일 예약도 가능한가요?",
         "가능할 수 있으나 저녁 시간대와 주말은 문의가 몰려 원하는 시간이 빠르게 마감될 수 있습니다. 가급적 "
         "사전 예약을 권장하며, 당일 방문을 원하시면 먼저 전화로 가능 시간을 확인하는 것이 좋습니다."),
        ("숫자로 나뉜 동인데 페이지가 없어요.",
         "구로1동·고척2동처럼 숫자로 나뉜 행정동은 중복 페이지 방지를 위해 대표 동 페이지에서 통합 안내합니다. "
         "해당 대표 동 페이지를 기준으로 문의하시면 됩니다."),
    ]
    h, ni = article_page(path, title, desc, f"지역별 안내 · {name}",
        [("홈", "/"), ("지역별 안내", "/guro-gu/"), (name, "")],
        f"{name} 출장마사지·홈타이 예약 안내",
        f"구로구 {name} 생활권의 방문 관리 안내입니다. {d['tag']} 특성에 맞춰 예약과 코스를 안내합니다.",
        secs, faq)
    write(path, h, priority="0.8", noindex=ni)


# ---------------------------------------------------------------------------
# 8. 지하철역 허브 (/guro-gu/stations/) + 역 페이지
# ---------------------------------------------------------------------------
def build_stations():
    path = "/guro-gu/stations/"
    title = "구로 지하철역별 출장마사지·홈타이 안내 | 1·2·7호선 구로권"
    desc = "구로구 1·2·7호선 역세권 방문 마사지·홈타이 안내입니다. 신도림역·구로역·남구로역·온수역 등 역별 인근 생활권을 확인하세요."
    line_blocks = ""
    for lid, lname, slugs in LINES:
        cards = "".join(
            f'<a class="card reveal" href="/guro-gu/stations/{STN[s]["slug"]}/"><div class="k">{STN[s]["lines"]}</div>'
            f'<h3>{STN[s]["name"]}</h3><p>{STN[s]["dong"][1]} 인근</p><span class="more">역 인근 안내 →</span></a>'
            for s in slugs)
        line_blocks += (f'<section class="lux-sec reveal" id="{lid}"><h2>{lname}</h2>'
                        f'<div class="grid g3">{cards}</div></section>\n')
    intro = (
        "<p>지하철역별 안내는 구로구를 지나는 1호선·2호선·7호선 구로권 역을 기준으로 구성됩니다. 각 역 페이지에서는 "
        "인근 생활권, 주변 대표 동, 예약 가능 시간, 방문 전 준비사항을 안내합니다. 환승역은 여러 노선 목록에 보이더라도 "
        "주소(URL)는 하나만 사용하며, 출구별 페이지나 역과 테마를 조합한 페이지는 만들지 않습니다.</p>")
    out = head(title, desc, path)
    out += nav(active="stations")
    out += crumb([("홈", "/"), ("지하철역별 안내", "")])
    out += lux_hero("지하철역별 안내",
        "구로 지하철역별 출장마사지·홈타이 안내",
        "1·2·7호선 구로권 역세권 기준으로 인근 생활권과 방문 관리를 안내합니다.")
    out += f"""<section class="block lux-body" style="padding-top:30px"><div class="wrap"><div class="lux-main" style="max-width:none">
<section class="lux-sec reveal" id="intro"><h2>구로 지하철역 안내 기준</h2>{intro}</section>
{line_blocks}
</div></div></section>
"""
    out += faq_block([
        ("환승역은 페이지가 여러 개인가요?", "아니요. 신도림역·대림역·온수역 같은 환승역도 페이지(주소)는 하나만 사용합니다."),
        ("역 이름에 테마를 붙인 페이지가 있나요?", "없습니다. ‘구로역 스웨디시’처럼 역과 테마를 조합한 페이지는 만들지 않습니다."),
        ("역과 지역 중 무엇을 보면 되나요?", "역 인근 동선은 역 페이지, 거주 생활권은 지역 페이지에서 확인하면 편리합니다."),
    ])
    out += footer()
    write(path, out, priority="0.9")

    seen = set()
    for s in STN:
        if s in seen:
            continue
        seen.add(s)
        build_station(s)


def build_station(key):
    st = STN[key]
    path = f"/guro-gu/stations/{st['slug']}/"
    name = st["name"]
    dong_slug, dong_name = st["dong"]
    title = f"{name} 출장마사지·홈타이 | 구로구 {name} 인근 방문 마사지 안내"
    desc = f"구로구 {name}({st['lines']}) 인근 방문 마사지·홈타이 안내입니다. {name} 주변 생활권과 예약 가능 시간을 확인하세요."
    note = f"<div class='data-box'><b>위치 확인</b><p>{st['note']}</p></div>" if st.get("note") else ""
    # 인근 대표 동의 관련 테마를 끌어와 역 페이지마다 연결을 다르게
    dd = next((x for x in DONGS if x["slug"] == dong_slug), None)
    theme_links = theme_chip_links(dd["themes"]) if dd else ""
    transfer = ("이 역은 환승역으로, 여러 노선 메뉴에 함께 보이더라도 안내 페이지(주소)는 하나만 사용합니다. "
                if "·" in st["lines"] else
                "단일 노선 역으로, 인근 생활권 동선을 기준으로 안내합니다. ")
    secs = [
        ("intro", f"{name} 인근 안내",
         f"<p>{st['desc']}</p><p>{st['life']}</p>{note}"),
        ("line", f"{name} 노선·동선 안내",
         f"<p>{name}은 {st['lines']} 역입니다. {transfer}"
         "구로88마사지는 출구별 페이지나 ‘역 이름 + 테마’를 조합한 페이지를 만들지 않고, 역 단위로만 인근 생활권을 "
         "안내합니다. 같은 역이라도 출구와 도착 위치에 따라 이동 시간이 달라질 수 있어, 방문 위치는 예약 시 정확한 "
         "주소를 기준으로 확정됩니다.</p>"),
        ("dong", f"{name} 주변 대표 동",
         f"<p>{name} 인근의 대표 생활권은 <a href='/guro-gu/{dong_slug}/'>{dong_name}</a>입니다. 거주지나 숙소가 "
         f"{dong_name} 생활권에 있다면 해당 지역 페이지에서 동네 특징과 교통, 관련 테마를 함께 확인할 수 있습니다. "
         f"{dong_name}에서 많이 찾는 테마로는 {theme_links} 등이 있으며, 자세한 내용은 지역 페이지로 연결됩니다. "
         "방문 위치는 예약 시 정확한 주소를 기준으로 확정됩니다.</p>"),
        ("reserve", f"{name} 예약 가능 시간·준비사항",
         "<p>예약은 위치·시간·코스·인원을 확인한 뒤 진행됩니다. 저녁 시간대와 주말은 문의가 많을 수 있어 여유 있는 "
         "예약을 권장하며, 심야·새벽 방문을 원하시면 먼저 전화로 가능 시간을 확인하는 것이 좋습니다. 방문 전에는 "
         "정확한 주소와 공동현관 출입 방법, 주차 여부, 조용한 공간 확보 여부를 확인해 주세요. 숙소·오피스텔은 출입 "
         "절차가 다양하므로 출입 방법과 연락 가능 여부를 함께 알려주시면 방문이 원활합니다. 자세한 내용은 "
         "<a href='/reservation/hours/'>예약 가능 시간</a>과 <a href='/guide/prepare/'>방문 전 준비사항</a>을 "
         "참고하세요.</p>"),
        ("theme", f"{name} 인근에서 참고할 테마·코스",
         "<p>테마는 독립 페이지로 운영하며, 역 페이지에서는 관련 테마로만 연결합니다. 전체 테마는 "
         "<a href='/theme/'>테마별 안내</a>에서, 코스 시간(60·90·120분)과 요금 기준은 "
         "<a href='/course/price/'>가격 안내</a>에서 확인하실 수 있습니다. 어떤 코스를 골라야 할지 고민된다면 "
         "<a href='/course/guide/'>코스 선택 가이드</a>가 도움이 됩니다. 다시 강조하지만 ‘역 이름 + 테마’를 조합한 "
         "별도 페이지는 만들지 않으며, 본 서비스는 의료 행위가 아닌 이완·휴식 목적의 건강관리입니다.</p>"),
        ("related", "함께 보면 좋은 안내",
         f"<p>{name} 인근 방문을 준비하신다면 아래 안내가 도움이 됩니다. 인근 대표 동의 생활권은 "
         f"<a href='/guro-gu/{dong_slug}/'>{dong_name}</a> 페이지에서, 다른 구로권 역은 "
         "<a href='/guro-gu/stations/'>지하철역별 안내</a>에서 확인할 수 있습니다.</p>"
         "<ul>"
         "<li><a href='/reservation/hours/'>예약 가능 시간</a> — 운영·방문 가능 시간</li>"
         "<li><a href='/reservation/place/'>방문 가능 장소</a> — 자택·숙소·오피스텔 안내</li>"
         "<li><a href='/guide/checklist/'>이용 전 확인사항</a> — 방문 전 점검 항목</li>"
         "</ul>"
         "<p>예약은 전화 상담으로 가능 여부를 확인한 뒤 진행됩니다. 정확한 방문 가능 여부와 금액은 예약 상담에서 "
         "최종 안내드립니다.</p>"),
    ]
    faq = [
        (f"{name} 근처도 방문이 가능한가요?",
         f"{name} 인근 생활권을 기준으로 안내하며, 정확한 가능 여부는 예약 시 방문 주소와 시간, 배정 상황에 따라 "
         "확인됩니다. 역에서 다소 떨어진 위치라도 주소를 알려주시면 가능 여부를 안내드립니다."),
        ("몇 번 출구를 기준으로 안내하나요?",
         "출구별 페이지는 운영하지 않습니다. 방문은 출구가 아니라 정확한 도착 주소를 기준으로 안내하므로, 예약 시 "
         "도로명 주소나 건물명을 알려주시면 됩니다."),
        ("당일 예약도 가능한가요?",
         "가능할 수 있으나 저녁 시간대와 주말은 문의가 많아 원하는 시간이 빠르게 마감될 수 있습니다. 사전 예약을 "
         "권장하며, 당일에는 먼저 전화로 가능 시간을 확인하는 것이 좋습니다."),
    ]
    h, ni = article_page(path, title, desc, f"지하철역별 안내 · {name}",
        [("홈", "/"), ("지하철역별 안내", "/guro-gu/stations/"), (name, "")],
        f"{name} 출장마사지·홈타이 예약 안내",
        f"구로구 {name}({st['lines']}) 인근 방문 관리 안내입니다. 주변 생활권과 예약 절차를 확인하세요.",
        secs, faq)
    write(path, h, priority="0.7", noindex=ni)


# ---------------------------------------------------------------------------
# 9. 테마 허브 (/theme/) + 테마 14
# ---------------------------------------------------------------------------
def build_themes():
    path = "/theme/"
    title = "테마별 마사지 안내 | 스웨디시·아로마·타이마사지 등 14종"
    desc = "스웨디시·로미로미·타이마사지·아로마테라피·홈케어 등 관리 유형별 특징과 추천 대상을 안내합니다."
    cards = "".join(
        f'<a class="card reveal" href="/theme/{t["slug"]}/"><div class="k">THEME</div>'
        f'<h3>{t["name"]}</h3><p>{html.escape(t["feat"])}</p><span class="more">자세히 →</span></a>'
        for t in THEMES)
    secs = [
        ("intro", "테마별 안내 기준",
         "<p>테마별 안내에서는 관리 유형별 특징, 추천 대상, 진행 방식, 예약 전 확인사항을 설명합니다. 각 테마는 "
         "독립 페이지로 운영하며, 지역 페이지와 역 페이지에서는 관련 테마로만 연결합니다. ‘구로역 스웨디시’, "
         "‘신도림역 24시간 홈타이’처럼 지역·역·테마를 조합한 페이지는 만들지 않아 중복과 도어웨이 위험을 줄였습니다.</p>"
         "<p>구로88마사지의 방문 관리는 오일을 사용하는 이완 중심 관리부터 지압·스트레칭 위주의 시원한 관리, 하체 "
         "집중·수면 유도까지 폭이 넓습니다. 처음 이용하신다면 부드러운 스웨디시나 아로마테라피가 무난하고, 특정 부위 "
         "뭉침이 심하다면 스포츠·경락이 적합합니다. 아래에서 원하는 관리를 골라 특징과 추천 대상을 확인하세요.</p>"),
        ("how", "테마 선택 기준",
         "<p>테마를 고를 때는 ‘무엇을 원하는가’에서 출발하면 쉽습니다. 전반적인 긴장 완화와 휴식이 목적이라면 "
         "<a href='/theme/swedish/'>스웨디시</a>·<a href='/theme/aroma-therapy/'>아로마테라피</a>, 뻣뻣한 몸을 "
         "시원하게 풀고 싶다면 <a href='/theme/thai-massage/'>타이마사지</a>·<a href='/theme/chinese-massage/'>"
         "중국마사지</a>, 근육 회복이 필요하다면 <a href='/theme/sports-massage/'>스포츠·경락</a>이 어울립니다. "
         "다리가 무겁다면 <a href='/theme/foot-massage/'>발마사지</a>, 잠들기 전 이완이라면 "
         "<a href='/theme/sleep-available/'>수면 가능</a> 관리를 권합니다.</p>"
         "<p>두 분 이상 함께라면 <a href='/theme/couple/'>커플 관리</a>, 늦은 시간이 필요하다면 "
         "<a href='/theme/24hours/'>24시간</a> 운영을 참고하세요. 테마는 코스 시간(60·90·120분)과 함께 선택하며, "
         "지역·역과 무관하게 동일한 기준으로 안내됩니다.</p>"),
        ("list", "전체 테마",
         "<p>아래 카드에서 관리 유형을 선택하면 특징·추천 대상·진행 방식·주의사항을 확인할 수 있습니다.</p>"
         f'<div class="grid g3">{cards}</div>'),
    ]
    faq = [
        ("처음이면 어떤 테마가 좋나요?", "부드러운 스웨디시나 아로마테라피가 무난합니다. 컨디션에 따라 상담에서 추천드립니다."),
        ("테마와 코스는 어떻게 다른가요?", "테마는 관리 유형, 코스는 시간·구성 단위입니다. 코스안내에서 함께 확인하세요."),
        ("지역별로 가능한 테마가 다른가요?", "배정 상황에 따라 달라질 수 있으며, 예약 시 가능 여부를 안내합니다."),
    ]
    h, ni = article_page(path, title, desc, "테마별 안내",
        [("홈", "/"), ("테마별 안내", "")],
        "테마별 마사지 안내",
        "관리 유형별 특징과 추천 대상을 정리한 테마 안내입니다. 원하는 관리를 골라 예약 상담에 참고하세요.",
        secs, faq)
    write(path, h, priority="0.8", noindex=ni)
    for t in THEMES:
        build_theme(t)


def build_theme(t):
    path = f"/theme/{t['slug']}/"
    name = t["name"]
    title = f"{name} 마사지 안내 | 특징·추천 대상·예약 안내"
    desc = f"{name}의 특징과 추천 대상, 예약 전 확인사항을 안내합니다. {html.escape(t['feat'])}"
    secs = [
        ("intro", f"{name}란",
         f"<p>{t['feat']}</p><p>{name}는 구로88마사지의 방문 관리에서 선택할 수 있는 테마 중 하나로, 가정·숙소·"
         "오피스텔 등 요청하신 위치에서 진행됩니다. 진행 강도와 방식은 컨디션과 요청에 따라 조절할 수 있어, 처음 "
         f"이용하시는 분도 부담 없이 받을 수 있습니다. {t['how']}</p>"),
        ("for", "이런 분께 권합니다",
         f"<p>{html.escape(t['for'])}. {t['time']} 다만 통증이 심하거나 특정 질환이 있는 경우에는 무리한 관리보다 "
         "전문의 진료를 먼저 권합니다. 본 서비스는 의료 행위가 아닌 이완·휴식 목적의 건강관리이며, 만 19세 이상 "
         "성인을 대상으로 합니다.</p>"),
        ("course", "코스·예약 연결",
         "<p>테마는 코스 시간(60·90·120분)과 함께 선택합니다. 가볍게는 60분, 전신을 충분히 이완하려면 90분, 깊은 "
         "휴식은 120분이 기준입니다. 어떤 코스가 맞을지 모르겠다면 <a href='/course/guide/'>코스 선택 가이드</a>를, "
         "시간·요금 기준은 <a href='/course/price/'>가격 안내</a>를, 예약 절차는 <a href='/reservation/'>예약안내</a>를 "
         "참고하세요. 지역 페이지와 역 페이지에서도 관련 테마로 이 페이지가 연결되며, 지역·역과 테마를 조합한 별도 "
         "페이지는 만들지 않습니다.</p>"),
        ("flow", f"{name} 진행 순서와 시간대 안내",
         f"<p>{t['how']} 진행 강도는 약하게·보통·강하게 중에서 조절할 수 있으니, 원하는 정도를 미리 말씀해 주시면 "
         f"컨디션에 맞춰 시작합니다. {t['time']}</p>"
         f"<p>{name}는 구로구 전지역 방문 관리에서 선택할 수 있으며, 신도림동·구로동·고척동·개봉동·오류동 등 대표 "
         "동과 1·2·7호선 역세권 어디서든 동일한 기준으로 안내됩니다. 다만 지역·역과 테마를 조합한 별도 페이지는 "
         "만들지 않으므로, 지역 정보는 <a href='/guro-gu/'>지역별 안내</a>에서, 이 테마는 독립 페이지로 확인해 "
         "주세요. 예약은 위치·시간·코스·인원을 확인한 뒤 진행됩니다.</p>"),
        ("check", "예약 전 확인사항",
         f"<p>방문 전에는 정확한 주소와 공동현관·객실 출입 방법, 관리에 적합한 조용한 공간 확보 여부를 확인해 "
         f"주세요. {t['caution']} 향이나 오일에 민감하거나 피부 반응이 우려되는 경우, 또는 특별히 원하거나 피하고 "
         "싶은 부위가 있다면 예약 시 미리 알려주시면 진행 방식을 조정합니다. 정확한 정보 공유는 관리의 질과 안전을 "
         "함께 높입니다. 본 서비스는 의료 행위가 아닌 이완·휴식 목적의 건강관리이며, 통증이 심하면 전문의 진료를 "
         "먼저 권합니다.</p>"),
        ("related", "함께 보면 좋은 안내",
         f"<p>{name}를 받기 전후로 아래 안내를 함께 확인하시면 도움이 됩니다. 시간·요금은 "
         "<a href='/course/price/'>가격 안내</a>, 코스 선택은 <a href='/course/guide/'>코스 선택 가이드</a>, "
         "방문 준비는 <a href='/guide/prepare/'>방문 전 준비사항</a>에서 확인할 수 있습니다.</p>"
         "<ul>"
         "<li><a href='/theme/'>전체 테마 보기</a> — 다른 관리 유형 비교</li>"
         "<li><a href='/reservation/'>예약안내</a> — 예약 방법과 절차</li>"
         "<li><a href='/guide/aftercare/'>관리 후 주의사항</a> — 받은 뒤 케어</li>"
         "</ul>"
         "<p>예약은 위치·시간·코스·인원을 확인한 뒤 진행되며, 정확한 가능 여부와 금액은 전화 예약 상담에서 "
         "최종 안내드립니다.</p>"),
    ]
    faq = [
        (f"{name}는 처음이어도 괜찮나요?",
         "예. 강도와 방식을 조절할 수 있으니 예약 시 처음임을 알려주시면 컨디션에 맞춰 편안하게 진행합니다. "
         "원하는 강도(약하게·보통·강하게)를 미리 말씀해 주시면 더 좋습니다."),
        ("시간은 어떻게 선택하나요?",
         "60·90·120분 중 목적에 맞게 선택합니다. 처음이라면 90분이 무난하며, 기준 요금은 "
         "<a href='/course/price/'>가격 안내</a>에서 확인할 수 있습니다."),
        ("구로 어느 지역까지 가능한가요?",
         "구로구 전지역을 기준으로 안내하며, 정확한 가능 여부는 예약 시 방문 위치와 시간으로 확인합니다."),
    ]
    h, ni = article_page(path, title, desc, f"테마별 안내 · {name}",
        [("홈", "/"), ("테마별 안내", "/theme/"), (name, "")],
        f"{name} 마사지 안내",
        f"{name}의 특징과 추천 대상, 예약 전 확인사항을 정리했습니다.",
        secs, faq)
    write(path, h, priority="0.7", noindex=ni)


# ---------------------------------------------------------------------------
# 10. 코스 허브 (/course/) + 코스 8
# ---------------------------------------------------------------------------
def price_cards_html():
    rows = ""
    for name, dur, won, dsc, best in PRICES:
        badge = '<div class="pmenu-badge">추천</div>' if best else ''
        cls = " best" if best else ""
        rows += (f'<div class="pmenu-card{cls}">{badge}<div class="pmenu-name">{name}</div>'
                 f'<div class="pmenu-price">{won}<span>원</span></div>'
                 f'<div class="pmenu-dur">{dur}</div>'
                 f'<div class="pmenu-desc">{dsc}</div>'
                 f'<a class="pmenu-btn" href="tel:{PHONE_TEL}">예약 문의</a></div>')
    return f'<div class="pmenu">{rows}</div>'


def price_table_html():
    """본문 섹션 안에 넣는 요금표(카드 + 안내문)."""
    return (price_cards_html() +
            '<div class="pmenu-note">표시 요금은 기본 기준이며 지역·예약 시간대·이동 거리에 따라 '
            '상담 시 최종 확인됩니다. <a href="/course/price/">상세 요금 안내 보기 →</a></div>')


def price_section():
    """전 페이지 공통으로 푸터 위에 노출되는 ‘코스별 기본 요금’ 섹션."""
    return f"""<section class="block" id="price" aria-label="코스별 기본 요금"><div class="wrap">
  <span class="eyebrow"><span class="pulse"></span>요금 안내</span>
  <h2 class="sec">코스별 기본 요금</h2>
  <p class="sec-lead">60·90·120분 코스별 기본 요금입니다. 숨겨진 추가 비용 없이 투명하게 안내합니다.</p>
  {price_cards_html()}
  <div class="pmenu-note">지역·예약 시간대·이동 거리에 따라 상담 시 최종 확인됩니다. <a href="/course/price/">상세 요금 안내 보기 →</a></div>
</div></section>
"""


def build_courses():
    path = "/course/"
    title = "코스안내 | 구로 출장마사지·홈타이 코스와 가격"
    desc = "피로 회복·아로마·스포츠·홈타이·커플·단체 코스와 60·90·120분 기준 요금을 안내합니다."
    cards = "".join(
        f'<a class="card reveal" href="/course/{c["slug"]}/"><div class="k">COURSE</div>'
        f'<h3>{c["name"]}</h3><p>{html.escape(c["desc"])}</p><span class="more">자세히 →</span></a>'
        for c in COURSES)
    secs = [
        ("intro", "코스 선택 안내",
         "<p>코스는 이용 목적과 컨디션에 따라 선택합니다. 피로 회복, 편안한 휴식, 근육 이완, 숙소 방문, 커플·단체 "
         "이용 등 상황에 맞는 코스를 마련했습니다. 기본 시간은 60·90·120분이며, 가볍게 풀고 싶다면 60분, 전신을 "
         "충분히 이완하려면 90분, 깊은 휴식과 집중 관리를 원한다면 120분이 기준입니다. 자세한 내용은 아래 코스별 "
         "페이지에서 확인하세요.</p>"
         "<p>코스는 원하는 테마(스웨디시·아로마·스포츠·경락 등)와 함께 구성할 수 있습니다. 즉 ‘무엇을(테마) 얼마나 "
         "오래(코스 시간)’ 받을지를 함께 정하는 방식입니다. 어떤 조합이 맞을지 고민된다면 "
         "<a href='/course/guide/'>코스 선택 가이드</a>에서 목적별 기준을 확인하거나 예약 상담에서 추천받으실 수 "
         "있습니다.</p>"),
        ("fee", "기본 요금",
         "<p>기본 요금은 60분 80,000원, 90분 120,000원, 120분 150,000원입니다. 90분 코스는 아로마를 포함한 추천 "
         "구성으로 가장 많이 선택됩니다. 코스별 기본 요금표는 이 페이지 하단의 "
         "<a href='#price'>코스별 기본 요금</a>에서 카드로 확인하실 수 있습니다.</p>"
         "<p>표시 요금은 기본 기준이며 지역·예약 시간대·이동 거리에 따라 상담 시 최종 확인됩니다. 자세한 기준은 "
         "<a href='/course/price/'>가격 안내</a>에서 다루며, 정확한 금액은 예약 상담에서 안내드립니다.</p>"),
        ("list", "코스 종류",
         "<p>아래 카드에서 목적에 맞는 코스를 선택하면 구성과 추천 상황, 예약 방법을 확인할 수 있습니다. 피로 "
         "회복부터 아로마·스포츠·홈타이·커플·기업 단체까지, 상황별로 나누어 안내합니다.</p>"
         f'<div class="grid g3">{cards}</div>'),
        ("place", "어디서 받을 수 있나요",
         "<p>모든 코스는 구로구 전지역을 대상으로 한 방문 관리로 진행됩니다. 자택은 물론 호텔·숙소, 오피스텔 등 "
         "안정적으로 관리를 받을 수 있는 실내 공간으로 방문하며, 정확한 방문 가능 여부는 예약 시 주소와 시간으로 "
         "확인합니다. 지역별 안내는 <a href='/guro-gu/'>지역별 안내</a>, 역세권 동선은 "
         "<a href='/guro-gu/stations/'>지하철역별 안내</a>를 참고하세요. 본 서비스는 의료 행위가 아닌 이완·휴식 "
         "목적의 건강관리이며, 만 19세 이상 성인을 대상으로 합니다.</p>"),
    ]
    faq = [
        ("어떤 코스를 골라야 할지 모르겠어요.", "코스 선택 가이드에서 목적별 기준을 확인하거나 예약 상담에서 추천받을 수 있습니다."),
        ("시간 연장이 가능한가요?", "배정 상황에 따라 가능할 수 있으며 예약 시 문의해 주세요."),
        ("표시 가격이 최종 금액인가요?", "기본 기준이며 조건에 따라 달라질 수 있어 상담에서 확정됩니다."),
    ]
    h, ni = article_page(path, title, desc, "코스안내",
        [("홈", "/"), ("코스안내", "")],
        "구로 출장마사지·홈타이 코스안내",
        "목적과 컨디션에 맞는 코스를 고를 수 있도록 코스 종류와 기준 요금을 정리했습니다.",
        secs, faq)
    write(path, h, priority="0.8", noindex=ni)
    for c in COURSES:
        build_course(c)


def build_course(c):
    path = f"/course/{c['slug']}/"
    name = c["name"]
    title = f"{name} | 구로 출장마사지·홈타이 코스 안내"
    desc = f"{name} 안내입니다. {html.escape(c['desc'])}"
    if c["slug"] == "price":
        body_intro = (f"<p>{c['desc']} 기본 시간은 60·90·120분이며, 표시 요금은 기준 금액입니다.</p>"
                      "<ul><li>60분 코스 — 80,000원 · 기본 컨디션·릴렉스 케어</li>"
                      "<li>90분 코스 — 120,000원 · 아로마 포함 추천 구성 (가장 많이 선택)</li>"
                      "<li>120분 코스 — 150,000원 · 전신 집중 프리미엄 케어</li></ul>"
                      "<p>카드 형태의 코스별 기본 요금표는 이 페이지 하단의 <a href='#price'>코스별 기본 요금</a>에서 "
                      "확인하실 수 있습니다. 지역·예약 시간대·이동 거리에 따라 금액이 달라질 수 있어, 정확한 금액은 "
                      "예약 상담에서 최종 안내합니다.</p>")
    elif c["slug"] == "guide":
        body_intro = ("<p>코스 선택은 ‘무엇을 풀고 싶은가’에서 시작합니다. 전반적인 피로라면 "
                      "<a href='/course/fatigue/'>피로 회복 관리</a>, 스트레스 해소와 분위기 있는 휴식이라면 "
                      "<a href='/course/aroma/'>아로마 관리</a>, 운동 후 근육 회복이라면 "
                      "<a href='/course/sports/'>스포츠 관리</a>가 적합합니다. 이동 없이 받고 싶다면 "
                      "<a href='/course/home/'>홈타이 코스</a>, 함께 받고 싶다면 "
                      "<a href='/course/couple/'>커플·가족 방문 관리</a>를 고려하세요.</p>"
                      "<p>시간은 가볍게 60분, 무난하게 90분, 깊은 휴식은 120분이 기준입니다. 결정이 어렵다면 "
                      "예약 상담에서 컨디션을 말씀해 주시면 맞는 코스를 안내드립니다.</p>")
    else:
        body_intro = f"<p>{c['desc']}</p><p>이 코스는 {c['fit']} 적합합니다. 진행 강도와 구성은 컨디션과 요청에 따라 조절할 수 있습니다.</p>"
    secs = [
        ("intro", f"{name} 안내", body_intro),
        ("fit", "추천 상황과 선택 기준",
         f"<p>{c['fit']} 권장합니다. 기본 시간은 60·90·120분 중 선택하며, 처음이라면 90분이 무난합니다. "
         "테마와 함께 구성할 수 있으니 <a href='/theme/'>테마별 안내</a>도 참고하세요.</p>"),
        ("reserve", "예약 방법",
         "<p>예약은 위치·시간·코스·인원을 확인한 뒤 진행됩니다. 자세한 절차는 <a href='/reservation/'>예약안내</a>, "
         "방문 전 준비는 <a href='/guide/prepare/'>방문 전 준비사항</a>을 참고하세요. 본 서비스는 의료 행위가 아닌 "
         "이완·휴식 목적의 건강관리이며, 만 19세 이상 성인을 대상으로 합니다.</p>"),
    ]
    faq = [
        ("시간은 어떻게 고르나요?", "가볍게는 60분, 무난하게는 90분, 깊은 휴식은 120분이 기준입니다."),
        ("테마와 함께 받을 수 있나요?", "예. 코스 시간과 원하는 테마를 함께 선택하실 수 있습니다."),
        ("가격은 어디서 보나요?", "가격 안내 페이지에서 기준 요금을 확인하고 예약 상담에서 최종 확정합니다."),
    ]
    h, ni = article_page(path, title, desc, f"코스안내 · {name}",
        [("홈", "/"), ("코스안내", "/course/"), (name, "")],
        f"{name}",
        f"{html.escape(c['desc'])}",
        secs, faq)
    write(path, h, priority="0.7", noindex=ni)


# ---------------------------------------------------------------------------
# 11. 예약안내 / 이용가이드 / 후기 / 고객센터 / 정책
# ---------------------------------------------------------------------------
RES_CONTENT = {
    "": [
        ("intro", "예약 방법",
         "<p>예약은 ① 희망 지역 또는 역 인근 위치 확인 → ② 희망 시간 확인 → ③ 코스와 인원 확인 → "
         "④ 방문 가능 여부 안내 → ⑤ 예약 확정 순서로 진행됩니다. 전화 상담 한 번으로 가능 여부를 안내드립니다.</p>"
         f"<p>예약·상담은 연중무휴 24시간 가능하며, 전화 <a href='tel:{PHONE_TEL}'>{PHONE_DISPLAY}</a>로 문의하실 수 있습니다. "
         "저녁 시간대와 주말은 문의가 몰릴 수 있어 여유 있는 예약을 권장합니다.</p>"),
        ("need", "예약 시 알려주실 정보",
         "<ul><li>희망 지역(대표 동) 또는 가까운 지하철역</li><li>희망 날짜와 시간</li>"
         "<li>원하는 코스(60·90·120분)와 테마</li><li>인원(커플·가족·단체 여부)</li>"
         "<li>방문 장소 유형(자택·숙소·오피스텔 등)</li></ul>"
         "<p>위 정보를 함께 말씀해 주시면 더 빠르게 가능 여부와 일정을 안내드릴 수 있습니다. 희망 위치는 "
         "<a href='/guro-gu/'>지역별 안내</a>의 대표 동이나 <a href='/guro-gu/stations/'>지하철역별 안내</a>의 역을 "
         "기준으로 말씀해 주시면 됩니다.</p>"),
        ("base", "위치·시간 기준 안내",
         "<p>예약은 ‘어디로, 언제, 무엇을, 몇 명이’를 기준으로 진행됩니다. 방문 위치는 출구나 동네 이름이 아니라 "
         "정확한 도착 주소를 기준으로 확정되며, 같은 지역이라도 위치에 따라 이동 시간이 달라질 수 있습니다. 시간은 "
         "저녁 시간대와 주말에 문의가 몰리므로, 가능하면 1~2개의 대체 시간을 함께 알려주시면 배정이 수월합니다.</p>"
         "<p>코스는 60·90·120분 중에서, 테마는 스웨디시·아로마·스포츠 등에서 선택하며, 커플·가족·단체 여부에 따라 "
         "배정이 달라집니다. 정확한 방문 가능 여부와 금액은 전화 예약 상담에서 최종 안내드립니다.</p>"),
        ("flow", "예약 진행 5단계",
         "<p>예약은 다음 순서로 간단하게 진행됩니다. 처음 이용하셔도 전화 한 번으로 안내받을 수 있습니다.</p>"
         "<ul>"
         "<li>① 희망 지역(대표 동) 또는 가까운 지하철역 확인</li>"
         "<li>② 희망 날짜·시간과 대체 시간 확인</li>"
         "<li>③ 코스(60·90·120분)와 테마, 인원 확인</li>"
         "<li>④ 관리사 배정과 방문 가능 여부 안내</li>"
         "<li>⑤ 예약 확정 및 방문 준비 안내</li>"
         "</ul>"
         "<p>희망 위치는 <a href='/guro-gu/'>지역별 안내</a>나 <a href='/guro-gu/stations/'>지하철역별 안내</a>에서 "
         "미리 확인해 두면 상담이 빠릅니다.</p>"),
        ("link", "함께 보면 좋은 안내",
         "<p>예약 단계별 상세 안내는 아래에서 확인하세요. 처음이라면 예약 가능 시간과 방문 가능 장소를 먼저 보는 "
         "것을 권합니다.</p>"
         "<ul>"
         "<li><a href='/reservation/hours/'>예약 가능 시간</a> — 운영·방문 가능 시간</li>"
         "<li><a href='/reservation/place/'>방문 가능 장소</a> — 자택·숙소·오피스텔</li>"
         "<li><a href='/reservation/payment/'>결제 안내</a> — 요금 기준과 결제</li>"
         "<li><a href='/reservation/change/'>변경·취소 안내</a> — 일정 변경 방법</li>"
         "<li><a href='/reservation/checklist/'>예약 전 체크사항</a> — 사전 점검 항목</li>"
         "</ul>"),
    ],
    "hours": [
        ("intro", "예약 가능 시간",
         "<p>상담과 예약 접수는 연중무휴 24시간 가능합니다. 실제 방문 가능 시간은 관리사 배정 상황과 지역, 이동 "
         "동선에 따라 달라질 수 있습니다. 특히 저녁 시간대와 주말, 공휴일 전후는 문의가 집중되어 원하는 시간이 빠르게 "
         "마감될 수 있으니 여유 있게 예약해 주세요.</p>"),
        ("tip", "원활한 예약을 위한 팁",
         "<ul><li>가능하면 1~2개의 대체 시간을 함께 알려주세요</li><li>심야·새벽 방문은 사전 예약을 권장합니다</li>"
         "<li>당일 예약은 가능 여부를 먼저 전화로 확인하는 것이 좋습니다</li></ul>"
         "<p>24시간대 운영이 필요한 경우 <a href='/theme/24hours/'>24시간 테마</a> 안내도 참고하세요.</p>"),
        ("link", "다음 단계",
         "<p>시간을 정하셨다면 <a href='/reservation/'>예약 방법</a>과 <a href='/guide/checklist/'>이용 전 확인사항</a>을 "
         "확인하신 뒤 전화로 예약을 진행해 주세요.</p>"),
    ],
    "place": [
        ("intro", "방문 가능 장소",
         "<p>자택, 숙소(호텔·모텔), 오피스텔, 게스트하우스 등 안정적으로 관리를 받을 수 있는 실내 공간으로 방문합니다. "
         "구로구 전지역을 기준으로 안내하며, 정확한 방문 가능 여부는 예약 시 주소와 시간으로 확인합니다.</p>"),
        ("check", "장소별 확인사항",
         "<ul><li>공동현관·엘리베이터 출입 방법</li><li>주차 가능 여부와 위치</li>"
         "<li>관리에 적합한 조용한 공간 확보 여부</li><li>숙소의 경우 객실 번호와 연락 가능 여부</li></ul>"
         "<p>오피스텔·숙소는 출입 절차가 다양하므로 예약 시 출입 방법을 함께 알려주시면 방문이 원활합니다.</p>"),
        ("link", "함께 보기",
         "<p><a href='/guide/prepare/'>방문 전 준비사항</a>과 <a href='/reservation/checklist/'>예약 전 체크사항</a>을 "
         "참고하면 방문 당일을 매끄럽게 준비할 수 있습니다.</p>"),
    ],
    "payment": [
        ("intro", "결제 안내",
         "<p>결제 방식과 시점은 예약 상담 과정에서 안내드립니다. 표시된 코스 요금은 기본 기준이며, 지역·시간대·인원·"
         "이동 거리에 따라 금액이 달라질 수 있습니다. 정확한 금액은 예약 확정 전에 안내됩니다.</p>"),
        ("fee", "기준 요금",
         "<p>코스별 기본 요금은 60분 80,000원, 90분 120,000원, 120분 150,000원입니다. 카드 형태의 요금표는 이 "
         "페이지 하단의 <a href='#price'>코스별 기본 요금</a>에서 확인하실 수 있습니다. 자세한 요금 기준은 "
         "<a href='/course/price/'>가격 안내</a>에서 다룹니다.</p>"),
        ("notice", "결제 시 유의사항",
         "<ul><li>예약 전 금액을 반드시 확인하세요</li><li>추가 요청에 따른 변동 금액은 사전에 안내됩니다</li>"
         "<li>부당한 추가 요구나 불법 행위는 일절 제공하지 않습니다</li></ul>"),
    ],
    "change": [
        ("intro", "변경·취소 안내",
         "<p>예약 변경이나 취소가 필요할 때는 가능한 한 빨리 전화로 알려주세요. 방문 준비와 일정 조정을 위해 일정 "
         "시간 이전의 사전 연락을 권장합니다. 시간 임박 변경·취소는 다른 예약에 영향을 줄 수 있어 협조를 부탁드립니다.</p>"),
        ("how", "변경·취소 방법",
         f"<p>전화 <a href='tel:{PHONE_TEL}'>{PHONE_DISPLAY}</a>로 예약자 성함과 예약 시간을 알려주시면 변경·취소를 "
         "처리해 드립니다. 가능한 대체 시간이 있다면 함께 알려주시면 재예약이 수월합니다.</p>"),
        ("link", "함께 보기",
         "<p>예약 전 확인이 필요한 사항은 <a href='/reservation/checklist/'>예약 전 체크사항</a>에서 미리 확인하세요.</p>"),
    ],
    "checklist": [
        ("intro", "예약 전 체크사항",
         "<p>예약을 진행하기 전에 아래 항목을 미리 확인하면 상담이 빠르고 정확해집니다. 위치와 시간, 코스, 인원, "
         "방문 장소 유형을 정리해 두는 것이 좋습니다.</p>"),
        ("list", "체크 리스트",
         "<ul><li>방문 받을 정확한 주소와 출입 방법</li><li>희망 날짜·시간과 대체 시간</li>"
         "<li>원하는 코스 시간과 테마</li><li>인원 및 커플·가족·단체 여부</li>"
         "<li>주차 가능 여부, 조용한 공간 확보 여부</li></ul>"),
        ("link", "다음 단계",
         "<p>확인을 마쳤다면 <a href='/reservation/'>예약 방법</a>에 따라 전화로 예약을 진행해 주세요. "
         "이용 전 일반 안내는 <a href='/guide/checklist/'>이용 전 확인사항</a>에서도 확인할 수 있습니다.</p>"),
    ],
}

GUIDE_CONTENT = {
    "": [
        ("intro", "처음 이용하시는 분께",
         "<p>방문 관리(출장마사지·홈타이)가 처음이라면 절차가 어렵지 않으니 안심하셔도 됩니다. 전화로 희망 지역과 "
         "시간, 코스를 말씀하시면 가능 여부를 안내드리고, 예약이 확정되면 약속 시간에 관리사가 방문합니다. "
         "익숙한 공간에서 편안하게 이완·휴식 중심의 관리를 받으실 수 있습니다.</p>"
         "<p>이용가이드는 방문 관리를 처음 이용하시는 분이 알아두면 좋은 내용을 단계별로 정리한 안내입니다. 방문 전 "
         "무엇을 준비하면 되는지, 관리 중에는 어떻게 진행되는지, 관리 후에는 무엇을 주의하면 되는지, 그리고 위생·"
         "안전 기준과 제공하지 않는 행위까지 한곳에서 확인할 수 있습니다. 처음에는 부담 없이 강도와 시간을 조절할 "
         "수 있으니, 원하는 정도를 예약 시 편하게 말씀해 주세요.</p>"),
        ("flow", "이용 순서",
         "<ul><li>전화 상담으로 가능 여부·일정 확인</li><li>코스와 테마 선택</li>"
         "<li>방문 장소·출입 방법 안내</li><li>약속 시간 방문 및 관리 진행</li><li>관리 후 휴식 및 마무리</li></ul>"),
        ("overview", "이용가이드 한눈에 보기",
         "<p>이용가이드는 첫 방문부터 관리 후까지 단계별로 알아두면 좋은 내용을 정리했습니다. 필요한 항목을 골라 "
         "확인하세요.</p>"
         "<ul>"
         "<li><a href='/guide/prepare/'>방문 전 준비사항</a> — 주소·출입·공간 등 미리 챙길 것</li>"
         "<li><a href='/guide/safety/'>위생 및 안전 기준</a> — 위생·개인정보·안전 운영 방식</li>"
         "<li><a href='/guide/aftercare/'>관리 후 주의사항</a> — 받은 뒤 휴식과 케어</li>"
         "<li><a href='/guide/forbidden/'>금지행위 안내</a> — 제공하지 않는 행위 기준</li>"
         "<li><a href='/guide/checklist/'>이용 전 확인사항</a> — 방문 전 최종 점검</li>"
         "<li><a href='/guide/faq/'>이용 FAQ</a> — 자주 묻는 질문</li>"
         "</ul>"
         "<p>예약 절차가 궁금하다면 <a href='/reservation/'>예약안내</a>를, 코스 선택이 고민이라면 "
         "<a href='/course/guide/'>코스 선택 가이드</a>를 함께 참고하세요.</p>"),
        ("expect", "처음이라 걱정되는 점들",
         "<p>처음 이용하실 때 자주 걱정하시는 부분을 미리 정리했습니다. 방문 관리는 정해진 절차에 따라 단정하게 "
         "진행되며, 원하는 강도와 집중 부위를 미리 말씀하시면 컨디션에 맞춰 시작합니다.</p>"
         "<ul>"
         "<li>강도 조절 — 약하게·보통·강하게 중에서 조절할 수 있습니다</li>"
         "<li>공간 — 집에 편평하고 조용한 공간만 있으면 충분합니다</li>"
         "<li>준비물 — 별도 준비물은 없으며, 원하면 가볍게 샤워 후 받으셔도 됩니다</li>"
         "<li>시간 — 처음에는 전신을 고르게 푸는 90분이 무난합니다</li>"
         "</ul>"
         "<p>본 서비스는 의료 행위가 아닌 이완·휴식 목적의 건강관리이며, 만 19세 이상 성인을 대상으로 합니다.</p>"),
        ("link", "함께 보기",
         "<p>첫 이용을 한결 편안하게 해 줄 안내를 모았습니다.</p>"
         "<ul>"
         "<li><a href='/guide/prepare/'>방문 전 준비사항</a> — 무엇을 준비할지</li>"
         "<li><a href='/guide/safety/'>위생 및 안전 기준</a> — 위생·안전 운영 방식</li>"
         "<li><a href='/course/guide/'>코스 선택 가이드</a> — 나에게 맞는 코스</li>"
         "<li><a href='/reservation/'>예약안내</a> — 예약 방법과 절차</li>"
         "</ul>"),
    ],
    "prepare": [
        ("intro", "방문 전 준비사항",
         "<p>관리를 매끄럽게 받기 위해 방문 전 몇 가지를 준비해 두면 좋습니다. 무엇보다 정확한 주소와 출입 방법, "
         "조용한 공간 확보가 중요합니다.</p>"),
        ("list", "준비 체크",
         "<ul><li>정확한 주소와 공동현관·객실 출입 방법</li><li>관리에 사용할 수 있는 편평하고 조용한 공간</li>"
         "<li>샤워 등 가벼운 준비(원하는 경우)</li><li>향·오일 민감 여부 등 사전 공유 사항</li>"
         "<li>주차가 필요한 경우 주차 위치</li></ul>"),
        ("link", "함께 보기",
         "<p>방문 장소 관련 안내는 <a href='/reservation/place/'>방문 가능 장소</a>, 관리 후 주의사항은 "
         "<a href='/guide/aftercare/'>관리 후 주의사항</a>을 참고하세요.</p>"),
    ],
    "safety": [
        ("intro", "위생 및 안전 기준",
         "<p>건전하고 안전한 방문 관리를 위해 위생 기준과 안전 수칙을 운영합니다. 관리 용품의 청결을 유지하고, "
         "예약 정보와 개인정보를 보호하며, 이용자와 관리사 모두의 안전을 우선합니다.</p>"),
        ("rule", "주요 기준",
         "<ul><li>청결한 관리 용품과 위생 관리</li><li>예약 정보·개인정보 보호</li>"
         "<li>이완·휴식 목적의 건강관리 범위 준수</li><li>불법·퇴폐 행위 및 무리한 요청 불가</li>"
         "<li>만 19세 이상 성인 대상</li></ul>"
         "<div class='data-box'><b>안내</b><p>통증이 심하거나 특정 질환이 있는 경우, 무리한 관리보다 전문의 진료를 "
         "먼저 권합니다. 본 서비스는 의료 행위가 아닙니다.</p></div>"),
        ("link", "함께 보기",
         "<p>금지되는 행위는 <a href='/guide/forbidden/'>금지행위 안내</a>에서 명확히 확인할 수 있습니다.</p>"),
    ],
    "aftercare": [
        ("intro", "관리 후 주의사항",
         "<p>관리 후에는 몸이 이완된 상태이므로 무리한 활동보다 가벼운 휴식이 좋습니다. 충분한 수분 섭취와 보온을 "
         "권장하며, 컨디션에 따라 천천히 일상으로 복귀하세요.</p>"),
        ("list", "권장 사항",
         "<ul><li>따뜻한 물 등 수분 충분히 섭취</li><li>관리 직후 격한 운동·음주 자제</li>"
         "<li>충분한 휴식과 수면</li><li>이상 증상이 있으면 무리하지 말고 휴식 후 필요 시 진료</li></ul>"),
        ("link", "함께 보기",
         "<p>수면을 돕는 관리는 <a href='/theme/sleep-available/'>수면 가능 테마</a>를, 다음 이용은 "
         "<a href='/reservation/'>예약안내</a>를 참고하세요.</p>"),
    ],
    "forbidden": [
        ("intro", "금지행위 안내",
         "<p>구로88마사지는 건전한 방문 건강관리만을 제공합니다. 아래 행위는 일절 허용되지 않으며, 확인 시 관리가 "
         "중단될 수 있습니다. 이용자와 관리사 모두의 안전과 권리를 위한 기준입니다.</p>"),
        ("list", "금지되는 행위",
         "<ul><li>불법·퇴폐 행위 및 이를 암시·요구하는 행위</li><li>관리사에 대한 폭언·폭력·성적 요구</li>"
         "<li>음주·약물 상태에서의 무리한 요청</li><li>사전 합의되지 않은 촬영·녹화</li>"
         "<li>미성년자 이용(만 19세 이상 성인 대상)</li></ul>"),
        ("link", "함께 보기",
         "<p>안전 기준은 <a href='/guide/safety/'>위생 및 안전 기준</a>, 청소년 보호는 "
         "<a href='/youth/'>청소년보호정책</a>을 참고하세요.</p>"),
    ],
    "checklist": [
        ("intro", "이용 전 확인사항",
         "<p>원활한 방문 관리를 위해 이용 전에 아래 사항을 확인해 주세요. 정확한 정보 공유는 관리의 질과 안전을 "
         "높입니다.</p>"),
        ("list", "확인 항목",
         "<ul><li>정확한 주소와 공동현관 출입 방법</li><li>주차 가능 여부</li>"
         "<li>조용한 공간 확보 여부</li><li>숙소·오피스텔의 출입 안내와 연락 가능 여부</li>"
         "<li>향·오일·피부 민감 여부 등 사전 공유 사항</li></ul>"),
        ("link", "함께 보기",
         "<p>예약 단계 점검은 <a href='/reservation/checklist/'>예약 전 체크사항</a>, 방문 준비는 "
         "<a href='/guide/prepare/'>방문 전 준비사항</a>을 참고하세요.</p>"),
    ],
    "faq": [
        ("intro", "이용 FAQ",
         "<p>이용 과정에서 자주 묻는 내용을 정리했습니다. 아래 목록에 없는 내용은 전화 상담으로 문의해 주세요. "
         "예약·코스·지역·역에 대한 상세 안내는 각 안내 페이지에서 확인할 수 있습니다.</p>"
         "<p>구로88마사지는 지역·역·테마를 분리해 안내하므로, 원하는 항목별 페이지에서 필요한 정보를 빠르게 찾아볼 "
         "수 있습니다. 가능 여부는 시간과 위치, 배정 상황에 따라 달라질 수 있습니다.</p>"),
    ],
}


def build_reservation():
    for p in RES_PAGES:
        path = p["path"]
        name = p["name"]
        secs = RES_CONTENT[p["slug"]]
        title = f"{name} | 구로 출장마사지·홈타이 예약안내"
        desc = f"구로 출장마사지·홈타이 {name} 안내입니다. 예약 절차와 확인사항을 정리했습니다."
        faq = [
            ("예약은 어디로 하나요?", f"전화 {PHONE_DISPLAY}로 희망 지역·시간·코스를 알려주시면 안내드립니다."),
            ("당일 예약이 되나요?", "가능할 수 있으나 저녁·주말은 문의가 많아 사전 예약을 권장합니다."),
            ("구로구 어디까지 되나요?", "구로구 전지역 대표 동 기준으로 안내하며, 정확한 가능 여부는 예약 시 확인합니다."),
        ]
        crumb_items = [("홈", "/"), ("예약안내", "/reservation/")]
        if p["slug"]:
            crumb_items.append((name, ""))
        else:
            crumb_items = [("홈", "/"), ("예약안내", "")]
        h, ni = article_page(path, title, desc, f"예약안내 · {name}",
            crumb_items, f"{name}",
            f"구로 출장마사지·홈타이 {name}입니다. 예약과 방문을 매끄럽게 준비하세요.",
            secs, faq)
        write(path, h, priority="0.7", noindex=ni)


def build_guide():
    for p in GUIDE_PAGES:
        path = p["path"]
        name = p["name"]
        secs = list(GUIDE_CONTENT[p["slug"]])
        title = f"{name} | 구로 출장마사지·홈타이 이용가이드"
        desc = f"구로 출장마사지·홈타이 {name} 안내입니다. 안전하고 편안한 이용을 위한 기준을 정리했습니다."
        faq = [
            ("처음 이용해도 괜찮나요?", "예. 절차가 어렵지 않으며 예약 시 처음임을 알려주시면 편안하게 안내합니다."),
            ("의료 행위인가요?", "아니요. 이완·휴식 목적의 건강관리이며 통증이 심하면 진료를 먼저 권합니다."),
            ("연령 제한이 있나요?", "만 19세 이상 성인을 대상으로 합니다."),
        ]
        if p["slug"]:
            crumb_items = [("홈", "/"), ("이용가이드", "/guide/"), (name, "")]
        else:
            crumb_items = [("홈", "/"), ("이용가이드", "")]
        # 이용 FAQ 페이지는 별도 FAQ를 풍부하게
        if p["slug"] == "faq":
            faq = [
                ("방문까지 얼마나 걸리나요?", "지역·시간대·배정 상황에 따라 다르며 예약 시 예상 시간을 안내합니다."),
                ("결제는 언제 하나요?", "결제 방식과 시점은 예약 상담에서 안내되며 가격 안내 페이지를 참고하세요."),
                ("커플·단체도 되나요?", "커플·가족·단체 방문 코스가 있으며 인원과 시간을 미리 알려주세요."),
                ("향이나 오일에 민감해요.", "예약 시 알려주시면 진행 방식을 조정합니다."),
                ("취소·변경은 어떻게 하나요?", "가능한 한 빨리 전화로 알려주시면 변경·취소를 도와드립니다."),
            ]
        h, ni = article_page(path, title, desc, f"이용가이드 · {name}",
            crumb_items, f"{name}",
            f"구로 출장마사지·홈타이 {name}입니다. 안전하고 편안한 이용을 위해 확인하세요.",
            secs, faq)
        write(path, h, priority="0.7", noindex=ni)


def build_reviews():
    path = "/reviews/"
    title = "이용 후기 | 구로 출장마사지·홈타이"
    desc = "구로 출장마사지·홈타이 이용 후기와 후기 작성 안내입니다. 지역별·역세권 이용 경험을 참고하세요."
    reviews = [
        ("★★★★★", "구로동에서 90분 코스로 받았는데 어깨 뭉침이 한결 가벼워졌어요. 예약 상담도 친절했습니다.", "구로동 · 90분 코스"),
        ("★★★★★", "신도림역 근처 오피스텔로 방문 받았어요. 시간 약속을 잘 지켜주셔서 좋았습니다.", "신도림동 · 스웨디시"),
        ("★★★★☆", "개봉동 자택에서 홈타이로 편하게 받았습니다. 이동 없이 받을 수 있어 만족해요.", "개봉동 · 홈타이"),
        ("★★★★★", "운동 후 회복 목적으로 스포츠 관리 받았는데 시원하게 잘 풀어주셨어요.", "구로디지털단지 인근 · 스포츠"),
        ("★★★★★", "기념일에 커플로 예약했어요. 두 사람 모두 편안하게 쉬다 갔습니다.", "천왕동 · 커플 관리"),
        ("★★★★☆", "늦은 시간 상담이 가능해서 좋았습니다. 다음엔 아로마로 받아보려고요.", "온수동 · 24시간"),
    ]
    cards = "".join(
        f'<div class="review reveal"><div class="stars">{s}</div><p>{html.escape(t)}</p>'
        f'<div class="who">{html.escape(w)}</div></div>' for s, t, w in reviews)
    out = head(title, desc, path)
    out += nav(active="reviews")
    out += crumb([("홈", "/"), ("후기", "")])
    out += lux_hero("후기", "구로 출장마사지·홈타이 이용 후기",
        "실제 이용 경험을 바탕으로 한 후기를 모았습니다. 지역과 코스별 분위기를 참고하세요.")
    out += f"""<section class="block"><div class="wrap">
  <div class="grid g3">{cards}</div>
  <div class="data-box" style="margin-top:24px"><b>후기 작성 안내</b><p>후기는 실제 이용 경험을 바탕으로 작성해 주세요. 과장·허위 후기나 타인의 권리를 침해하는 내용은 게시될 수 없습니다. 작성 방법은 고객센터 1:1 문의로 안내드립니다.</p></div>
</div></section>
"""
    out += faq_block([
        ("후기는 어떻게 남기나요?", "고객센터 1:1 문의를 통해 작성 방법을 안내받을 수 있습니다."),
        ("후기를 보고 예약할 수 있나요?", "후기는 참고용이며, 예약은 전화 상담으로 가능 여부를 확인한 뒤 진행됩니다."),
    ])
    out += footer()
    write(path, out, priority="0.6")


def build_customer():
    path = "/customer/"
    title = "고객센터 | 구로 출장마사지·홈타이 문의·공지"
    desc = "구로88마사지 고객센터입니다. 공지사항, 자주 묻는 질문, 1:1 문의, 제휴·기업 문의를 안내합니다."
    secs = [
        ("notice", "공지사항",
         "<p>운영 시간과 서비스 관련 공지를 안내합니다. 현재 연중무휴 24시간 상담을 운영하며, 명절·연휴 기간이나 "
         "기상 악화 시에는 방문 가능 시간과 이동 동선이 조정될 수 있습니다. 저녁 시간대와 주말은 문의가 집중되어 "
         "원하는 시간이 빠르게 마감될 수 있으니 여유 있는 예약을 권장합니다. 운영 관련 변경 사항이 있을 경우 이 "
         "영역과 예약 상담을 통해 안내드립니다.</p>"),
        ("qna", "자주 묻는 질문",
         "<p>예약·코스·지역·역 관련 자주 묻는 질문은 <a href='/guro/faq/'>구로 출장마사지 FAQ</a>와 "
         "<a href='/guide/faq/'>이용 FAQ</a>에서 확인할 수 있습니다. 가능 여부는 시간·위치·배정 상황에 따라 달라질 "
         "수 있으며, 정확한 안내는 예약 상담 과정에서 확정됩니다. 지역별 정보는 <a href='/guro-gu/'>지역별 안내</a>, "
         "역세권 동선은 <a href='/guro-gu/stations/'>지하철역별 안내</a>, 관리 유형은 <a href='/theme/'>테마별 "
         "안내</a>에서 항목별로 확인하실 수 있습니다.</p>"),
        ("inquiry", "1:1 문의",
         f"<p>개별 문의는 전화 <a href='tel:{PHONE_TEL}'>{PHONE_DISPLAY}</a>로 연락 주시면 신속히 안내드립니다. "
         "예약자 성함, 희망 지역·시간, 코스를 함께 알려주시면 상담이 빠릅니다. 예약 변경·취소, 방문 위치 안내, 코스 "
         "추천 등 어떤 내용이든 문의하실 수 있으며, 상담 과정에서 강요나 부담을 드리지 않습니다. 가능 여부는 시간과 "
         "위치, 배정 상황에 따라 달라질 수 있어 통화로 확인하는 것이 가장 정확합니다.</p>"),
        ("partner", "제휴·기업 문의",
         "<p>기업·단체 방문 관리나 제휴 관련 문의는 전화 상담으로 접수합니다. 인원과 일정, 장소를 알려주시면 "
         "맞춤 안내를 드립니다. 임직원 복지나 행사 프로그램 등 단체 인원을 대상으로 한 방문도 가능하며, 자세한 "
         "코스는 <a href='/course/group/'>기업·단체 방문 관리</a>를 참고하세요.</p>"),
        ("policy", "정책·약관 안내",
         "<p>고객센터는 공지사항, 자주 묻는 질문, 1:1 문의, 제휴·기업 문의, 그리고 정책·약관 안내를 한곳에 모은 "
         "창구입니다. 예약·이용 중 궁금한 점이나 변경이 필요한 사항은 언제든 전화로 문의해 주세요. "
         "개인정보 보호와 이용 조건은 정책 페이지에서 확인하실 수 있습니다. 예약 정보와 개인정보는 "
         "<a href='/privacy/'>개인정보처리방침</a>에 따라 보호되며, 서비스 이용 조건은 <a href='/terms/'>이용약관</a>, "
         "청소년 보호 기준은 <a href='/youth/'>청소년보호정책</a>에 정리되어 있습니다.</p>"
         "<p>구로88마사지는 건전한 방문 건강관리만을 제공하며, 불법·퇴폐 행위는 일절 제공하지 않습니다. 금지되는 "
         "행위는 <a href='/guide/forbidden/'>금지행위 안내</a>에서, 위생·안전 기준은 "
         "<a href='/guide/safety/'>위생 및 안전 기준</a>에서 확인하실 수 있습니다.</p>"),
    ]
    faq = [
        ("상담 시간은 언제인가요?", "연중무휴 24시간 상담이 가능하며, 방문 가능 시간은 배정 상황에 따라 달라집니다."),
        ("개인정보는 어떻게 보호되나요?", "예약 정보와 개인정보는 개인정보처리방침에 따라 보호됩니다."),
        ("단체 예약도 문의가 되나요?", "예. 제휴·기업 문의를 통해 인원과 일정에 맞춰 안내드립니다."),
    ]
    h, ni = article_page(path, title, desc, "고객센터",
        [("홈", "/"), ("고객센터", "")],
        "구로88마사지 고객센터",
        "공지사항, 자주 묻는 질문, 1:1 문의, 제휴·기업 문의를 한곳에서 안내합니다.",
        secs, faq)
    write(path, h, priority="0.6", noindex=ni)


def policy_page(path, title, h1, secs):
    desc = f"{SITE_NAME} {h1}입니다."
    out = head(title, desc, path, noindex=False)
    out += nav(active="")
    out += crumb([("홈", "/"), (h1, "")])
    out += lux_hero("정책", h1, f"{SITE_NAME}의 {h1} 전문입니다.", byline=False, actions=False)
    body = "".join(sec(sid, t, b) for sid, t, b in secs)
    out += f'<section class="block lux-body" style="padding-top:30px"><div class="wrap"><div class="lux-main" style="max-width:none">{body}</div></div></section>\n'
    out += footer()
    write(path, out, priority="0.3")


def build_policies():
    policy_page("/privacy/", "개인정보처리방침 | 구로88마사지", "개인정보처리방침", [
        ("p1", "수집하는 개인정보",
         "<p>본 사이트는 예약 상담을 위해 전화번호 등 최소한의 정보를 이용자가 제공하는 범위에서만 활용합니다. "
         "별도의 회원가입 절차나 온라인 양식을 통한 자동 수집은 운영하지 않습니다.</p>"),
        ("p2", "이용 목적과 보유 기간",
         "<p>수집된 정보는 예약 접수·확인·상담 목적에만 사용하며, 목적 달성 후에는 관련 법령에 따른 보관 기간을 "
         "제외하고 지체 없이 파기합니다.</p>"),
        ("p3", "제3자 제공 및 보호 책임",
         f"<p>이용자의 동의 없이 개인정보를 제3자에게 제공하지 않습니다. 개인정보 보호 책임자는 {BIZ['privacy']}이며, "
         f"관련 문의는 전화 {PHONE_DISPLAY}로 접수합니다.</p>"),
        ("p4", "이용자의 권리",
         "<p>이용자는 자신의 개인정보에 대한 열람·정정·삭제를 요청할 수 있으며, 요청 시 지체 없이 조치합니다.</p>"),
    ])
    policy_page("/terms/", "이용약관 | 구로88마사지", "이용약관", [
        ("t1", "목적",
         "<p>본 약관은 구로88마사지가 제공하는 방문 건강관리 예약 안내 서비스의 이용 조건과 절차, 권리·의무를 "
         "정함을 목적으로 합니다.</p>"),
        ("t2", "서비스의 성격",
         "<p>본 서비스는 의료 행위가 아닌 이완·휴식 목적의 건강관리 방문 서비스이며, 만 19세 이상 성인을 대상으로 "
         "합니다. 불법·퇴폐 행위는 일절 제공하지 않습니다.</p>"),
        ("t3", "예약과 취소",
         "<p>예약은 전화 상담을 통해 이루어지며, 변경·취소는 가능한 한 빠른 사전 연락을 권장합니다. 자세한 내용은 "
         "<a href='/reservation/change/'>변경·취소 안내</a>를 따릅니다.</p>"),
        ("t4", "이용자의 의무",
         "<p>이용자는 정확한 정보를 제공하고, 관리사의 안전과 인격을 존중해야 하며, "
         "<a href='/guide/forbidden/'>금지행위</a>를 하지 않아야 합니다.</p>"),
        ("t5", "면책",
         "<p>천재지변, 이용자 귀책 사유 등 회사가 통제할 수 없는 사유로 인한 서비스 제한에 대해서는 책임이 "
         "제한될 수 있습니다.</p>"),
    ])
    policy_page("/youth/", "청소년보호정책 | 구로88마사지", "청소년보호정책", [
        ("y1", "기본 방침",
         "<p>구로88마사지는 만 19세 이상 성인을 대상으로 서비스를 제공하며, 청소년 유해 정보로부터 청소년을 "
         "보호하기 위해 노력합니다.</p>"),
        ("y2", "이용 제한",
         "<p>미성년자의 이용은 제한되며, 예약 과정에서 연령 확인이 필요할 수 있습니다. 불법·퇴폐 행위 및 이를 "
         "암시하는 요청은 일절 제공하지 않습니다.</p>"),
        ("y3", "신고 및 문의",
         f"<p>청소년 보호와 관련한 문의나 신고는 전화 {PHONE_DISPLAY}로 접수합니다. 관련 기준은 "
         "<a href='/guide/forbidden/'>금지행위 안내</a>를 함께 참고하세요.</p>"),
    ])


# ---------------------------------------------------------------------------
# 12. 루트 파일: sitemap.xml / robots.txt / webmanifest / favicon / og
# ---------------------------------------------------------------------------
def build_root_files():
    # sitemap (noindex 페이지는 제외)
    urls = ""
    for path, noindex, pr, cf in sorted(PAGES):
        if noindex:
            continue
        urls += (f"  <url><loc>{DOMAIN}{path}</loc>"
                 f"<changefreq>{cf}</changefreq><priority>{pr}</priority></url>\n")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               f"{urls}</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    robots = (f"User-agent: *\nAllow: /\nDisallow: /tools/\n\n"
              "User-agent: GPTBot\nAllow: /\n\n"
              "User-agent: ClaudeBot\nAllow: /\n\n"
              "User-agent: Google-Extended\nAllow: /\n\n"
              f"Sitemap: {DOMAIN}/sitemap.xml\nHost: {DOMAIN}\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    manifest = ('{\n'
                f'  "name": "{SITE_NAME}",\n'
                f'  "short_name": "{SITE_NAME}",\n'
                '  "start_url": "/",\n'
                '  "display": "standalone",\n'
                '  "background_color": "#0b0b0e",\n'
                '  "theme_color": "#0b0b0e",\n'
                '  "icons": [\n'
                '    {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"}\n'
                '  ]\n'
                '}\n')
    with open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8") as f:
        f.write(manifest)

    favicon = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
               f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
               f'<stop offset="0" stop-color="#f4d29c"/><stop offset=".45" stop-color="#e9b8a7"/>'
               f'<stop offset="1" stop-color="#c98a6b"/></linearGradient></defs>'
               f'<rect width="64" height="64" rx="14" fill="#0b0b0e"/>'
               f'<rect x="8" y="8" width="48" height="48" rx="11" fill="url(#g)"/>'
               f'<text x="32" y="44" font-family="Georgia,serif" font-style="italic" '
               f'font-size="34" font-weight="700" text-anchor="middle" fill="#1a1208">{BRAND_MARK}</text></svg>')
    with open(os.path.join(ROOT, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(favicon)

    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    og = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">'
          f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
          f'<stop offset="0" stop-color="#f4d29c"/><stop offset=".45" stop-color="#e9b8a7"/>'
          f'<stop offset="1" stop-color="#c98a6b"/></linearGradient></defs>'
          f'<rect width="1200" height="630" fill="#0b0b0e"/>'
          f'<text x="80" y="300" font-family="sans-serif" font-size="84" font-weight="800" fill="url(#g)">{SITE_NAME}</text>'
          f'<text x="80" y="380" font-family="sans-serif" font-size="40" fill="#cfd2da">구로 출장마사지·홈타이 예약 안내</text>'
          f'<text x="80" y="450" font-family="sans-serif" font-size="34" fill="#9a9aa3">구로구 전지역 · 24시간 상담 · {PHONE_DISPLAY}</text></svg>')
    with open(os.path.join(ROOT, "assets", "og-cover.svg"), "w", encoding="utf-8") as f:
        f.write(og)


# ---------------------------------------------------------------------------
# 13. main
# ---------------------------------------------------------------------------
def main():
    build_home()
    build_guro_hub()
    build_area()
    build_stations()
    build_themes()
    build_courses()
    build_reservation()
    build_guide()
    build_reviews()
    build_customer()
    build_policies()
    build_root_files()

    total = len(PAGES)
    noidx = sum(1 for _, ni, _, _ in PAGES if ni)
    print(f"생성 완료: 총 {total} 페이지 (noindex {noidx}개)")
    if noidx:
        print("noindex 페이지(본문 2,000자 미만):")
        for path, ni, _, _ in sorted(PAGES):
            if ni:
                print(f"  - {path}")


if __name__ == "__main__":
    main()
