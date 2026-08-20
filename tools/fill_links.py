#!/usr/bin/env python3
"""추천 페이지의 링크 슬롯을 쿠팡 딥링크로 채운다.

    python3 tools/fill_links.py 1=https://link.coupang.com/... 3=https://...

슬롯 번호는 content/recommend.md 의 `<!-- SLOT:N -->` 주석과 짝이다.
주는 것만 채우고 나머지는 「준비 중」으로 남긴다 — 부분 납품이 가능해야
오너가 한 번에 여섯 개를 다 만들 필요가 없다.
"""
import re
import sys
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "content" / "recommend.md"
SLOT = re.compile(r"→ \*\*(?P<label>[^*]+)\*\* — 링크 준비 중 <!-- SLOT:(?P<n>\d+) -->")
DONE = re.compile(r"→ \[(?P<label>[^\]]+?) 보기\]\((?P<url>[^)]+)\) <!-- SLOT:(?P<n>\d+) -->")


def main() -> int:
    given = {}
    for arg in sys.argv[1:]:
        if "=" not in arg:
            print(f"❌ 형식이 아니다: {arg}  (예: 1=https://link.coupang.com/...)")
            return 2
        n, url = arg.split("=", 1)
        url = url.strip()
        if not url.startswith("https://"):
            print(f"❌ https 링크가 아니다: {url}")
            return 2
        given[n.strip()] = url

    text = PAGE.read_text(encoding="utf-8")

    def swap(m: re.Match) -> str:
        n = m.group("n")
        if n not in given:
            return m.group(0)
        return f"→ [{m.group('label')} 보기]({given.pop(n)}) <!-- SLOT:{n} -->"

    text = SLOT.sub(swap, text)
    # 이미 채워진 슬롯을 다시 주면 갈아끼운다
    def replace_done(m: re.Match) -> str:
        n = m.group("n")
        if n not in given:
            return m.group(0)
        return f"→ [{m.group('label')} 보기]({given.pop(n)}) <!-- SLOT:{n} -->"

    text = DONE.sub(replace_done, text)

    if given:
        print(f"⚠️ 짝이 없는 슬롯 번호: {', '.join(sorted(given))}")

    remaining = len(SLOT.findall(text))
    if remaining == 0:
        before = text
        text = re.sub(r"\n> \*\*구매 링크는 준비 중입니다\.\*\*\n", "\n", text)
        print("· 전부 채워졌다"
              + (" — 「준비 중」 안내를 지웠다" if text != before else " (안내 문구를 못 찾았다)"))
    PAGE.write_text(text, encoding="utf-8")
    print(f"· 남은 빈 슬롯: {remaining}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
