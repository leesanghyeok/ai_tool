---
name: rubric-creating-expert
description: 세계 최고 수준 전문가 루브릭을 실제 신규 답변으로 캘리브레이션하는 워크플로우. rubric-design으로 만든 기본 루브릭을 질문 생성, 병렬 답변+채점, 평균 검증, 반복 개선 루프로 엄격화한다.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [rubric, evaluation, calibration, expert, subagents, workflow]
    related_skills: [rubric-design]
---

# Rubric Creating Expert

## 개요

이 스킬은 특정 분야에서 “세계 최고 수준 전문가 답변”을 평가하기 위한 루브릭을 만들고, 실제 신규 세션형 답변으로 반복 검증·개선하는 워크플로우를 정의한다.

중요한 역할 분리:

- 기본 루브릭 설계, 배점, 체크리스트, cap/gate 작성 원칙은 반드시 `rubric-design` 스킬을 사용한다.
- 이 스킬은 `rubric-design`을 대체하지 않는다.
- 이 스킬은 생성된 루브릭이 실제 신규 답변을 얼마나 엄격하게 평가하는지 검증하고, 목표 평균점수에 도달할 때까지 질문 생성·답변 생성·채점·개선 루프를 운영한다.

핵심 원칙:

> 루브릭은 문서상 좋아 보이는 것만으로는 검증된 것이 아니다. 반드시 새로운 질문, 새로운 답변, 실제 채점을 통해 캘리브레이션해야 한다.

## 언제 사용하나

다음 요청에 사용한다.

- “세계 최고 수준 전문가 기준 루브릭을 만들어줘”
- “일반 답변이 쉽게 고득점 받지 못하게 검증해줘”
- “신규 세션 답변 평균이 40점 미만이 되도록 캘리브레이션해줘”
- “목표 평균점수 50점/60점 기준으로 루브릭을 조정해줘”
- “서브에이전트로 병렬 검증하면서 루브릭을 개선해줘”
- “루브릭이 기존 답변에 과적합되지 않게 반복 검증해줘”

## 언제 사용하지 않나

다음에는 이 스킬만 단독으로 사용하지 않는다.

- 단순히 루브릭 초안만 만들 때: `rubric-design`을 사용한다.
- 사용자가 이미 완성된 루브릭으로 한 답변만 채점해달라고 할 때: 제공된 루브릭을 직접 적용한다.
- 평가 도메인이 없는 일반 의견 요청일 때.

## 고정 언어

이 스킬의 실행 언어는 항상 한국어다.

- 질문, 답변, 채점, 요약, 보고서는 한국어로 작성한다.
- 단, 파일명, slug, YAML key, JSON schema key, 코드/명령어/식별자는 필요하면 영어를 유지한다.
- 별도의 언어 변수는 두지 않는다.

## 변수

이 스킬에서 다루는 변수는 다음뿐이다.

| 변수 | 기본값 | 설명 |
|---|---:|---|
| `domain` | 사용자 요청에서 추론 | 평가 분야 |
| `target_average` | 40 | 종료 기준 평균점수 |
| `question_count` | 10 | 루프마다 생성할 질문 수 N |
| `max_version` | 10 | 최대 루브릭 버전 |
| `artifact_dir` | 사용자 지정 또는 비-repo artifact 위치 | 산출물 저장 위치 |

### 도메인 처리 규칙

도메인이 명확하면 그대로 사용한다.

예:
- “마케팅 전문가 루브릭” → `domain = marketing`
- “투자 전문가 답변 루브릭” → `domain = investment`

도메인이 애매하면 진행 전에 사용자에게 확인한다.

확인 질문 예:

```text
평가 도메인이 명확하지 않습니다. 어떤 분야의 세계 최고 수준 전문가 루브릭으로 진행할까요?
예: 마케팅, 투자, 제품 전략, 소프트웨어 설계, 리서치 등
```

## 루브릭 파일과 워크플로우 설정 분리

반드시 지킬 원칙:

> 루브릭 파일은 평가 기준 문서다. 워크플로우 설정은 실행 관리 문서다. 두 관심사를 섞지 않는다.

### 루브릭 파일에 넣을 것

루브릭 파일 경로 예:

```text
rubrics/{domain}-expert-rubric-v{version}.md
```

포함할 내용:

- 평가 목적
- 평가 대상
- 세계 최고 수준 전문가 기준
- 총점 구조
- 세부 채점 기준
- local cap
- global cap
- high-score gate
- Judge 지침
- JSON 출력 스키마
- 점수 해석

포함하지 않을 내용:

- 목표 평균점수
- 질문 개수 N
- 최대 버전
- 현재 루프 번호
- artifact 저장 경로
- 특정 샘플 점수
- 이번 실행의 종료조건
- 질문 생성 프롬프트
- 서브에이전트 실행 로그

### 워크플로우 설정 파일에 넣을 것

설정 파일 경로:

```text
run-config.md
```

포함할 내용:

- `domain`
- `target_average`
- `question_count`
- `max_version`
- `artifact_dir`
- `current_version`
- stop condition
- 실행 방식
- 서브에이전트 병렬 처리 방식
- 파일 경로 규칙

예시:

```markdown
# Rubric Calibration Run Config

- domain: marketing
- target_average: 40
- question_count: 10
- max_version: 10
- current_version: 1
- artifact_dir: `/Users/stark/Documents/ai-artifacts/marketing-rubric-calibration/`

stop_condition:
- average_score < target_average
- or current_version >= max_version
```

## 권장 산출물 구조

```text
{artifact_root}/{domain}-rubric-calibration/
  README.md
  run-config.md

  rubrics/
    {domain}-expert-rubric-v1.md
    {domain}-expert-rubric-v2.md
    {domain}-expert-rubric-v3.md

  iterations/
    v1/
      questions.md
      responses/
        q01.md
        q02.md
      scores/
        q01-score.md
        q02-score.md
      summary.md
      gap-analysis.md

    v2/
      questions.md
      responses/
      scores/
      summary.md
      gap-analysis.md

  final/
    final-rubric.md
    final-summary.md
```

구조의 의도:

- 루브릭은 `rubrics/`에 둔다.
- 워크플로우 실행 설정은 `run-config.md`에 둔다.
- 질문/답변/점수는 `iterations/vX/`에 둔다.
- 최종본은 `final/`에 둔다.
- 루브릭 문서에 workflow setting을 넣지 않는다.

## 전체 워크플로우

### Phase 0. 도메인 및 실행 설정 확인

1. 평가 도메인이 명확한지 확인한다.
2. 애매하면 사용자에게 확인한다.
3. 실행 설정을 정한다.
   - `target_average` 기본 40
   - `question_count` 기본 10
   - `max_version` 기본 10
   - `artifact_dir` 결정
4. `run-config.md`를 만든다.

주의:
- 이 단계의 설정값은 루브릭 파일에 넣지 않는다.

### Phase 1. `rubric-design`으로 초기 루브릭 생성

1. `rubric-design` 스킬을 로드한다.
2. 도메인 기준 세계 최고 수준 전문가 기준을 정의한다.
3. 초기 루브릭 v1을 작성한다.
4. 루브릭 파일에는 평가 기준만 포함한다.
5. 실행 설정은 루브릭에 넣지 않는다.

산출물:

```text
rubrics/{domain}-expert-rubric-v1.md
```

### Phase 2. 질문 생성 에이전트 실행

질문 생성은 별도 서브에이전트가 담당한다.

질문 생성 에이전트의 역할:

- 도메인 하위 영역을 골고루 포함하는 질문 `question_count`개 생성
- 각 질문의 평가 의도 작성
- 일반 답변이 쉽게 그럴듯하게 답할 수 있지만, 전문가 답변과 차이가 드러나는 질문으로 구성
- 질문 본문에는 루브릭이나 평가 목적을 노출하지 않음

산출물:

```text
iterations/v{version}/questions.md
```

### Phase 3. N개 신규 서브에이전트 병렬 실행

각 질문마다 서브에이전트 하나를 배정한다.

각 서브에이전트는 다음을 수행한다.

1. 질문에 대한 일반 답변 작성
2. 답변 파일 저장
3. 현재 루브릭 읽기
4. 자기 답변 채점
5. 채점 파일 저장
6. `final_score` 반환

핵심 개선점:

- 답변을 먼저 모두 준비한 뒤 따로 채점하지 않는다.
- 기본 루브릭 캘리브레이션에서는 질문별 신규 서브에이전트가 답변 작성과 채점을 한 번에 수행할 수 있다.
- 단, wiki 품질/자료 corpus를 루브릭으로 평가하는 workflow에서는 예외적으로 질문 생성, wiki 답변, 루브릭 채점을 반드시 서로 다른 신규 서브에이전트로 분리한다. 같은 에이전트가 질문·답변·채점을 모두 수행하면 평가가 오염된다.
- 답변 작성 전에는 루브릭을 보지 말라고 명시한다.
- 답변 작성 후 루브릭을 읽고 채점한다. 단, 위 예외 workflow에서는 답변 에이전트가 루브릭을 읽지 않고 별도 judge 에이전트가 채점한다.
- 평균 계산은 부모 에이전트가 수행한다.

산출물:

```text
iterations/v{version}/responses/qXX.md
iterations/v{version}/scores/qXX-score.md
```

### Phase 4. 결과 종합

부모 에이전트가 수행한다.

해야 할 일:

- 응답 파일 N개 존재 확인
- 점수 파일 N개 존재 확인
- 각 점수 파일에서 `final_score` 추출
- 평균 계산
- 목표 평균과 비교
- 고득점 답변의 공통 과대평가 원인 정리

산출물:

```text
iterations/v{version}/summary.md
```

평균 계산은 반드시 도구로 수행한다. 암산하거나 대략 계산하지 않는다.

### Phase 5. 종료조건 확인

종료조건은 `run-config.md`의 설정을 사용한다.

```text
if average_score < target_average:
    종료
elif current_version >= max_version:
    종료
else:
    루브릭 개선
```

종료 시 기록:

- 도달 버전
- 평균점수
- 질문 개수
- 최고점/최저점
- 목표 달성 여부
- max_version 도달 여부

### Phase 6. 루브릭 개선

목표 평균 미달성 시 수행한다.

1. 고득점 답변을 분석한다.
2. 과대평가 원인을 도출한다.
3. 개선 방향을 작성한다.
4. `rubric-design` 원칙에 맞춰 다음 루브릭 버전을 생성한다.
5. 루브릭 파일에는 평가 기준만 포함한다.

산출물:

```text
iterations/v{version}/gap-analysis.md
rubrics/{domain}-expert-rubric-v{version+1}.md
```

### Phase 7. 다음 루프

중요한 원칙:

- 다음 루프에서는 기존 질문을 재사용하지 않는다.
- 질문 생성 에이전트가 새 질문을 만든다.
- 새 질문 → 새 답변 → 새 채점으로 루브릭을 검증한다.
- 이 구조 때문에 기본 워크플로우에는 별도 holdout validation을 넣지 않는다.

원칙 문장:

```text
루브릭 개선 후 같은 답변을 다시 채점해 종료조건을 맞추지 않는다.
개선된 루브릭은 새 질문/새 답변으로 검증한다.
```

예외:

- 디버깅 또는 비교 목적이면 기존 질문 재채점 가능.
- 하지만 종료조건 검증에는 새 질문 세트를 사용한다.

## 서브에이전트 병렬 처리 규칙

### 질문 생성 에이전트

질문 세트 전체를 만드는 에이전트 1개를 사용한다.

### 답변+채점 에이전트

질문 수 N개만큼 신규 서브에이전트를 병렬로 사용한다.

- 각 에이전트는 질문 1개만 처리한다.
- 각 에이전트는 답변 작성과 채점을 모두 수행한다.
- 평균 계산은 하지 않는다.
- 파일 저장을 완료해야 한다.

도구/시스템 제한으로 N개를 한 번에 실행할 수 없으면 가능한 최대 병렬 수로 batch 처리한다.

예:

```text
question_count = 10
max parallel = 3
실행 batch:
- Q01~Q03
- Q04~Q06
- Q07~Q09
- Q10
```

### 부모 에이전트 검증

서브에이전트의 “완료했다”는 보고를 그대로 믿지 않는다.

부모 에이전트는 반드시 확인한다.

- 응답 파일 존재
- 점수 파일 존재
- `final_score` 존재
- 평균 계산 결과
- 목표 평균 달성 여부

## 프롬프트 템플릿

### 도메인 확인 템플릿

```text
평가 도메인이 명확하지 않습니다.
어떤 분야의 세계 최고 수준 전문가 루브릭으로 진행할까요?

예:
- 마케팅
- 투자
- 제품 전략
- 소프트웨어 설계
- 리서치
- 기타
```

### 질문 생성 에이전트 템플릿

```text
도메인: {domain}
질문 개수: {question_count}

세계 최고 수준 전문가 답변과 일반 답변의 차이가 드러나는 실무 질문 {question_count}개를 생성하라.

조건:
- 질문은 서로 다른 하위영역을 다룰 것
- 각 질문은 실제 실무자가 물을 법한 자연스러운 질문일 것
- 질문 본문에는 루브릭이나 평가 목적을 노출하지 말 것
- 각 질문마다 평가 의도를 별도로 기록할 것
- 질문은 일반론 답변이 쉽게 나올 수 있지만, 전문가 답변과 차이가 드러나도록 설계할 것

출력:
- Q번호
- 제목
- 질문
- 평가 의도
```

### 답변+채점 에이전트 템플릿

```text
너는 질문 하나를 처리하는 독립 서브에이전트다.

중요한 순서:
1. 먼저 루브릭을 보지 말고 질문에 대한 일반 답변을 작성한다.
2. 답변을 원문 그대로 파일에 저장한다.
3. 그 다음 루브릭을 읽고 답변을 채점한다.
4. 채점 결과를 파일에 저장한다.

질문:
{question}

답변 저장 경로:
{response_path}

루브릭 경로:
{rubric_path}

채점 저장 경로:
{score_path}

채점 지침:
- 답변에 명시된 내용만 인정한다.
- 루브릭의 cap/gate를 엄격 적용한다.
- final_score를 반드시 포함한다.
- 적용된 cap/gate 근거를 짧게 적는다.
- 평균 계산은 하지 않는다.
```

### 결과 종합 템플릿

```text
다음 score 파일들에서 final_score를 추출하라.
평균을 계산하라.
목표 평균점수 {target_average} 미만인지 확인하라.

출력:
- 문항별 점수표
- 합계
- 평균
- 목표 달성 여부
- 고득점 문항과 과대평가 가능성
- 다음 루프 필요 여부
```

## Common Pitfalls

1. **루브릭 파일에 워크플로우 설정을 넣는 것**
   - target average, question count, max version은 `run-config.md`에 둔다.

2. **rubric-design을 건너뛰는 것**
   - 기본 루브릭 설계는 이 스킬의 역할이 아니다.

3. **같은 질문/답변으로 반복 채점해 목표 평균만 맞추는 것**
   - 루프마다 질문을 새로 생성해야 한다.

4. **서브에이전트 보고를 그대로 믿는 것**
   - 부모가 파일과 점수를 직접 검증한다.

5. **평균을 암산하는 것**
   - 평균은 반드시 도구로 계산한다.

6. **답변 작성 전에 루브릭을 노출하는 것**
   - 답변+채점 에이전트는 먼저 답변을 쓰고 저장한 뒤 루브릭을 읽는다.

7. **질문 생성과 답변 생성을 같은 컨텍스트에서 섞는 것**
   - 질문 생성 에이전트와 답변+채점 에이전트를 역할상 분리한다.

8. **도메인이 애매한데 추측으로 진행하는 것**
   - 애매하면 사용자에게 확인한다.

## Verification Checklist

스킬 실행 또는 구현 후 확인한다.

- [ ] `rubric-design`을 먼저 사용했다.
- [ ] 도메인이 명확하다.
- [ ] 도메인이 애매한 경우 사용자에게 확인했다.
- [ ] `run-config.md`가 있다.
- [ ] 루브릭 파일에는 평가 기준만 들어 있다.
- [ ] target average, question count, max version이 루브릭 파일에 들어 있지 않다.
- [ ] 질문 생성 에이전트가 새 질문 세트를 만들었다.
- [ ] 질문 수가 `question_count`와 일치한다.
- [ ] 각 질문별 답변+채점 서브에이전트가 실행됐다.
- [ ] 응답 파일이 N개 존재한다.
- [ ] 점수 파일이 N개 존재한다.
- [ ] 모든 점수 파일에 `final_score`가 있다.
- [ ] 평균을 도구로 계산했다.
- [ ] 평균과 `target_average`를 비교했다.
- [ ] 목표 미달성 시 루브릭 개선과 새 질문 생성 루프로 진행했다.
- [ ] 종료 시 최종 루브릭과 summary를 저장했다.

## 참고 자료

- `references/design-rationale-2026-06-21.md`: 이 스킬을 만들 때 사용자 교정에서 나온 설계 근거와 병렬 검증 파이프라인 요약.

## Remember

```text
rubric-design은 루브릭을 만든다.
rubric-creating-expert는 루브릭을 실제 신규 답변으로 검증하고 개선한다.

루브릭 파일 = 평가 기준
run-config.md = 워크플로우 설정
iterations/vX = 질문, 답변, 채점, 요약

매 루프마다 새 질문을 만든다.
각 질문마다 새 서브에이전트가 답변과 채점을 수행한다.
부모 에이전트는 파일과 평균을 직접 검증한다.
```
