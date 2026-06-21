# AI Tool

PR 워크플로우용 AI agent 스킬을 담은 저장소입니다.

스킬 본문은 특정 에이전트 런타임에 종속되지 않는 공통 포맷으로 관리하며,
Codex에서는 플러그인 매니페스트를 통해 그대로 사용할 수 있습니다.

## 구성

- `feedback-ai-loggin`: AI/agent 출력 불만족 사례를 LLM Wiki `raw/feedback/` 아래에 구조화된 Markdown 로그로 남깁니다.
- `llm-wiki`: Karpathy LLM Wiki 방식의 상호 링크된 Markdown 지식 베이스를 생성/조회/관리합니다. `WIKI_PATHS`/`WIKI_DEFAULT`로 여러 주제별 wiki를 선택할 수 있습니다.
- `pr-review`: 현재 브랜치의 PR을 리뷰하고, 구조화된 GitHub 리뷰 코멘트를 게시합니다.
- `pr-review-apply`: 기존 PR 리뷰 피드백을 확인하고, 승인된 변경을 반영한 뒤 검증과 리뷰 스레드 답글까지 처리합니다.
- `rubric-design`: AI 출력, 문서, 연구 요약, 에이전트 작업 등을 평가하기 위한 체크리스트형 루브릭을 설계·보정합니다.

## 디렉토리 구조

- `skills/`: 공통 스킬 루트
- `.codex-plugin/plugin.json`: Codex 호환 플러그인 매니페스트
- `scripts/link_codex_skills.sh`: 기존 Codex 홈 symlink 방식 설치 스크립트

## Codex 호환 매니페스트

이 저장소는 Codex 플러그인 루트로도 사용할 수 있습니다.

- 매니페스트: `.codex-plugin/plugin.json`
- 스킬 경로: `./skills/`

## 설치

스킬 디렉토리를 지원하는 에이전트에서는 `skills/`를 스킬 루트로 등록해서 사용할 수 있습니다.

Codex에서는 이 저장소를 로컬 또는 Git 기반 플러그인 소스로 등록해서 사용할 수 있습니다.

```text
git@github.com:leesanghyeok/ai_tool.git
```

설치 후에는 사용하는 에이전트의 스킬 호출 문법에 맞춰 스킬 이름으로 호출합니다.

Codex 호환 호출 예시:

```text
Use $feedback-ai-loggin to record AI output dissatisfaction as a feedback log.
Use $llm-wiki to build or query an interlinked Markdown knowledge base.
Use $pr-review to review the current branch PR.
Use $pr-review-apply to apply current PR review feedback.
Use $rubric-design to design or calibrate scoring rubrics.
```

## 기존 Codex symlink 방식 설치

`CODEX_HOME/skills`를 직접 사용하는 환경에서는 아래 스크립트로 공통 `skills/` 아래의 스킬들을 링크할 수 있습니다.

```bash
./scripts/link_codex_skills.sh
```
