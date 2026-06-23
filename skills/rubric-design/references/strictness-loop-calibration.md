# Hard target average를 위한 strictness-loop calibration

사용자가 “average score가 40 미만이 되거나 v10에 도달할 때까지 rubric을 계속 evolve해줘”처럼 measured score target에 도달할 때까지 rubric을 iteratively tighten하라고 요청할 때 이 reference를 사용한다.

## 패턴

1. rubric을 수정하기 전에 explicit stop conditions를 정의한다.
   - Example: `average_score < 40 OR rubric_version == v10`.
   - score target은 calibration objective로 취급하고, scores를 fabricate해도 된다는 허가로 취급하지 않는다.

2. real calculation으로 current baseline을 established한다.
   - current scores table을 읽는다.
   - mental calculation이 아니라 tool/script로 average를 compute한다.
   - baseline을 loop log에 기록한다.

3. sample set이 여러 domains에 걸쳐 있으면 independent diagnosis를 위해 parallel subagents를 사용한다.
   - arbitrary line ranges가 아니라 domain 또는 sample cluster 기준으로 split한다.
   - 각 subagent에게 over-credit patterns를 식별하고 caps/gates를 제안하게 한다.
   - outputs는 proposals로 유지하고, final rubric은 직접 synthesize한다.

4. point weights를 변경하기 전에 gates/caps를 추가해서 tighten한다.
   - hard average target의 경우 weights만으로는 scores를 충분히 움직이기 어렵다.
   - 40+ / 60+ / 75+ gates와 domain-specific hard caps를 추가한다.
   - “mentions a metric”과 “uses a numeric decision rule”을 구분한다.

5. parallel로 re-score한다.
   - sample answers를 batches로 split한다.
   - subagents에게 new rubric을 엄격하게 적용하고 final_score + cap/gate reason only를 반환하도록 지시한다.
   - results를 수집한 뒤 average를 centrally compute한다.

6. 첫 번째 stop condition이 충족되면 즉시 중단한다.
   - `average < target`이면 later versions로 계속 진행하지 않는다.
   - version ceiling에 도달하면 중단하고 best achieved average를 보고한다.

7. durable artifacts를 저장한다.
   - New rubric version: `...rubric-vN.md`
   - Score table: `scores-vN.md`
   - Loop log: `strictness-loop.md`
   - subagents가 유용한 domain analyses를 생성한 경우 proposal files.

## 유용한 strictness lever

- 40+ gate: numeric decision rule, required economic metric, failure/stop condition, relevant customer/competition context, explicit choice/forfeit를 요구한다.
- 60+ gate: segment-specific strategy, competitor/substitute analysis, unit economics 또는 financial scenario, real experiment design, risk/pivot, trade-off를 요구한다.
- 75+ gate: financial model, statistically/operationally credible experiment, resource constraints/opportunity cost, success/stop/scale rules, pivot condition을 요구한다.
- Domain hard caps: domain의 essential proof가 없는 answers를 cap한다.
  - B2B SaaS: ACV, sales cycle, CAC payback, pipeline source, conversion baselines.
  - DTC retention: purchase cycle, replenishment, cohort LTV, margin, holdout details.
  - App retention: activation event, aha moment, habit loop, cohort segmentation, LTV/CAC stop rule.
  - Premium repositioning: WTP, price anchor, premium proof, cannibalization/rollback.
  - Content marketing: cost, payback, opportunity cost, sourced vs influenced pipeline, kill/scale threshold.
  - Incrementality: MDE/sample, pre-period balance, contamination, confidence/uncertainty.
  - Pricing: revenue/churn scenarios, elasticity/WTP, grandfathering economics.
  - Competitive entry: competitor battlecard, wedge economics, ACV/CAC/payback, validation thresholds.

## 함정

- rubric을 변경하지 않은 채 단순히 “grade harsher”하지 않는다. strictness는 observable gates/caps로 encode한다.
- strong answers를 임의로 낮추지 않는다. 어떤 explicit high-bar condition이 빠졌는지 설명한다.
- 길고 잘 구조화된 playbooks라도 decision rules와 economics가 없으면 high score를 주지 않는다.
- stop condition이 충족된 뒤 loop를 계속하지 않는다.
