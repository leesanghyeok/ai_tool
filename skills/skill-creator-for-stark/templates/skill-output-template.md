# 스킬 작업 결과 템플릿

상태: `completed | partial | blocked | unverified`

## 변경 파일

- `SKILL.md`: <path 또는 변경 없음>
- `references/`: <path 목록 또는 []>
- `templates/`: <path 목록 또는 []>
- `scripts/`: <path 목록 또는 []>
- `history/`: <path 또는 생략 사유>

## 핵심 설계 결정

- <최소 입력/출력/환경 계약 결정>
- <domain-specific hard gate 결정>
- <trigger section 통합 방식>
- <templates/와 references/ 분리 결정>

## 검증 결과

- `validator`: <command와 실제 결과>
- `syntax/read-back`: <실제 결과>
- `git diff --check`: <실제 결과 또는 생략 사유>
- `fixture`: <positive/negative fixture 결과 또는 생략 사유>

## 품질 평가

- 실행 여부: <실행/생략>
- 기준: `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md`
- 결과: <certification_score, D1-D5 hard gate, pass/fail 또는 생략 사유>

## 실패/차단/미확인

| 항목 | 값 |
|---|---|
| `failed_command_or_tool` | <없음 또는 실패 단위> |
| `actual_error` | <없음 또는 핵심 오류> |
| `impact` | <완료/검증/품질 판정 영향> |
| `recovery_action` | <다음 복구 행동> |
| `unverified_items` | <미검증 항목 또는 없음> |

## 다음 단계

- <commit, 후속 스킬 수정, 추가 승인점 등>
