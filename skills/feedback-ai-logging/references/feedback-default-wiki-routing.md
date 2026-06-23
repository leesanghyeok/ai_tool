# Feedback 기본 wiki 경로 라우팅 주의사항

## 배경

feedback logging 실행 중 runtime에 project wiki routing이 설정되어 있을 수 있다.

```text
WIKI_PATHS=marketing=/Users/stark/Documents/marketing-wiki
WIKI_DEFAULT=marketing
```

이 상태에서 일반 wiki 작업은 domain wiki로 가도 되지만, feedback log는 cross-project 품질 데이터이므로 사용자가 명시하지 않은 domain wiki에 자동 저장하면 안 된다.

기본 feedback log 목적지는 다음이다.

```text
$HOME/wiki/raw/feedback
```

## 지속 규칙

`WIKI_PATHS`와 `WIKI_DEFAULT`는 일반 wiki 작업을 domain/project wiki로 route할 수 있다. 그러나 feedback incident log는 agent 품질 개선용 raw data이므로 domain default를 조용히 따라가지 않는다.

기본 routing 우선순위:

1. 사용자가 명시한 feedback wiki path가 있으면 그것을 사용한다.
2. 없으면 `FEEDBACK_WIKI_PATH`를 사용한다.
3. 없으면 feedback/general wiki 용도로 명시된 `WIKI_PATH`를 사용한다.
4. 없으면 `$HOME/wiki`를 사용한다.
5. 사용자가 해당 domain wiki를 feedback 목적지로 명시하지 않았다면 `WIKI_PATHS`/`WIKI_DEFAULT`를 feedback default로 사용하지 않는다.

## 복구 절차

log가 잘못된 domain wiki에 작성되었으면 다음 순서로 복구한다.

1. `<domain-wiki>/raw/feedback/YYYY-MM-DD/` 아래 생성 파일을 식별한다.
2. 각 incident file을 `$HOME/wiki/raw/feedback/YYYY-MM-DD/`로 이동한다.
3. body content는 수정하지 않는다.
4. `session_id`가 실제로 틀린 경우가 아니면 filename과 frontmatter를 보존한다.
5. 이동 후 body-only `sha256`을 재계산 또는 검증한다.
6. 잘못된 feedback directory가 비었고 안전하면 제거한다.
7. old path와 new path를 모두 보고한다.

## 검증 체크리스트

- [ ] 목적지가 `$HOME/wiki/raw/feedback` 또는 사용자가 명시한 feedback wiki다.
- [ ] 잘못된 domain wiki path에 residual feedback file이 남아 있지 않다.
- [ ] 이동된 각 파일의 body-only `sha256`이 유효하다.
- [ ] 최종 보고가 실제 destination path를 포함한다.
