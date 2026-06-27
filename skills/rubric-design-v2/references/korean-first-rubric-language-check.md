# Korean-first 루브릭 언어 검증

## 목적

한국어 사용자용 skill 또는 rubric을 평가할 때 `한국어 우선`을 단순히 한글 포함 여부로 판정하지 않도록 보정합니다. 사람-facing prose의 기본 문장 언어가 한국어인지 확인하고, 번역 가능한 영어 heading, label, 절차 동사, 판단 기준이 반복되면 감점 또는 cap을 적용합니다.

## 허용되는 영어

아래 항목은 한국어 우선 위반으로 보지 않습니다.

- JSON/YAML key, enum value, schema field.
- file path, command, CLI flag, API name, URL.
- package, model, product, organization, repository 같은 proper noun.
- code identifier, function/class/module name.
- quoted source title 또는 원문 인용.
- 처음 한국어로 설명한 technical term의 괄호 병기.

## 감점해야 하는 영어

아래처럼 자연스러운 한국어 대체어가 있는데 사람-facing prose에 반복되는 영어는 감점합니다.

| 영어 표현 | 권장 한국어 예시 |
|---|---|
| workflow | 절차, 작업 흐름 |
| output | 출력, 산출물 |
| validation | 검증 |
| source | 출처, 원천 자료 |
| briefing | 브리핑, 보고서 |
| delivery | 전달, 게시 |
| status | 상태 |
| pattern | 패턴, 절차 패턴 |
| item | 항목 |
| parent / thread | 부모 메시지 / 스레드 |

## Deterministic checker 권장 절차

1. 평가 대상 파일을 읽습니다.
2. code fence, inline code, URL, file path, command, JSON/YAML key, enum, proper noun allowlist를 제외합니다.
3. 남은 human-facing prose에서 다음 값을 계산합니다.
   - 영어 prose token 비율.
   - 영어-only heading 수와 비율.
   - 번역 가능한 영어 label 반복 횟수.
4. checker 결과를 scorecard의 D5 근거와 global cap 판단 근거로 포함합니다.

## Cap 적용 기준 예시

- 영어 prose token 비율이 10%를 넘으면 D5는 최대 8점입니다.
- 영어 prose token 비율이 20%를 넘으면 D5는 최대 7점이고 total score는 최대 80점입니다.
- 영어 prose token 비율이 35%를 넘으면 D5는 최대 5점이고 total score는 최대 65점입니다.
- 주요 heading 또는 보고 template label의 20% 이상이 영어-only이면 total score는 최대 85점입니다.

## 주의

영어 사용 자체를 금지하지 않습니다. 목적은 machine identifier와 고유명사는 보존하되, 사람이 읽는 설명과 절차가 영어 prose에 기대지 않도록 하는 것입니다.
