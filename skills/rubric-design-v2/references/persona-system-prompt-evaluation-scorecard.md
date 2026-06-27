# Persona/System Prompt 평가 점수카드 패턴

## 목적

persona 또는 system prompt가 사용자의 운영 선호, 승인 경계, 검증 규율, 언어 스타일, 보안 경계를 실제 응답에 반영하는지 평가한다.

## 차원 예시

- 핵심 판단 모델과 우선순위 반영.
- 승인과 실행 경계.
- 완료 주장 전 검증 규율.
- 한국어 우선 응답 스타일.
- 보안과 개인정보 경계.
- 큰 context와 tool 사용 재현성.
- 충돌 처리와 제외 영역 처리.

## 절차

1. prompt 원문을 read-back한다.
2. 정적 포함 checklist를 채점한다.
3. 시나리오 질문을 만들고 새 응답을 생성한다.
4. 독립 judge가 시나리오 응답을 채점한다.
5. 정적 점수와 시나리오 점수를 가중 집계한다.
6. 전역 상한 후보를 확인한다.
7. 권장 prompt patch를 path와 근거 기준으로 보고한다.

## JSON 점수카드 필드

- `prompt_source`
- `scenario_id`
- `static_scores`
- `scenario_scores`
- `global_caps_applied`
- `final_score`
- `recommended_patches`

## 주의사항

- 시나리오 응답은 placeholder가 아니라 실제 생성 output이어야 한다.
- hidden memory나 이전 대화는 평가 패킷에 포함된 경우에만 근거로 쓴다.
