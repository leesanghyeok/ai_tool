# AI Tool

PR 워크플로우용 Codex 스킬을 담은 플러그인입니다.

## 구성

- `pr-review`: 현재 브랜치의 PR을 리뷰하고, 구조화된 GitHub 리뷰 코멘트를 게시합니다.
- `pr-review-apply`: 기존 PR 리뷰 피드백을 확인하고, 승인된 변경을 반영한 뒤 검증과 리뷰 스레드 답글까지 처리합니다.

## 플러그인 매니페스트

이 저장소는 Codex 플러그인 루트로 사용할 수 있습니다.

- 매니페스트: `.codex-plugin/plugin.json`
- 스킬 경로: `./codex/skills/`

## 설치

이 저장소를 로컬 또는 Git 기반 Codex 플러그인 소스로 등록해서 사용할 수 있습니다.

```text
git@github.com:leesanghyeok/ai_tool.git
```

설치 후에는 스킬 이름으로 호출합니다.

```text
Use $pr-review to review the current branch PR.
Use $pr-review-apply to apply current PR review feedback.
```

## 기존 symlink 방식 설치

`CODEX_HOME/skills`를 직접 사용하는 환경에서는 아래 스크립트를 사용할 수 있습니다.

```bash
./codex/scripts/link_codex_skills.sh
```
