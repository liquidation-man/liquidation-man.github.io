# AGENTS.md — Codex 등 CLAUDE.md 를 읽지 않는 에이전트용 진입점

> ### 글을 쓰기 전에 [`CLAUDE.md`](CLAUDE.md) 를 읽는다.

내용을 여기 복제하지 않는다 — 갈라지기 때문이다. 대신 **어겼을 때 되돌리기 어려운 것 하나만** 옮겨 둔다.

## 절대 금지

**클로드 코드(또는 유사 AI 코딩 도구) 자체의 동작·오류·함정과 그 원인·해결책을 글로 쓰지 않는다.**

같은 소재로 만든 **유료 전자책**이 팔리고 있다(4,900원). 이 블로그는 무료다.
여기에 결론을 적으면 파는 물건을 공짜로 주는 것이다.

- ✅ **무엇을 만들었는지**는 쓴다. 개발일지의 원래 목적이다.
- ❌ **도구의 함정과 해법**은 쓰지 않는다.
  (예: 「없다고 한 프로그램이 사실은 PATH 문제였다」 — 이게 책 6장이다)

막히는 여덟 가지 주제와 판정 기준은 `CLAUDE.md` 의 표에 있다.
`.github/workflows/no-ebook-spoiler.yml` 이 자동으로 검사하고, 걸리면 빨간 X 가 뜬다.
(배포는 막지 않는다.)

## 그 밖에

- 테마는 서브모듈이다: `git submodule update --init --depth 1 themes/PaperMod`
- 레이아웃 확장은 `layouts/_partials/` — 글 하단은 `extend_post_content.html`
- 이 PC 에 Hugo 가 없다. 로컬 빌드 검증 불가 — push 후 Actions 로 확인한다.
- 전체 맥락: `liquidation-man/side-projects` 의 `CONTEXT.md`
