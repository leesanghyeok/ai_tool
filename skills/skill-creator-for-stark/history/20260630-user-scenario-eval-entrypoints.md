# 2026-06-30 user scenario eval entrypoints

## Mode

modify — `skill-creator-for-stark` 자체 사용자 시나리오 eval과 deterministic entrypoint를 보강했다.

## 변경 요약

- `evals/skill-creator-for-stark.eval.yaml`에 create/modify command scenario와 create/modify/migrate `llm-judge` scenario를 추가했다.
- `scripts/run_pipeline.py`를 추가해 `scripts/run_pipeline.py --input {input} --output {output}` command case가 실제 workflow entrypoint를 호출하도록 했다.
- `scripts/run_llm_judge.py`를 추가해 `{judge_packet}` JSON의 `schema_version`과 `prompt`를 검증하고 non-empty 자연어 output을 쓰도록 했다.
- `scripts/run_evals.py`와 `scripts/run_evals_template.py`의 `_judge_packet()`을 `schema_version + prompt` 계약으로 맞췄다.
- `templates/eval-spec.template.md`, `references/skill-eval-authoring-rules.md`, `README.md`, `SKILL.md`를 신규 case/entrypoint 계약에 맞춰 갱신했다.

## 검증 기록

- `python3 scripts/run_evals.py --validate` 통과.
- `python3 scripts/run_evals.py --json` 결과 `passed=8`, `failed=0`.
- `python3.11 -m unittest discover -s scripts/tests -v` 통과.
- `python3 scripts/check_pipeline.py .` 결과 `pipeline OK`.
- `python3 scripts/validate-skill-package.py .` 통과. 기존 authoring-skill 허용 warning은 남음.
- `python3 -m py_compile scripts/run_pipeline.py scripts/run_llm_judge.py scripts/run_evals.py scripts/run_evals_template.py` 통과.
- `git diff --check` 통과.
- OS temp `hermes-verify-*` ad-hoc verification으로 신규 case schema, judge positive/negative, pipeline temp output/read-back, cleanup을 확인했다.

## 남은 주의사항

- `run_llm_judge.py`의 portable eval path는 deterministic smoke judge adapter다. 실제 Hermes isolated subagent CLI binding, timeout/input size 제한은 external/isolated judge 실행 단계에서 별도 확인한다.
- `--promote`는 실행하지 않았고, 신규 scenario case의 `expected.json`은 생성하지 않았다.
