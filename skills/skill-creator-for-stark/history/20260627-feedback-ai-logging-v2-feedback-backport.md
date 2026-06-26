# 2026-06-27 feedback-ai-logging-v2 피드백 환류

## 배경

`feedback-ai-logging-v2/feedback/`에 기록된 불만사항 7건을 확인하고, 그중 6건은 개별 스킬 문서만의 문제가 아니라 `skill-creator-for-stark`의 scaffold와 validator에서 유발된 것으로 판단했다.

확인한 피드백 원문:

- `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback/235903-unknown-session-too-many-input-variables.md`
  - 제목: feedback-ai-logging-v2 입력 변수가 과다함
  - 핵심 불만: 스킬 문서가 실제 결과에 크게 영향을 주는 입력만 요구하지 않고, 기본값이 있거나 자주 바뀌지 않는 값까지 입력 변수로 과하게 노출한다. 실행자가 매번 무엇을 채워야 하는지 불필요하게 커진다.
- `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback/235904-unknown-session-output-variables-template-duplication.md`
  - 제목: feedback-ai-logging-v2 출력 변수가 템플릿 내용을 중복함
  - 핵심 불만: 출력 변수가 최종 output template에 적을 내용을 거의 그대로 변수화한 것처럼 보인다. 결과 확인에 필요한 핵심 정보와 보고 문장 구성 요소가 분리되지 않아 불필요하게 장황하다.
- `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback/235905-unknown-session-env-variables-unclear-necessity.md`
  - 제목: feedback-ai-logging-v2 ENV 변수 필요성이 불명확함
  - 핵심 불만: `ENV_` 항목이 왜 필요한지 불명확하고, 사용자 입력 변수처럼 보여 혼란을 만든다. 파일시스템 권한, time command, hash command, validator command 같은 실행 전제가 입력 계약과 같은 수준으로 노출되어 있다.
- `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback/000508-unknown-session-hard-gates-not-skill-specific.md`
  - 제목: feedback-ai-logging-v2 Hard Gates가 스킬 고유 기준이 아님
  - 핵심 불만: Hard Gates 섹션이 `feedback-ai-logging-v2`의 raw feedback 기록 품질을 직접 보장하는 기준보다, 범용 skill creator가 SKILL.md를 작성할 때 지켜야 하는 메타 규칙을 포함하고 있다. `Metadata gate`, `Body size gate`처럼 스킬 패키지 형식 검증에 가까운 항목이 섞여 있어 이 스킬 실행자가 무엇을 반드시 지켜야 하는지 흐린다.
- `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback/000509-unknown-session-duplicate-trigger-sections.md`
  - 제목: feedback-ai-logging-v2 사용 시점과 Trigger Examples가 중복됨
  - 핵심 불만: `사용 시점`, `사용하지 말아야 할 때`, `Trigger Examples`가 사실상 같은 trigger 판단을 반복한다. 같은 의미의 섹션이 분리되어 있어 문서가 길어지고, 스킬 사용자가 어느 섹션을 기준으로 trigger 여부를 판단해야 하는지 불필요하게 헷갈린다.
- `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback/000632-unknown-session-log-template-in-references-not-templates.md`
  - 제목: feedback-ai-logging-v2 로그 템플릿이 templates/가 아니라 references/에 있음
  - 핵심 불만: 스킬이 생성하려는 직접 산출물이 로그 파일인데, 그 로그 파일의 템플릿 역할을 하는 문서가 `templates/`에 있지 않고 `references/`에 들어가 있다. 이 때문에 산출물 템플릿과 참고 설명 문서의 경계가 흐려지고, 실행자가 실제로 복사/작성 기준으로 삼아야 할 파일을 찾기 어렵다.
- `/Users/stark/project/jarvis/ai_tool/skills/feedback-ai-logging-v2/feedback/001132-unknown-session-ignored-explicit-output-directory.md`
  - 제목: feedback-ai-logging-v2가 명시 output directory 아래에 임의 하위 경로를 추가함
  - 핵심 불만: 사용자가 저장 디렉터리를 명시했는데도 스킬/agent가 자체 기본 경로 규칙을 덧붙여 `raw/feedback` 하위 디렉터리를 만들었다. 이는 사용자의 명시 경로를 output root로 재해석하고 내부 subdir 규칙을 추가한 것으로, 요청한 저장 위치와 실제 저장 위치가 달라진다.

이 중 6건은 직접적으로 `skill-creator-for-stark`의 scaffold/template/validator 문제로 환류했다. `001132-unknown-session-ignored-explicit-output-directory.md`는 `feedback-ai-logging-v2` 자체의 output routing 문제로 분류하되, creator 관점에서는 “사용자가 명시한 output/approval scope를 일반 기본값으로 덮지 말아야 한다”는 보조 점검 항목으로 참고했다.

## 반영한 원칙

- `INPUT_`는 사용자가 실제 결정하고 결과를 바꾸는 값만 남긴다.
- `OUTPUT_`는 완료·검증·후속 승인 판단에 필요한 값만 남긴다.
- `ENV_`는 사용자 입력이 아니라 실행 전제로 설명하고, 필요할 때만 표로 둔다.
- 생성되는 스킬의 `Hard Gates`에는 domain-specific gate만 둔다.
- trigger 판단은 하나의 canonical section에 통합한다.
- 직접 생성할 파일 skeleton은 `templates/`, 판단 기준은 `references/`에 둔다.

## 변경 요약

- `SKILL.md`: contract triage, domain-specific hard gate, trigger de-duplication, template placement gate를 workflow와 hard gate에 추가했다.
- `references/skill-authoring-rules.md`: 최소 변수화, trigger 중복 방지, hard gate 작성 규칙, template/reference 분리 기준을 보강했다.
- `templates/SKILL.template.md`: 모든 스킬에 범용 변수와 package gate를 주입하던 template을 slim template으로 교체했다.
- `templates/skill-output-template.md`: `INPUT_`/`OUTPUT_` 전체 table 반복 대신 상태, 변경 파일, 검증, 품질, 미확인 중심 보고로 축소했다.
- `scripts/validate-skill-package.py`: contract row count warning, trigger duplication, package hard gate leakage, template placement, feedback guidance token 검사를 추가했다.
- `references/skill-feedback-logging-rules.md`: feedback log skeleton은 `templates/`, 형식 설명은 `references/`에 두는 기준을 추가했다.

## 남은 결정

- `ENV_` section을 장기적으로 완전 optional로 바꿀지는 별도 migration이 필요하다.
- 새 validator rule은 기존 skill 호환성을 위해 일부를 warning으로 시작했다.
- `feedback-ai-logging-v2` 자체의 `SKILL.md`와 template 위치 수정은 후속 작업으로 분리할 수 있다.
