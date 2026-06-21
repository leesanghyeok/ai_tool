# Feedback Log 파일명 포맷 마이그레이션

Raw feedback log의 파일명 규칙이 바뀌었고 기존 파일도 새 규칙에 맞춰야 할 때 이 reference를 사용한다.

## 현재 규칙

Feedback log는 다음 위치에 저장된다.

```text
$WIKI/raw/feedback/YYYY-MM-DD/{HHMMSS}-{session_id}-{short-slug}.md
```

`HHMMSS` 구성요소는 파일 수정 시간이 아니라 해당 파일의 `created_at` frontmatter에서 가져와야 한다.

## 안전한 마이그레이션 절차

1. 스킬의 일반 wiki path 규칙에 따라 active wiki path를 결정한다.
2. `raw/feedback/*/*.md` 아래의 기존 파일을 열거한다.
3. 각 파일의 frontmatter를 읽고 다음 값을 추출한다.
   - `session_id`
   - `created_at`
4. `created_at`에서 `HHMMSS`를 파싱한다.
5. 가능한 경우 기존 slug를 보존한다.
   - Old canonical form: `{session_id}-{HHMMSS}-{slug}.md`
   - Older mixed form: `-{HHMMSS}-` marker를 찾아 그 뒤 suffix를 slug로 사용한다.
6. `{HHMMSS}-{session_id}-{slug}.md`로 rename한다.
7. Target file이 이미 있으면 덮어쓰지 말고 중단한다.
8. 다음을 검증한다.
   - 모든 feedback Markdown filename이 현재 규칙과 일치한다.
   - Old canonical pattern이 남아 있지 않다.
   - 파일 내용과 body hash는 변경되지 않았다.
9. Wiki에 `log.md`가 있으면 old → new path를 나열하는 compact entry를 append한다.

## 주의사항

- 파일명만 바꿀 때 `sha256`을 다시 계산하거나 변경하지 않는다. Hash는 path가 아니라 Markdown body를 대상으로 한다.
- `created_at`이 있으면 old filename에서 시간을 추론하지 않는다. Frontmatter가 source of truth다.
- Filename migration 중 raw feedback body text를 수정하지 않는다. Raw incident는 immutable이며, filesystem rename은 metadata hygiene에 해당한다.
- Wiki가 git repository라고 가정하지 않는다. Verification에 git status를 쓰기 전에 먼저 확인한다.
