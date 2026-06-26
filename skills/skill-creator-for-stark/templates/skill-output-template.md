# 스킬 생성 결과 템플릿

## 생성/수정 결과

### INPUT 값

| 변수 | 필수 | 사용값 | 기본값 | 설명 |
|---|---:|---|---|---|
| `INPUT_SKILL_GOAL` | required |  | 없음 | 만들거나 수정한 스킬의 목적. |
| `INPUT_TRIGGER_CONDITIONS` | required |  | 없음 | 스킬 사용 조건과 near-miss 경계. |
| `INPUT_REPO_ROOT` | required |  | 현재 작업 repository | 작업 기준 repository root. |
| `INPUT_SKILL_ROOT` | required |  | `<INPUT_REPO_ROOT>/skills` | 스킬 디렉터리 root. |
| `INPUT_SKILL_NAME` | required |  | 없음 | 생성/수정한 skill name과 directory basename. |
| `INPUT_CONSTRAINTS` | optional |  | 사용자 고정 규칙 + 현재 요청 | 적용한 제약. |
| `INPUT_APPROVAL_SCOPE` | required |  | 없음 | 승인된 파일 쓰기/수정 범위. |
| `INPUT_HISTORY_POLICY` | optional |  | `history/YYYYMMDD-<topic>.md` | history 기록 정책. |
| `INPUT_TRIGGER_EXAMPLE_POLICY` | optional |  | `draft_min_3_each` | trigger 예시 작성 정책. |
| `INPUT_WORKFLOW_MODE` | required |  | 없음 | `create`, `modify`, `quality-review-only` 중 실제 작업 mode. |
| `INPUT_SKILL_QUALITY_RUBRIC_PATH` | optional |  | `/Users/stark/project/jarvis/ai_tool/rubric/skill/skill-quality-rubric-v1.md` | 품질 평가에 사용한 rubric path. |
| `INPUT_MIN_QUALITY_SCORE` | optional |  | `95` | 완료로 인정할 최소 `certification_score`. |
| `INPUT_QUALITY_EVALUATION_REQUIRED` | optional |  | mode별 기본값 | 품질 평가 필수 여부. |
| `INPUT_QUALITY_EVALUATION_MODE` | optional |  | `clean_subagent` | 품질 평가 실행 방식. |

### OUTPUT 산출물

| 변수 | 필수 | 값 | 기본값 | 설명 |
|---|---:|---|---|---|
| `OUTPUT_SKILL_DIR` | required |  | 없음 | 생성/수정된 skill directory. |
| `OUTPUT_SKILL_MD` | required |  | 없음 | 생성/수정된 `SKILL.md`. |
| `OUTPUT_REFERENCES` | optional |  | `[]` | 생성/수정된 reference files. |
| `OUTPUT_TEMPLATES` | optional |  | `[]` | 생성/수정된 template files. |
| `OUTPUT_SCRIPTS` | optional |  | `[]` | 생성/수정된 deterministic scripts. |
| `OUTPUT_HISTORY_RECORD` | optional |  | 없음 | 생성/수정 이력 파일. |
| `OUTPUT_TRIGGER_EXAMPLES` | required |  | 없음 | `should_trigger` / `should_not_trigger` 예시 또는 파일. |
| `OUTPUT_VERIFICATION_RESULT` | required |  | 없음 | 실행한 검증과 실제 결과. |
| `OUTPUT_OPEN_QUESTIONS` | optional |  | `[]` | 미확인 사항. |
| `OUTPUT_WORKFLOW_MODE` | required |  | 없음 | 실제 적용한 workflow mode. |
| `OUTPUT_QUALITY_SCORECARD` | optional |  | 없음 | 품질 평가 JSON scorecard 또는 저장 경로. |
| `OUTPUT_QUALITY_CERTIFICATION` | optional |  | 없음 | 95점 기준 품질 판정. |
| `OUTPUT_QUALITY_FIXES` | optional |  | `[]` | 95점 미만 또는 hard gate 실패 시 우선 수정 목록. |
| `OUTPUT_QUALITY_EVALUATION_SKIPPED_REASON` | optional |  | 없음 | 수정 모드에서 품질 평가를 생략한 사유. |
| `OUTPUT_NEXT_ACTIONS` | optional |  | `[]` | 다음 단계. |
### 실패/차단 보고

| 필드 | 값 | 설명 |
|---|---|---|
| `failed_command_or_tool` |  | 실패한 command, API, tool, subagent, validator 이름. |
| `expected_result` |  | 기대한 통과 조건 또는 출력. |
| `actual_error` |  | 실제 error, exit code, score, blocker. |
| `likely_cause` |  | 확인된 원인 또는 근거 있는 추정 원인. |
| `impact` |  | 완료 주장, 품질 통과, 파일 안전성에 미치는 영향. |
| `recovery_action` |  | 다음 복구 행동, 재시도 조건, 대체 경로. |
| `status_class` |  | `blocked`, `partial`, `unverified`, `failed`, `recovered` 중 현재 상태. |
| `retry_condition` |  | 같은 방법으로 재시도해도 되는 조건과 재시도하지 말아야 할 조건. |
| `alternative_path` |  | 재시도가 부적절할 때 사용할 대체 도구, 수동 확인, 축소 scope. |
