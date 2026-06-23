# AI 품질 피드백 루프 — 리서치 노트

사용자가 반복 사용 과정에서 AI/LLM 답변 품질을 개선하고 싶어 할 때, 특히 출력이 자주 만족스럽지 않다고 하며 체계적인 피드백 루프를 원할 때 이 참고 문서를 사용한다.

## 핵심 운영 루프

개인/팀이 실무적으로 사용할 수 있는 루프:

1. 만족스럽지 않은 출력을 실패 사례로 수집한다.
2. 실패 유형을 라벨링한다: 요구사항 누락, 사실 오류, 근거/날짜 누락, 오래된 정보, 일반적인 답변, 실행 가능하지 않음, 검증되지 않음, 잘못된 톤, 지나치게 장황함, 의도 오해.
3. 관찰 가능한 체크리스트 항목과 cap rule을 포함해 작업별 rubric을 작성하거나 개정한다.
4. 대표 prompt/task로 구성된 작은 golden set을 만든다.
5. 후보 prompt/model/workflow를 golden set에 대해 평가한다.
6. prompt, retrieval, tool use, model choice, workflow를 개선한다.
7. 동일한 eval set을 다시 실행해 변화를 측정한다.
8. 새 production failure를 dataset에 다시 추가한다.

## 영향력 있는 방법론과 출처

- Hamel Husain, “Your AI Product Needs Evals” — published 2024-03-29, https://hamel.dev/blog/posts/evals/
  - eval을 AI 제품 품질의 기반으로 다룬다.
  - 출력이 왜 좋은지/나쁜지 설명하는 human critique를 수집한다.
  - evaluator prompt/model이 human judgment와 정렬될 때까지 반복 개선한다.

- OpenAI Evals — repository created 2023-01-23T20:51:04Z, https://github.com/openai/evals
  - LLM과 LLM system을 평가하기 위한 framework 및 registry.
  - 전이 가능한 핵심 아이디어: 임시방편적 판단 대신 example + expected behavior/scoring criteria를 사용한다.

- Anthropic, “Building Effective AI Agents” — published 2024-12-19, https://www.anthropic.com/engineering/building-effective-agents
  - 명확한 success criteria, feedback loop, human oversight를 강조한다.
  - 유용한 패턴: 한 component가 생성하고 다른 component가 평가/개선하는 evaluator-optimizer loop.

- Shinn et al., “Reflexion: Language Agents with Verbal Reinforcement Learning” — arXiv published 2023-03-20T18:08:50Z, https://arxiv.org/abs/2303.11366
  - trial failure를 자연어 reflection으로 변환해 model fine-tuning 없이 후속 시도를 개선한다.
  - “최신 정보 질문에는 source/date verification이 필요하다” 같은 지속 가능한 실패 노트에 유용하다.

- Khattab et al., “DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines” — arXiv published 2023-10-05T17:37:25Z, https://arxiv.org/abs/2310.03714
  - prompt engineering을 data/metric에 대해 program을 최적화하는 문제로 재구성한다.
  - 반복적인 prompt 수정이 golden set 기준으로 측정되어야 할 때 사용한다.

- Zheng et al., “Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena” — arXiv published 2023-06-09T05:55:52Z, https://arxiv.org/abs/2306.05685
  - LLM-as-a-judge를 대중화했으며 그 한계와 bias를 논의한다.
  - model/prompt selection에서는 absolute scoring보다 pairwise comparison이 더 쉽고 신뢰도 높을 수 있다.

- Chiang et al., “Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference” — arXiv published 2024-03-07T01:22:38Z, https://arxiv.org/abs/2403.04132
  - human preference + pairwise comparison + Elo-style ranking.
  - model 또는 prompt version 간 개인 A/B test를 설계할 때 유용한 model이다.

- Es et al., “Ragas: Automated Evaluation of Retrieval Augmented Generation” — arXiv published 2023-09-26T19:23:54Z, https://arxiv.org/abs/2309.15217
  - RAG 품질의 경우 retrieval relevance, faithfulness, context support, hallucination risk를 일반 답변 품질과 분리해 평가한다.

- Eugene Yan, “Patterns for Building LLM-based Systems & Products” — published 2023-07-30, https://eugeneyan.com/writing/llm-patterns/
  - 사용자 피드백을 만족도와 제품 효과성을 측정하는 구체적 지표로 강조한다.
  - 단순한 thumbs-up/down과 reason label만으로도 eval dataset이 될 수 있다.

## 사용자에게 권장하는 deliverable 형태

이 유형의 요청에 답할 때는 다음을 포함한다:

- 추천 기준을 먼저 제시한다.
- 단순 bibliography가 아니라 간결하게 순위를 매긴 방법 묶음을 제시한다.
- 각 방법마다 source link + publication time/date를 포함한다.
- 사용자가 오늘 바로 시작할 수 있는 구체적인 loop를 제공한다.
- failure logging을 위한 lightweight template을 제공한다.
- loop를 성숙시키기 위한 rubric/golden-set/A-B-test 경로를 제시한다.

## 경량 템플릿

Failure log columns:

| Date | Task type | Output/link | Failure type | Why bad | Better-answer standard | Retest result |
|---|---|---|---|---|---|---|

Common failure labels:

- Requirement miss
- Factual error
- Missing source/evidence
- Missing publication/update date
- Stale information
- Too generic
- Not actionable
- Not verified
- Wrong tone/style
- Too verbose
- Misunderstood intent

Example research-answer cap rules:

- No sources: total score capped at 60.
- Missing publication dates when requested: total score capped at 75.
- Core user question ignored: total score capped at 50.
- Fabricated source/tool result: total score capped at 40.
