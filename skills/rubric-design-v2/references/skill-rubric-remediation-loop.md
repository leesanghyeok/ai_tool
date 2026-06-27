# Skill 루브릭 개선 루프

사용자가 agent skill을 skill 품질 루브릭 통과 수준으로 개선하거나 목표 점수까지 끌어올리라고 요청할 때 이 참고 문서를 사용한다.

## 사용 조건

- skill 패키지가 체크리스트 rubric으로 평가됐고 하드 게이트를 실패했다.
- 사용자가 skill을 통과시키거나 95점 이상 같은 목표 점수에 도달하도록 개선해 달라고 요청한다.
- 대상이 수정 가능한 skill/패키지이며, 보호된 bundled skill 또는 hub-installed skill이 아니다.

## 작업 절차

1. 루브릭 점수카드를 일반 조언이 아니라 개선 지도로 취급한다.
   - 하드 게이트 차단 이슈를 먼저 나열한다.
   - 지역/전역 상한을 제거하는 최소 수정부터 찾는다.
   - 새 좁은 skill을 만들기보다 대상 skill과 기존 references를 수정하는 것을 선호한다.

2. skill의 class-level 절차 계층을 수정한다.
   - 반복 규칙은 `SKILL.md`에 둔다.
   - 상세 runbook, schema, 예시, source-specific 절차, session-derived 세부사항은 `references/` 아래에 둔다.
   - one-session 서사를 추가하지 않는다.

3. 품질 차원 최적화보다 하드 게이트를 먼저 닫는다.
   - 승인/보안/개인정보 gap은 보통 main `SKILL.md` 본문에 속한다.
   - 검증, 결정론적 검사, 보고 templates, 실패 라벨은 evaluator가 추론하지 않아도 될 만큼 명시한다.

4. 루브릭이 보상하는 곳에는 기계 검증 가능한 근거를 추가한다.
   - 고정 JSON schema.
   - parse 가능한 shard output.
   - 결정론적 preflight 검사.
   - read-back 또는 diff 검증.

5. large 또는 다차원 skill evaluation은 clean shard로 다시 채점한다.
   - clean subagent 또는 동등한 isolated judge에 차원을 나눈다.
   - shard judge는 최종 전역 점수를 계산하지 않는다.
   - parent가 score를 집계하고, cap을 적용하며, 모순을 조정한다.

6. 성공을 주장하기 전에 edit를 검증한다.
   - 변경 section을 read back한다.
   - 해당 file에 가능한 syntax/format 검사를 실행한다.
   - schema가 추가됐다면 JSON code block을 parse한다.
   - rubric 기준으로 re-score하고 하드 게이트 status를 보고한다.
   - 사용자가 100/100 같은 목표를 요구했다면 통과 기준에서 멈추지 않는다. 완벽하지 않은 차원을 focused clean judge로 다시 점검하고, 남은 체크리스트 누락을 수정한 뒤 목표에 도달하거나 차단 이슈가 명확해질 때까지 re-score한다.

7. 한국어 우선 skill-quality 개선에서는 `SKILL.md`만 보지 말고 support files와 templates도 확인한다.
   - 미래 agent가 읽는 `references/`, `templates/`, `scripts/` 문장도 skill 패키지의 일부로 본다.
   - rubric이 한국어 우선 human-facing 문장을 보상하면 영어-only heading과 보고/template label을 제거하거나 번역한다.
   - machine identifier는 보존한다: path, command, JSON/YAML key, enum value, CLI flag, API 이름, 패키지 이름, proper noun.
   - 가능하면 결정론적 heading/문장 spot 검사를 실행한 뒤 정성 판단은 clean judge 재채점으로 확인한다.

## 고효율 개선 패턴

- D3 safety/승인 실패:
  - 저위험 행동과 승인 필요 행동을 분리한다.
  - plan feedback이나 partial agreement는 execution 승인이 아니라고 명시한다.
  - credential, secret, private URL, raw 근거, 전달 대상 경계를 정의한다.
  - 외부 전달 전 대상, account, 본문, thread policy, public/private 범위를 확인하게 한다.

- D4 검증 실패:
  - observable output으로 completion condition을 정의한다.
  - artifact, read-back, API response, message id, test result 같은 실제 근거를 요구한다.
  - scheduler/도구 `ok` 또는 subagent self-report만으로는 충분하지 않다고 명시한다.

- D6 실패 처리 gap:
  - failed command/API/도구, core error, likely cause, impact, 복구 행동을 분리해 보고하게 한다.
  - retry와 alternative-source 기준을 추가한다.
  - `completed`, `partial`, `blocked`, `unverified`, `source 부족` 같은 상태를 라벨링한다.

- D7 구조 gap:
  - 고정 최종 보고 template을 추가한다.
  - 겉보기 모순은 job type 또는 범위 구분으로 해소한다.

- D8 병렬/결정론적 자동화 gap:
  - independent work의 shard 기준을 추가한다.
  - 최종 ranking, synthesis, caps, 전달 gate는 중앙에서 처리한다.
  - one-off script보다 reusable collector/checker design을 사용한다.

## 보고 형식

다음을 보고한다.

- 변경 파일.
- 검증 command/check와 실제 결과.
- old score와 new score.
- 하드 게이트 status.
- 아직 적용되는 cap이 있으면 해당 cap.
- 남은 score-limiting issue.
- commit, push, 외부 전달을 하지 않았다면 그 사실.
