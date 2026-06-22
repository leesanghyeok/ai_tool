# 루브릭 v3류 회사별 데이터 blocker와 raw 검증 메모

## 언제 참고하나

`wiki-learning-rubric` 실행 중 루브릭이 다음을 요구할 때 참고한다.

- 회사별 baseline, CAC/LTV/payback, margin, NRR/GRR, churn, ACV, sales cycle
- 경쟁자별 win/loss, switching cost, proof gap
- 실험 표본 수, MDE/power, holdout/control 가능성
- segment별 revenue/churn/margin 시나리오

## 핵심 교훈

공개 자료와 wiki corpus 보강은 전문가 프레임워크를 강화할 수 있지만, 루브릭이 “실제 경영 의사결정 자료 수준”과 “회사별 데이터가 없으면 높은 점수 불가”를 명시하면 공개 corpus만으로 target_average 90 통과를 주장하면 안 된다.

이 경우 종료 보고는 다음 셋을 분리한다.

1. 현재 wiki-only baseline score
2. 공개 자료 기반 raw 수집 및 compiled page 보강 결과
3. 90점 통과를 막는 private/company-specific data checklist

## 반복 운영 규칙

- baseline 질문/답변/채점은 원칙대로 분리 subagent로 실행한다.
- 평균은 도구로 계산한다.
- 평균 미달 시 공개 자료로 보강하되, company-specific data가 없으면 `pass=false`를 유지한다.
- 다음 iteration은 실제/익명화 baseline data가 제공되거나, 사용자가 “가상 baseline scenario pack” 사용을 명시 승인할 때만 통과 가능성 검증으로 진행한다.
- 가상 baseline은 실제 통과가 아니라 `가정 기반 통과 가능성`으로 라벨링한다.

## Raw 수집 검증 pitfall

URL fetch가 `saved`로 끝나도 본문이 유효하다고 가정하지 않는다. 특히 다음은 raw 후보에서 제외하거나 대체 URL을 찾아야 한다.

- 404 page가 긴 HTML/Markdown으로 저장된 경우
- SPA shell, CSS/JS dump만 저장된 경우
- 실제 claim이 없는 pricing shell이나 generic landing page
- r.jina.ai가 200을 반환했지만 내용이 오류 페이지인 경우

최소 검증:

- `source_url`, `fetched_via`, `sha256`, `cluster`, `questions` frontmatter 존재
- 본문에 source title과 관련 claim이 있는지 샘플 read-back
- 404/error/page-not-found 문자열 검색
- 수집 report에 `saved/exists/failed`뿐 아니라 `invalid_content`를 별도 분류

## 보고 문구 예시

```text
현재 average_score는 43.0으로 target 90 미달입니다. 공개 자료 기반으로 raw와 compiled pages를 보강했지만, 루브릭이 요구하는 회사별 baseline/재무/실험 데이터가 없어 통과를 확인할 수 없습니다. 다음 iteration은 실제/익명화 company baseline data 또는 명시 승인된 가상 baseline scenario가 필요합니다.
```
