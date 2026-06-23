---
name: rubric-design
description: AI 출력, 연구 요약, 문서, 모델 응답 또는 에이전트 작업을 평가하기 위한 채점 루브릭을 설계, 개선, 보정할 때 사용합니다.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [rubric, evaluation, llm-as-judge, scoring, calibration]
    related_skills: [test-driven-development, writing-plans]
---

# 루브릭 설계

## 개요

이 스킬은 재사용 가능한 작업별 채점 루브릭을 설계할 때 사용합니다. 목표는 단순히 배점을 나누는 것이 아니라, 사람이나 LLM 판정자가 실제로 안정적으로 적용할 수 있는 루브릭을 만드는 것입니다. 좋은 루브릭은 평가 목적이 분명하고, 사용자의 가치 판단이 가중치에 반영되며, 관찰 가능한 체크리스트 기준과 상한/감점 규칙, 안정적인 출력 템플릿을 함께 갖습니다.

좋은 루브릭은 다음 네 가지를 분리합니다.

1. **평가 목적** — 평가자가 무엇을 보상하려 하는지.
2. **가중치** — 사용자가 무엇을 더 중요하게 여기는지.
3. **관찰 가능한 체크리스트 기준** — 실제 출력에서 확인 가능한 구체적 근거.
4. **상한/감점 규칙** — 최종 점수를 제한해야 하는 치명적 실패 조건.

`13–15점 = excellent`처럼 넓은 범위 기준에만 의존하지 마세요. 범위 기준은 해석 보조용으로는 쓸 수 있지만 판정자 간 점수 편차를 크게 만듭니다. 각 항목이 작고 명시적인 점수값을 갖는 체크리스트형 채점을 기본으로 합니다.

## 사용 시점

사용자가 다음을 요청할 때 이 스킬을 사용합니다.

- 새 루브릭 설계.
- 기존 루브릭 개선 또는 보정.
- 모호한 평가 기준을 100점 루브릭으로 전환.
- LLM-as-a-Judge 평가용 루브릭 작성.
- AI 출력, 연구 요약, 문서, 코드 리뷰, 모델 응답, 에이전트 작업 평가.
- 체크리스트 항목, 상한/감점, JSON 출력을 포함한 채점 기준 정의.
- 반복 작업을 위한 재사용 가능한 평가 템플릿 생성.

다음 경우에는 이 스킬을 사용하지 않습니다.

- 사용자가 단순한 감상이나 가벼운 의견만 원하고 점수 구조가 필요 없는 경우.
- 평가 판단이 아니라 순수 사실 조회인 경우.
- 사용자가 이미 완전한 루브릭을 제공했고 직접 채점만 요청한 경우. 이때는 제공된 루브릭을 적용하되, 모호하면 먼저 확인합니다.

## 핵심 원칙

### 1. 가중치는 가치 판단이다

가중치는 이 평가에서 무엇을 더 중요하게 볼지에 대한 사용자의 판단을 반영해야 합니다.

예시:

- 문헌 품질이 가장 중요함 → 포괄성, 근거, 인용 품질, 연구 흐름 비중을 높입니다.
- 실무 시스템 설계가 가장 중요함 → 방법론 비교, 적용 가능성, 보정, 운영 리스크 비중을 높입니다.
- 초심자용 설명이 가장 중요함 → 개념 정확성, 구조, 명확성, 예시 비중을 높입니다.
- 에이전트 작업 결과가 가장 중요함 → 요구사항 충족, 검증 근거, 실패 처리, 사용자 의도 정합성 비중을 높입니다.

기존 루브릭을 수정할 때는 “새 버전이 이전 버전보다 무엇을 더 강하게 보상해야 하는가?”를 먼저 정합니다.

### 2. 체크리스트는 관찰 가능한 근거여야 한다

다음처럼 큰 범주만 두지 마세요.

```text
편향과 신뢰성 논의 — 20점
```

다음처럼 실제 출력에서 확인 가능한 항목으로 나눕니다.

```text
위치/순서 편향 설명 — 3점
장문 선호 편향 설명 — 3점
자기 선호/모델 계열 편향 설명 — 3점
캘리브레이션 문제 설명 — 3점
인간 평가자와의 일치 문제 설명 — 3점
완화 전략 제시 — 5점
```

판정자는 각 점수에 대해 “출력의 어느 부분이 그 근거인가”를 지적할 수 있어야 합니다.

### 3. 넓은 범위 기준에만 의존하지 않는다

`13–15점 = 우수` 같은 기준은 너무 거칩니다. 모든 범주가 2–3점짜리 내부 범위를 가지면 판정자 간 총점이 10점 이상 달라질 수 있습니다.

권장 방식:

```text
범주 총점: 15점
- 기준 A: 2점
- 기준 B: 2점
- 기준 C: 3점
- 기준 D: 3점
- 기준 E: 5점
```

범위 기준은 보조 설명으로만 사용하고, 주된 채점 방식은 checklist item 단위 배점이어야 합니다.

### 4. 치명적 실패에는 상한을 둔다

중요한 차원은 더 높은 배점을 받아야 합니다. 하지만 “빠지면 치명적인 조건”은 단순히 배점만 높일 것이 아니라 total score cap 또는 penalty rule로 다룹니다.

예시:

```text
출력이 과제와 무관하면 총점은 40점으로 상한한다.
핵심 요구사항이 완전히 빠졌으면 총점은 60점으로 상한한다.
조작된 인용이나 출처가 있으면 총점은 60점으로 상한한다.
치명적 개념 오류가 여러 개 있으면 총점은 70점으로 상한한다.
안전, 법률, 개인정보, 보안 제약을 위반하면 총점은 50점으로 상한한다.
```

구분:

- **중요한 것** → 더 많은 점수를 배정합니다.
- **없거나 틀리면 치명적인 것** → 상한/감점 규칙을 둡니다.

### 5. 루브릭은 목적별로 달라야 한다

모든 작업을 하나의 고정 루브릭에 끼워 맞추지 않습니다. 루브릭은 다음을 반영해야 합니다.

- 작업 목표.
- 점수가 지원할 의사결정.
- 사용자의 우선순위.
- 신뢰를 급격히 낮추는 실패 조건.
- 원하는 출력 형식.

범주 템플릿은 출발점일 뿐입니다. 최종 루브릭은 작업 목적에 맞게 조정되어야 합니다.

### 6. 판정 출력은 구조화되어야 한다

LLM Judge가 루브릭을 적용할 예정이면 구조화된 출력을 요구합니다. 최소한 다음을 포함합니다.

- 범주별 점수.
- checklist item별 점수.
- 각 점수의 근거.
- 적용된 상한/감점.
- 빠진 점수.
- 강점.
- 권장 수정사항.
- confidence와 human review 필요 여부.

### 7. 판정 실행은 깨끗한 컨텍스트에서 수행한다

LLM Judge용 루브릭을 만들 때는 판정자가 현재 대화를 이어받지 않도록 설계합니다. 판정자는 self-contained evaluation packet만 받아야 하며, 이전 chat history, agent memory, implementation notes, unstated assumptions를 근거로 사용하면 안 됩니다.

기본 패턴:

1. 평가 대상, 평가할 출력, 루브릭, 허용된 출처/근거 묶음, 상한 규칙, JSON schema만 포함한 evaluation packet을 만듭니다.
2. 가능하면 새 clean subagent/session에서 루브릭을 적용합니다.
3. 판정 프롬프트에 supplied packet만 사용하고, packet에 없는 근거는 missing evidence로 처리하라고 명시합니다.
4. 다차원 또는 중요도가 높은 루브릭은 차원/checklist group 단위로 나누어 병렬 clean subagents에 맡깁니다.
5. parent agent가 shard JSON을 검증하고, missing/duplicate criteria를 확인하며, contradiction을 조정하고, 점수를 합산한 뒤 global cap을 중앙에서 적용합니다.

same-context judging은 중요도가 낮은 빠른 확인이거나 clean subagent를 사용할 수 없을 때만 허용합니다. 이 경우 scorecard에 예외 사유와 컨텍스트 오염 위험을 명시해야 합니다.

## 루브릭 설계 워크플로우

### Step 1: 평가 목적 정의

무엇을 왜 평가하는지 명확히 합니다.

다음 질문에 답합니다.

```text
무엇을 평가하는가?
누가 점수를 사용할 것인가?
이 점수는 어떤 결정을 지원하는가?
탁월한 출력은 어떤 모습인가?
어떤 실패가 신뢰를 급격히 낮추는가?
```

### Step 2: 평가 대상 정의

예시:

- LLM response.
- Literature survey.
- Research briefing.
- Code implementation.
- PR review.
- Planning document.
- Agent task result.
- Model evaluation report.

최종 루브릭에는 평가 대상을 명시합니다.

### Step 3: 평가 차원 선택

5–8개 차원을 선택합니다. 너무 적으면 모호하고, 너무 많으면 적용하기 어렵습니다.

후보 차원:

- Requirement satisfaction.
- Factual/conceptual accuracy.
- Coverage.
- Methodology comparison.
- Analytical depth.
- 근거와 인용 품질.
- Practical applicability.
- Structure and readability.
- Verification evidence.
- 리스크, 한계, 편향 인식.
- User intent alignment.

### Step 4: 가중치 배정

사용자가 다른 척도를 요구하지 않으면 100점 척도를 사용합니다.

권장 분포:

```text
핵심 차원: 2–4개, 총 60–75점
보조 차원: 2–4개, 총 25–40점
```

사용자가 명시적으로 동일 가중치를 원하지 않는 한 모든 차원을 동일 배점으로 만들지 않습니다. 동일 배점은 실제 우선순위를 숨기는 경우가 많습니다.

### Step 5: 가중치를 체크리스트로 변환

각 차원의 점수를 1–5점 정도의 작은 checklist item으로 나눕니다.

Checklist item은 다음 조건을 만족해야 합니다.

- 관찰 가능함.
- 구체적임.
- 별도로 채점 가능함.
- 작업 목적과 연결됨.
- 다른 항목과 중복되지 않음.

나쁜 예:

```text
좋은 분석 — 20점
```

좋은 예:

```text
분석 깊이 — 20점
- 주요 tradeoff를 식별한다 — 5점
- 인과관계 또는 작동 메커니즘을 설명한다 — 5점
- 대안을 나열하지 않고 비교한다 — 5점
- 한계와 불확실성을 밝힌다 — 3점
- 의사결정에 필요한 함의를 제시한다 — 2점
```

### Step 6: 상한/감점 규칙 추가

상한과 감점은 checklist scoring 이후에 적용되도록 명시합니다.

전체 평가에 영향을 주는 실패에는 global cap을 사용합니다.

```text
출력이 off-topic이면 총점은 40점으로 상한한다.
주요 사용자 요청을 무시하면 총점은 60점으로 상한한다.
조작된 출처가 있으면 총점은 60점으로 상한한다.
중요한 safety constraint를 위반하면 총점은 50점으로 상한한다.
```

차원 내부 실패에는 local cap을 사용합니다.

```text
출처가 전혀 없으면 Evidence Quality는 4/10으로 상한한다.
방법론을 나열만 하고 비교하지 않으면 Methodology Comparison은 8/20으로 상한한다.
테스트나 검증을 수행하지 않았으면 Verification Evidence는 5/15로 상한한다.
```

여러 global cap이 적용되면 가장 낮은 cap을 사용합니다.

### Step 7: 판정 실행 모드 정의

Judge Prompt를 작성하기 전에 판정 실행이 현재 대화 컨텍스트에서 분리되는 방식을 정의합니다.

기본 실행 모드:

1. 현재 컨텍스트를 이어가지 말고 clean new subagent/session에서 판정합니다.
2. 평가 대상, 평가할 출력, 루브릭, 허용된 근거/출처 묶음, 상한/감점 규칙, JSON schema만 포함한 self-contained evaluation packet을 전달합니다.
3. 현재 대화 기록, 숨겨진 memory, 이전 구현 메모, 사용자 선호는 evaluation target 또는 evidence packet에 명시적으로 포함된 경우가 아니면 제외합니다.
4. 다차원, 장문, 중요도가 높은 평가는 rubric을 차원/checklist group 단위로 shard하고 parallel clean subagents로 판정합니다.
5. 각 shard judge는 자신에게 배정된 차원/checklist JSON만 반환합니다.
6. parent agent가 중앙에서 집계합니다: JSON parse 검증, 누락/중복 기준 탐지, 모순 조정, 점수 합산, local cap 적용, global cap 최종 적용.

same-context judging을 사용했다면 scorecard에 예외로 표시하고 컨텍스트 오염 위험이 왜 허용 가능한지 설명해야 합니다.

### Step 8: 판정 지시사항 정의

LLM이 루브릭을 적용할 예정이면 다음과 같은 엄격한 지시를 포함합니다.

```text
1. 이 평가는 clean context에서 실행한다. evaluation packet에 포함되지 않은 이전 대화, memory, assumptions는 무시한다.
2. 제공된 루브릭, 평가할 출력, 명시적으로 제공된 근거 묶음만 사용한다.
3. total score를 먼저 정하지 않는다.
4. checklist item을 먼저 채점한다.
5. 암시되었거나 추정되는 내용에는 점수를 주지 않는다.
6. 각 점수의 근거를 인용하거나 요약한다.
7. packet에 특정 기준을 채점할 근거가 없으면 외부 컨텍스트로 추론하지 말고 낮은 점수 또는 0점을 준다.
8. checklist 채점 이후 지역 상한과 감점을 적용한다.
9. local caps 이후 global caps를 적용한다. 여러 global caps가 적용되면 가장 낮은 cap을 사용한다.
10. 길다고 자동으로 좋은 점수를 주지 않는다.
11. 기술 용어를 많이 썼다고 자동으로 좋은 점수를 주지 않는다.
12. dimension shard만 평가하는 경우 최종 총점을 계산하지 말고 해당 shard 결과만 반환한다.
13. 요청된 structured output만 반환한다.
```

### Step 9: 출력 템플릿 정의

최종 루브릭은 다음 두 가지를 모두 포함해야 합니다.

1. 사람이 읽는 루브릭 문서.
2. 판정 결과를 위한 기계 판독 가능 JSON output schema.

아래 템플릿을 기본으로 사용합니다.

### Step 10: 루브릭 보정

반복 사용 전에 예시 출력으로 루브릭을 테스트합니다.

권장 calibration loop:

1. 강한 출력, 보통 출력, 약한 출력, 유창하지만 틀리거나 근거가 약한 출력을 포함해 3–5개 sample output을 채점합니다.
2. 점수 순위가 사람 판단과 맞는지 확인합니다.
3. 너무 모호하거나 너무 쉽게 충족되는 checklist item을 찾습니다.
4. weights와 caps를 조정합니다.
5. sample output을 다시 채점합니다.
6. 결과가 안정되면 rubric version을 고정합니다.

동일 출력에 대해 판정자 간 점수 차이가 5–8점을 넘으면 checklist 기준을 더 관찰 가능하게 좁힙니다.

## 재사용 출력 템플릿: 사람이 읽는 루브릭

최종 루브릭을 사용자에게 제공할 때 이 템플릿을 사용합니다. 사용자의 대화나 요청이 한국어이면 사람-facing prose는 한국어로 작성합니다. JSON key, file path, command, API name, enum, proper noun은 원문을 유지할 수 있습니다.

```markdown
# {task_name} 평가 루브릭

## 1. 평가 목적

{evaluation_purpose}

## 2. 평가 대상

{evaluation_target}

## 3. 총점

100점

## 4. 차원 요약

| 차원 | 배점 | 평가 초점 |
|---|---:|---|
| {dimension_1} | {points} | {focus} |
| {dimension_2} | {points} | {focus} |
| ... | ... | ... |
| **합계** | **100** | |

## 5. 세부 채점 기준

### 5.1 {dimension_1} — {points}점

| 체크리스트 기준 | 배점 | 인정 기준 |
|---|---:|---|
| {criterion_1} | {points} | {observable_evidence} |
| {criterion_2} | {points} | {observable_evidence} |

지역 상한/감점:
- {local_cap_rule}
- {local_penalty_rule}

### 5.2 {dimension_2} — {points}점

| 체크리스트 기준 | 배점 | 인정 기준 |
|---|---:|---|
| {criterion_1} | {points} | {observable_evidence} |
| {criterion_2} | {points} | {observable_evidence} |

## 6. 전역 상한 및 감점 규칙

- {global_cap_rule_1}
- {global_cap_rule_2}

## 7. 점수 해석

| 총점 | 해석 |
|---:|---|
| 90–100 | 탁월함. 거의 수정 없이 사용 가능 |
| 80–89 | 좋음. 일부 보완 후 사용 가능 |
| 70–79 | 보통. 핵심 요구는 충족했지만 주요 공백 존재 |
| 60–69 | 약함. 상당한 수정 필요 |
| 0–59 | 부적합. 주요 요구 누락 또는 신뢰 불가 |

## 8. 채점 절차

1. evaluated output이 평가 범위에 들어오는지 확인한다.
2. 적용 가능한 global cap이 있는지 확인한다.
3. checklist item을 독립적으로 채점한다.
4. dimension score를 합산한다.
5. local caps and penalties를 적용한다.
6. global caps를 적용한다.
7. 근거, 빠진 점수, 권장 수정사항을 보고한다.

## 9. 판정자 프롬프트

```text
{judge_prompt}
```

## 10. JSON 출력 스키마

```json
{json_schema}
```
```

## 깨끗한 병렬 서브에이전트 판정 워크플로우

루브릭에 여러 dimension이 있거나, evaluated output이 길거나, high-stakes 평가이거나, 사용자가 parallel inspection을 명시적으로 요청한 경우 이 워크플로우를 사용합니다.

1. Parent agent가 루브릭, 평가할 출력, 허용된 근거, score schema, 상한 규칙을 포함한 bounded evaluation packet을 준비합니다.
2. Parent가 루브릭을 차원 또는 checklist shard로 나누고, 각 shard의 점수 책임 범위가 겹치지 않게 합니다.
3. Parent가 clean subagents를 병렬로 실행합니다. 각 subagent는 packet과 자신에게 배정된 shard만 받습니다.
4. 각 shard judge는 자신에게 배정된 기준에 대한 strict JSON만 반환합니다. 근거와 local cap/penalty suggestion을 포함합니다.
5. Parent가 모든 shard result에 대해 JSON parse 가능성, 점수 범위, 누락 기준, 중복 기준, 근거 기반성을 검증합니다.
6. Parent가 shard 간 contradiction을 최종 점수 전에 조정합니다.
7. Parent가 local caps를 적용한 뒤, 모든 shard score를 병합하고 global caps를 중앙에서 적용합니다.
8. Parent가 최종 사람이 읽는 scorecard와 기계 판독 가능 JSON result를 생성합니다.

단일 shard로 의도한 평가가 아니라면 shard judge가 final total을 독립적으로 결정하게 하지 않습니다. Shard judge는 possible global cap을 flag할 수 있지만, final global cap은 parent agent가 적용합니다.

## 재사용 출력 템플릿: LLM 판정 JSON

Judge 결과의 기본 machine-readable format입니다. JSON key와 enum 값은 안정성을 위해 영어를 유지합니다.

```json
{
  "evaluation_target": "string",
  "judging_context": "clean_subagent | parallel_clean_subagents | same_context_exception",
  "context_contamination_notes": "string",
  "total_score": 0,
  "max_score": 100,
  "grade": "string",
  "global_caps_applied": [
    {
      "rule": "string",
      "reason": "string",
      "score_cap": 0
    }
  ],
  "dimension_scores": [
    {
      "dimension": "string",
      "score": 0,
      "max_score": 0,
      "checklist": [
        {
          "criterion": "string",
          "score": 0,
          "max_score": 0,
          "evidence": "string",
          "comment": "string"
        }
      ],
      "caps_or_penalties": [
        {
          "rule": "string",
          "effect": "string",
          "reason": "string"
        }
      ],
      "summary": "string",
      "improvement": "string"
    }
  ],
  "critical_missing_points": [
    "string"
  ],
  "major_errors": [
    "string"
  ],
  "strengths": [
    "string"
  ],
  "recommended_revisions": [
    "string"
  ],
  "confidence": "low | medium | high",
  "needs_human_review": true
}
```

## 재사용 출력 템플릿: 판정자 프롬프트

LLM에게 루브릭 적용을 맡길 때 이 prompt를 사용합니다.

```text
당신은 제공된 루브릭을 적용하는 엄격한 판정자입니다.

평가 원칙:
1. 이 평가는 깨끗한 독립 컨텍스트에서 실행합니다. evaluation packet에 포함되지 않은 이전 대화, memory, assumptions는 무시합니다.
2. 제공된 rubric, evaluated output, 명시적으로 제공된 evidence bundle만 사용합니다.
3. 명시되지 않은 내용은 추론하지 말고, unstated assumptions에는 점수를 주지 않습니다.
4. total_score를 먼저 정하지 않습니다.
5. total_score를 계산하기 전에 각 checklist item을 먼저 채점합니다.
6. 모든 checklist score에 대해 근거를 제시합니다.
7. packet에 특정 기준을 채점할 근거가 없으면 외부 context로 추론하지 말고 낮은 점수 또는 0점을 줍니다.
8. checklist 채점 이후 지역 상한과 감점을 적용합니다.
9. local caps 이후 global caps를 적용합니다. 여러 global caps가 적용되면 가장 낮은 cap을 사용합니다.
10. 길다는 이유만으로 보상하지 않습니다.
11. 기술 용어를 많이 썼다는 이유만으로 보상하지 않습니다.
12. claim이 근거 없이 제시되면 관련 evidence criterion 점수를 낮춥니다.
13. parallel judging workflow에서 하나의 차원 shard만 평가하는 경우, 최종 총점을 계산하지 말고 해당 shard result만 반환합니다.
14. 지정된 JSON format만 반환합니다.

평가 대상:
{evaluation_target}

루브릭:
{rubric}

JSON 출력 스키마:
{json_schema}
```

## 공통 차원 세트

아래는 출발점일 뿐입니다. 작업 목적에 맞게 조정합니다.

참조 노트:

- `references/llm-wiki-quality-rubric-workflow.md` — ad-hoc llm-wiki health check를 D1–D4 hard gates, deterministic checker boundaries, raw sha256 normalization, stable JSON scorecard를 갖춘 95점 기준 루브릭으로 전환하는 패턴.
- `references/ai-quality-feedback-loops.md` — evals, 실패 로그, 루브릭, golden sets, pairwise comparison, Reflexion, DSPy, RAGAS, user feedback를 활용한 AI/LLM 품질 피드백 루프 연구 노트와 템플릿.
- `references/real-response-calibration-pattern.md` — 실제 isolated/new-session output으로 루브릭을 보정하는 workflow. 산출물 배치, high-score gates, marketing-rubric 보정 함정 포함.
- `references/strictness-loop-calibration.md` — 목표 평균/버전 상한을 맞추기 위해 루브릭을 반복적으로 엄격화하는 패턴. 병렬 subagent diagnosis, gates/caps, stop-condition logging 포함.
- `references/holdout-validation-for-strict-rubrics.md` — 엄격화된 루브릭이 overfit되었는지 확인하는 패턴. fresh questions, blind/new-session answers, parallel scoring, central aggregation 포함.
- `references/persona-system-prompt-evaluation-scorecard.md` — user-persona system prompt 평가 패턴. 재사용 루브릭과 task-specific scorecard 분리, scenario responses, independent reviewers, parseable JSON score block, read-back verification 포함.
- `references/clean-parallel-judge-execution.md` — clean new subagents에서 rubric judge를 실행하고, multi-dimension scoring을 병렬 shard로 나누며, 중앙 집계하고, 한국어 우선 human-facing 루브릭 prose 및 `references/` supporting docs를 강제하는 workflow.
- `references/skill-quality-rubric-planning-pattern.md` — 재사용 agent skills/workflow playbooks 평가 루브릭 설계 패턴. trigger/procedure/boundary/verification, Korean-first, generic-agent hard rules, clean/parallel-subagent judging, deterministic-vs-nondeterministic automation separation, reusable-script requirements, caps, artifact split, calibration scaffold 포함.
- `references/korean-first-rubric-language-check.md` — 한국어 우선 평가를 한글 포함 여부가 아니라 사람-facing prose의 기본 언어, 번역 가능한 영어 label 반복, 영어 prose 비율로 검증하는 보정 패턴.
- `references/skill-rubric-remediation-loop.md` — 기존 skill을 루브릭 목표 점수까지 끌어올릴 때의 remediation workflow. hard-gate blocker 우선, class-level SKILL.md vs references/ 배치, JSON/schema/checker 보강, clean shard 재채점, final verification/reporting 패턴 포함.

### 문헌 조사 / 연구 리뷰

권장 차원:

- Research coverage.
- Conceptual accuracy.
- Methodology comparison.
- 한계, 편향, 신뢰성 논의.
- Research flow and synthesis.
- 근거와 인용 품질.
- Practical implications.
- Structure and readability.

### LLM-as-a-Judge / 평가 시스템 설계

권장 차원:

- 평가 방법론 비교.
- 편향, 신뢰성, 보정 인식.
- 실무 평가 파이프라인 설계.
- Conceptual accuracy.
- 관련 연구 또는 벤치마크 포괄성.
- Evidence quality.
- Output structure.

### Persona/System-Prompt 평가 루브릭

평가 대상이 persona-derived system prompt이면 정적 prompt coverage와 scenario response scoring을 함께 포함합니다.

- 정적 차원은 core judgment model, approval/execution boundaries, verification/completion standards, communication style, security/privacy, code/design preferences, large-analysis/tooling reproducibility, conflict/excluded-domain handling을 다룹니다.
- Scenario scoring은 validation scenarios에 prompt를 적용한 응답을 만들고 각 response를 `0 / 0.5 / 1`로 채점한 뒤 weighted aggregation합니다.
- 위험한 실패에는 cap을 둡니다: legal/financial/medical judgment 모방, 승인 없는 destructive/production/credential/external action 권장, stale memory를 live evidence보다 우선, unverified completion 허용, secret 유출.
- 루브릭 외에 scorecard artifact를 요구합니다: 차원 표, scenario group 표, global-cap check, final formula, strengths, weaknesses, recommended prompt patches, machine-readable JSON result.
- 사용자가 “quality evaluation”을 요청했다면 scenario/template에서 멈추지 말고, 실제 prompt-applied responses를 생성하고, independent judge scoring을 수행하고, static coverage review와 final score 계산까지 완료합니다.
- Hermes default-profile persona 작업은 active identity source인 `~/.hermes/SOUL.md`를 직접 검증합니다. canonical prompt source/read-back parity(hash/size)를 확인하고 `config.yaml`만으로 persistent persona identity를 판단하지 않습니다.
- 실제 점수 확실성이 필요하면 fresh sessions에서 scenario evaluation을 실행합니다. 예: `hermes chat -Q -q` 스타일 호출. `.md`와 `.json` 결과 artifact를 모두 작성합니다.

지원 플레이북: `references/hermes-persona-live-evaluation-playbook.md`

### 에이전트 작업 결과 평가

권장 차원:

- Requirement satisfaction.
- Evidence of execution and verification.
- Correctness and completeness.
- Handling of failures and uncertainty.
- User intent alignment.
- Safety and reversibility.
- Communication clarity.

### 코드 구현 평가

권장 차원:

- Requirement satisfaction.
- Correctness.
- Test coverage and verification.
- Maintainability.
- Integration with existing architecture.
- Error handling and edge cases.
- Regression risk.

### PR 리뷰 품질 평가

권장 차원:

- Bug/risk detection.
- Technical correctness.
- Actionability of comments.
- Evidence from diff or tests.
- Prioritization by severity.
- Avoidance of noise or nitpicks.
- Respectful and concise communication.

## 공통 상한 규칙 라이브러리

루브릭 설계 시 아래 규칙을 사용하거나 상황에 맞게 조정합니다.

### 전역 상한

- 출력이 과제와 무관하면 total score는 40점으로 상한합니다.
- 주요 사용자 요청을 무시하면 total score는 60점으로 상한합니다.
- 핵심 deliverable이 빠졌으면 total score는 65점으로 상한합니다.
- 조작된 citation, source, tool result가 있으면 total score는 60점으로 상한합니다.
- 치명적 factual/conceptual error가 여러 개 있으면 total score는 70점으로 상한합니다.
- 안전, 법률, privacy, security constraint를 위반하면 total score는 50점으로 상한합니다.
- 내용이 너무 부실해서 평가할 수 없으면 total score는 50점으로 상한합니다.
- 요청된 reusable rubric document의 사람-facing prose가 한국어 우선으로 작성되지 않았으면 total score는 80점으로 상한합니다.
- Korean-first rubric requirement가 명시되었는데 사람-facing prose 대부분이 영어이면 total score는 70점으로 상한합니다.

Machine identifiers such as JSON keys, file paths, commands, API names, enum values, schema fields, and proper nouns may remain in their original language and should not trigger Korean-first language caps.

### 지역 상한

- 출처가 전혀 없으면 Evidence/Citation Quality는 해당 차원의 40%로 상한합니다.
- 방법론을 나열만 하고 비교하지 않으면 Methodology Comparison은 해당 차원의 50%로 상한합니다.
- 테스트 또는 검증이 없으면 Verification Evidence는 해당 차원의 50%로 상한합니다.
- 요청된 output format을 따르지 않으면 Structure/Format은 해당 차원의 50%로 상한합니다.
- 응답이 지나치게 generic하면 Analysis Depth는 해당 차원의 60%로 상한합니다.

### 감점 규칙

- Unsupported claims는 evidence 관련 checklist score를 낮춥니다.
- Ambiguous wording은 structure 또는 clarity score를 낮춥니다.
- Missing requested format은 structure/format score를 낮춥니다.
- Redundant content는 concision/readability score를 낮춥니다.
- Overconfident claims without uncertainty handling은 reliability score를 낮춥니다.

## 예시: LLM-as-a-Judge 문헌 조사 루브릭

아래 예시는 checklist 기반 접근 방식을 보여줍니다.

### 차원 요약

| 차원 | 배점 |
|---|---:|
| Research coverage and scope | 15 |
| Conceptual accuracy | 15 |
| Evaluation methodology comparison | 15 |
| Limitations, bias, and reliability | 15 |
| Research flow and synthesis | 10 |
| Practical applicability | 10 |
| Evidence and citation quality | 10 |
| Structure and readability | 10 |
| **합계** | **100** |

### 한계, 편향, 신뢰성 — 15점

| 체크리스트 기준 | 배점 | 인정 기준 |
|---|---:|---|
| Position/order bias explained | 2 | 답변 순서가 judge preference에 영향을 줄 수 있음을 설명한다 |
| Verbosity bias explained | 2 | 긴 답변이 부당하게 선호될 수 있는 이유를 설명한다 |
| Self-preference/model-family bias explained | 2 | judge model과 유사한 output을 선호하는 문제를 논의한다 |
| Calibration problem explained | 2 | score scale reliability 또는 consistency 문제를 논의한다 |
| Human agreement problem explained | 2 | human evaluators와의 agreement/disagreement를 논의한다 |
| Reproducibility problem explained | 2 | prompt, model, run, benchmark에 따른 variance를 논의한다 |
| Bias mitigation methods proposed | 2 | shuffling, pairwise evaluation, multi-judge, calibration set 같은 구체적 완화책을 제시한다 |
| Impact on evaluation outcomes explained | 1 | 이런 bias가 최종 decision에 왜 중요한지 설명한다 |

Local caps:

- 답변이 “LLM judges have bias”라고만 말하고 구체적 bias를 명명하거나 설명하지 않으면 이 차원은 6/15로 상한합니다.
- mitigation method가 없으면 이 차원은 12/15로 상한합니다.

## 보정 지침

루브릭 초안을 작성한 뒤 sample output으로 테스트합니다.

최소한 다음을 포함합니다.

1. 강한 출력.
2. 보통 출력.
3. 약한 출력.
4. 유창하지만 틀리거나 근거가 부족한 tricky output.

확인할 것:

- 강한 출력이 올바른 이유로 높은 점수를 받는가?
- 유창하지만 틀린 출력이 충분히 감점되는가?
- 누락된 요구사항이 cap을 trigger하는가?
- 두 판정자의 점수 차이가 5–8점을 넘는가?
- 너무 주관적인 checklist item이 있는가?

편차가 크면 모호한 기준을 observable evidence 기준으로 바꿉니다. 약한 예시가 너무 높게 나오면 먼저 cap을 강화합니다. 치명적 누락에는 weights보다 caps가 더 적합합니다.

### 재사용 루브릭과 보정 결과 분리

반복 사용을 위한 루브릭은 안정적인 기준과 calibration artifacts를 분리합니다.

- **Rubric document:** evaluation purpose, target, definition of excellence, weighted checklist criteria, local/global caps, scoring procedure, judge prompt, JSON schema, score interpretation.
- **Calibration/results document:** sample prompts, sample answers, expected scores, score tables, cap applications, rubric tuning notes.

사용자가 명시적으로 all-in-one artifact를 원하지 않는 한 sample scores를 canonical rubric에 섞지 않습니다. Sample scores는 버전이 바뀌면 drift되므로, 분리해야 future judges가 오래된 calibration examples를 기준의 일부로 오해하지 않습니다.

저장 위치가 정해지지 않았으면 repository나 skill-managed directory 밖의 neutral artifact directory에 먼저 staging하고 path를 보고합니다. 사용자가 destination을 명시적으로 선택한 뒤 repo/wiki/skill directory에 작성합니다.

약한 답변 유형 예시:

- 사용자 context 없는 generic advice.
- 적용 없이 framework name만 나열.
- 진단이나 전략 없이 tactic/channel list만 제시.
- 유창하지만 근거 없는 strategy.
- 특정 subdomain에는 강하지만 integrated judgment가 부족한 답변.
- Competent practitioner answer.
- Strong but incomplete expert answer.
- True expert answer with diagnosis, tradeoffs, measurement, and risks.

## 흔한 함정

1. **Category weights만 정함.** 배점만으로는 부족합니다. checklist criteria가 필요합니다.
2. **넓은 range anchor를 주된 채점 방식으로 사용함.** 판정자 간 편차가 커집니다.
3. **모든 category를 동일 배점으로 둠.** 실제 priority를 숨깁니다.
4. **중요성과 치명성을 혼동함.** 중요한 항목은 points, 치명적 실패는 caps/penalties로 다룹니다.
5. **관찰 불가능한 기준 사용.** “좋음”, “명확함”, “충분함” 대신 evidence-based criteria를 씁니다.
6. **Judge가 total score를 먼저 정하게 함.** checklist item을 먼저 채점하게 합니다.
7. **근거를 요구하지 않음.** 모든 점수에는 evaluated output에 근거한 이유가 있어야 합니다.
8. **Calibration을 생략함.** 반복 사용 전 예시로 테스트합니다.
9. **하나의 예시에 overfit함.** 루브릭은 유사 작업 전반에 일반화되어야 합니다.
10. **길이나 jargon을 보상함.** 길이와 기술 용어는 그 자체로 품질이 아닙니다.

## Verification Checklist

루브릭을 최종화하기 전에 확인합니다.

- [ ] evaluation purpose가 명시되어 있다.
- [ ] evaluation target이 명시되어 있다.
- [ ] 사용자가 다른 척도를 요구하지 않았다면 total score가 100점으로 정규화되어 있다.
- [ ] highest-weighted dimensions가 사용자의 우선순위와 맞다.
- [ ] 각 dimension이 checklist criteria로 나뉘어 있다.
- [ ] checklist criteria가 observable하고 separately scorable하다.
- [ ] 넓은 range anchor에만 의존하지 않는다.
- [ ] critical failure conditions에 cap 또는 penalty rule이 있다.
- [ ] scoring procedure가 total score보다 checklist item scoring을 먼저 요구한다.
- [ ] judge prompt가 각 score의 evidence를 요구한다.
- [ ] LLM judging이 예상되면 JSON output schema가 포함되어 있다.
- [ ] final scorecard가 fresh 또는 explicitly bounded scenario responses에서 생성된다. hand-written placeholder가 아니다.
- [ ] judge execution mode가 정의되어 있다: clean subagent, parallel clean subagents, 또는 explicitly labeled same-context exception.
- [ ] evaluation packet boundaries가 정의되어 있다. included inputs와 excluded context가 명시되어 있다.
- [ ] multi-dimension 또는 high-stakes rubric은 parallel judging과 parent aggregation을 지정한다.
- [ ] parent aggregation이 shard JSON을 검증하고 global caps를 중앙 적용한다.
- [ ] 요청이나 domain이 Korean-first output을 요구하면 human-facing rubric prose, `references/` supporting docs, canonical rubric files, judge prompt files, scorecard/report prose가 한국어 우선이다.
- [ ] Korean-first는 한글 문자가 존재한다는 뜻이 아니라, 사람이 읽는 heading, label, 절차 문장, 판단 기준, 보고 template label의 기본 언어가 한국어라는 뜻으로 판정한다.
- [ ] Korean-first 검증은 주요 headings와 사람-facing 문장의 영어 비중을 실제로 측정하거나 spot-check한다. JSON key, enum, file path, command, API name, schema field, proper noun은 번역 예외로 분류한다.
- [ ] 번역 가능한 영어 prose가 heading/label/procedure에 반복되면 감점 또는 cap을 둔다. 예: `workflow`, `output`, `validation`, `source`, `briefing`, `delivery`, `status`, `pattern`, `item`, `parent`, `thread`.
- [ ] 엄격한 skill/rubric 평가에서는 code fence, inline code, URL, path, JSON/YAML key, enum, proper noun allowlist를 제외한 영어 prose token 비율, 영어-only heading 수, 영어 label 반복 수를 deterministic checker 결과로 scorecard에 포함한다.
- [ ] Persona/system-prompt evaluation에서 Hermes default profile을 평가할 때 active identity source인 `~/.hermes/SOUL.md`를 canonical prompt와 read-back check(hash/size)한다.
- [ ] canonical persona source가 one-off score artifacts와 분리되어 있다. 특정 run result로 rubric을 덮어쓰지 않는다.
- [ ] 반복 사용을 위한 calibration loop가 정의되어 있다.

## origin/main 병합 보강

루브릭 설계 시 다음 운영 원칙을 유지한다.

- Judge run은 가능한 clean context에서 수행하고, 같은 컨텍스트 예외는 명시적으로 표시한다.
- 큰 평가 대상은 `parallel_clean_subagents`로 shard하고 parent가 중앙에서 schema validation, aggregation, cap 적용, contradiction reconciliation을 수행한다.
- Calibration artifact와 canonical rubric은 분리한다. Calibration sample family는 gold standard가 아니라 검증 분포다.
- JSON key, enum, path, command, API name 같은 machine identifier는 번역하지 않는다.
