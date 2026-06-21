# AI Quality Feedback Loops — 연구 노트

사용자가 반복적인 사용 과정에서 AI/LLM 답변의 품질을 개선하고 싶어 할 때, 특히 출력이 자주 만족스럽지 않다고 불평하며 체계적인 피드백 루프를 원할 때 이 참고 자료를 사용하세요.

## 핵심 운영 루프

실용적인 개인/팀 루프:

1. 만족스럽지 않은 출력을 실패 사례로 캡처합니다.
2. 실패 유형을 라벨링합니다: 요구사항 누락, 사실 오류, 근거/날짜 누락, 오래된 정보, 일반적인 답변, 실행 불가능함, 검증되지 않음, 잘못된 톤, 지나치게 장황함, 의도 오해.
3. 관찰 가능한 체크리스트 항목과 상한 규칙이 포함된 작업별 루브릭을 작성하거나 수정합니다.
4. 대표 프롬프트/작업으로 구성된 작은 golden set을 구축합니다.
5. 후보 프롬프트/모델/워크플로를 golden set에 대해 평가합니다.
6. 프롬프트, 검색, 도구 사용, 모델 선택 또는 워크플로를 개선합니다.
7. 동일한 eval set을 다시 실행해 변화를 측정합니다.
8. 새로운 운영 환경의 실패를 데이터셋에 다시 추가합니다.

## 영향력 있는 방법과 출처

- Hamel Husain, “Your AI Product Needs Evals” — 발표일 2024-03-29, https://hamel.dev/blog/posts/evals/
  - evals를 AI 제품 품질의 기반으로 다룹니다.
  - 출력이 좋은/나쁜 이유를 설명하는 사람의 비평을 수집합니다.
  - 평가자 프롬프트/모델이 사람의 판단과 일치할 때까지 반복 개선합니다.

- OpenAI Evals — 레포지토리 생성 시점 2023-01-23T20:51:04Z, https://github.com/openai/evals
  - LLM과 LLM 시스템을 평가하기 위한 프레임워크 및 레지스트리입니다.
  - 전이 가능한 핵심 아이디어: 임시방편적 판단 대신 예시 + 기대 동작/채점 기준을 사용합니다.

- Anthropic, “Building Effective AI Agents” — 발표일 2024-12-19, https://www.anthropic.com/engineering/building-effective-agents
  - 명확한 성공 기준, 피드백 루프, 사람의 감독을 강조합니다.
  - 유용한 패턴: 한 구성 요소가 생성하고 다른 구성 요소가 평가/개선하는 evaluator-optimizer 루프.

- Shinn et al., “Reflexion: Language Agents with Verbal Reinforcement Learning” — arXiv 발표일 2023-03-20T18:08:50Z, https://arxiv.org/abs/2303.11366
  - 시도 실패를 자연어 reflection으로 변환하여 모델 파인튜닝 없이 이후 시도를 개선합니다.
  - “최신 정보 질문에는 출처/날짜 검증이 필요하다”와 같은 지속적인 실패 노트에 유용합니다.

- Khattab et al., “DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines” — arXiv 발표일 2023-10-05T17:37:25Z, https://arxiv.org/abs/2310.03714
  - 프롬프트 엔지니어링을 데이터/메트릭에 대해 프로그램을 최적화하는 작업으로 재구성합니다.
  - 반복적인 프롬프트 조정을 golden set에 대해 측정해야 할 때 사용합니다.

- Zheng et al., “Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena” — arXiv 발표일 2023-06-09T05:55:52Z, https://arxiv.org/abs/2306.05685
  - LLM-as-a-judge를 대중화했고 한계/편향을 논의합니다.
  - 모델/프롬프트 선택에서는 절대 점수화보다 pairwise comparison이 더 쉽고 신뢰할 수 있을 때가 있습니다.

- Chiang et al., “Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference” — arXiv 발표일 2024-03-07T01:22:38Z, https://arxiv.org/abs/2403.04132
  - 사람 선호 + pairwise comparison + Elo 스타일 랭킹.
  - 모델 또는 프롬프트 버전 간 개인 A/B 테스트에 유용한 모델입니다.

- Es et al., “Ragas: Automated Evaluation of Retrieval Augmented Generation” — arXiv 발표일 2023-09-26T19:23:54Z, https://arxiv.org/abs/2309.15217
  - RAG 품질의 경우, 검색 관련성, 충실성, 맥락 지원, hallucination 위험을 일반 답변 품질과 별도로 평가합니다.

- Eugene Yan, “Patterns for Building LLM-based Systems & Products” — 발표일 2023-07-30, https://eugeneyan.com/writing/llm-patterns/
  - 사용자 피드백을 만족도와 제품 효과성의 구체적인 척도로 강조합니다.
  - 간단한 thumbs-up/down와 이유 라벨이 eval 데이터셋이 될 수 있습니다.

## 사용자에게 권장되는 산출물 형태

이 유형의 요청에 답할 때는 다음을 포함하세요:

- 권장 기준을 먼저 제시합니다.
- 단순 참고문헌이 아니라 간결하게 순위가 매겨진 방법 묶음.
- 각 방법의 출처 링크 + 공개 시간/날짜.
- 사용자가 오늘 바로 시작할 수 있는 구체적인 루프.
- 실패를 기록하기 위한 경량 템플릿.
- 루프를 성숙시키기 위한 루브릭/golden-set/A-B-test 경로.

## 경량 템플릿

실패 로그 열:

| 날짜 | 작업 유형 | 출력/링크 | 실패 유형 | 문제점 | 더 나은 답안 기준 | 재시험 결과 |
|---|---|---|---|---|---|---|

일반적인 실패 라벨:

- 요구사항 누락
- 사실 오류
- 출처/근거 누락
- 공개/업데이트 날짜 누락
- 오래된 정보
- 지나치게 일반적임
- 실행 가능하지 않음
- 검증되지 않음
- 잘못된 톤/스타일
- 지나치게 장황함
- 의도 오해

연구 답변 예시 상한 규칙:

- 출처 없음: 총점은 60점으로 제한됩니다.
- 요청된 공개 날짜 누락: 총점은 75점으로 제한됩니다.
- 핵심 사용자 질문 무시: 총점은 50점으로 제한됩니다.
- 조작된 출처/도구 결과: 총점은 40점으로 제한됩니다.
