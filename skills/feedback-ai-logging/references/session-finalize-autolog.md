# 세션 종료 feedback 자동 수확 패턴

사용자가 Hermes session 종료 시 `feedback-ai-logging`을 자동 실행하고 싶다고 요청할 때 이 참고 문서를 사용한다. 이 문서가 session-finalize 자동화의 canonical reference다.

## 권장 통합 방식

Gateway-only hook이나 직접 Markdown 쓰기보다 Hermes user plugin lifecycle hook을 우선한다.

1. user plugin에서 `on_session_finalize` hook을 등록한다.
2. hook callback은 transcript 분석이나 `raw/feedback/` 파일 작성을 직접 하지 않는다.
3. callback은 별도 Hermes one-shot child process를 spawn하고 즉시 return한다.
4. child process는 종료 대상 session을 `--resume`하고 이 skill을 preload한다.
5. incident detection, idempotency, frontmatter, body section, body-only `sha256`, wiki write는 모두 `feedback-ai-logging` skill이 담당한다.

권장 command shape:

```bash
HERMES_FEEDBACK_AUTOLOG_CHILD=1 hermes --resume "$SESSION_ID"   --skills feedback-ai-logging   chat --source feedback-autolog   -q 'feedback-ai-logging 스킬을 사용해 resume된 세션의 feedback 사건을 수확하세요. 중복이면 새 파일을 만들지 말고, 근거 부족/비실패이면 기록하지 마세요.'
```

## 직접 파일 쓰기보다 안전한 이유

- hook은 작은 trigger로 남고 skill 규칙을 중복 구현하지 않는다.
- child Hermes process가 target session을 resume해 현재 skill 지침을 적용한다.
- idempotency, controlled taxonomy, frontmatter, body-only `sha256` 규칙이 한 곳에 유지된다.
- 느리거나 실패한 child process가 core session finalization을 막지 않는다.
- 나중에 이 skill을 개선하면 autolog behavior도 함께 개선된다.

## Hook 선택 기준

`on_session_finalize`는 Hermes session lifecycle hook이다. Gateway-only `session:end`보다 넓으며 CLI/gateway session boundary를 모두 다룰 수 있다.

포함되는 예:

- shutdown
- `/new`
- `/reset`
- idle 또는 daily expiry
- manual reset

`on_session_finalize`를 “Discord thread close”와 동일시하지 않는다.

- Discord thread archive/close/delete는 platform object event다.
- Hermes session finalize는 internal conversation lifecycle event다.
- Discord thread conversation도 idle expiry, daily reset, `/new`, `/reset`, gateway shutdown 시점에 나중에 finalize될 수 있다.
- “Discord thread archive/delete 즉시 실행”이 요구사항이면 Discord adapter thread lifecycle listener를 별도로 추가하고 thread id를 Hermes session id에 mapping한다.

## 필수 safety guard

- **재귀 방지:** child env에 `HERMES_FEEDBACK_AUTOLOG_CHILD=1`을 설정하고, hook callback은 이 값이 있으면 즉시 skip한다.
- **누락 세션 방지:** 비어 있거나 `None` 또는 `unknown-session`인 id는 skip한다.
- **중복 실행 방지:** 같은 `session_id`가 여러 finalize surface에서 반복 spawn되지 않도록 작은 seen-state를 유지한다.
- **종료 사유 allowlist:** 기본값은 `shutdown`, `new_session`, `session_expired`, `reset`, `manual_reset` 같은 Hermes lifecycle reason으로 제한한다.
- **명시 opt-in 또는 dry-run:** 초기 운영은 `HERMES_FEEDBACK_AUTOLOG_DRY_RUN=1` 또는 `HERMES_FEEDBACK_AUTOLOG_ENABLED=1` 같은 명시 gate 뒤에서 시작한다.
- **로그 기록:** `dry_run`, `spawn_start`, `spawned`, `skip`, `error` event를 JSONL로 `~/.hermes/logs/<plugin>.log`에 기록한다.
- **실패 격리:** hook 실패가 session shutdown/finalization을 막지 않게 log만 남기고 return한다.
- **Skill 멱등성 유지:** plugin seen-state는 spawn 최적화일 뿐이며 최종 duplicate 방지는 skill workflow가 기존 `raw/feedback/`를 검색해 수행한다.

## 검증 체크리스트

- [ ] plugin이 `hermes plugins list --plain --no-bundled`에서 enabled로 보인다.
- [ ] plugin manager가 `hooks=1`, `error=None`으로 load한다.
- [ ] dry-run hook invocation이 wiki file을 쓰지 않고 child command를 log한다.
- [ ] child guard invocation이 `reason=child_guard` 또는 equivalent skip log를 남기고 spawn하지 않는다.
- [ ] 같은 `session_id`에 대한 반복 finalize event가 첫 실행 이후 `already_seen` 또는 equivalent를 log한다.
- [ ] gateway가 이미 실행 중이었다면 restart 후 새 plugin이 gateway session에 반영된다.
- [ ] production end-to-end 검증은 실제 session finalize event 후 plugin log, seen-state, `$WIKI/raw/feedback/YYYY-MM-DD/`를 모두 확인한다.
