# AI Quality Feedback Loops — Research Notes

Use this reference when a user wants to improve the quality of AI/LLM answers over repeated use, especially when they complain that outputs are often unsatisfactory and want a systematic feedback loop.

## Core operating loop

A practical personal/team loop:

1. Capture unsatisfactory outputs as failure cases.
2. Label the failure type: requirement miss, factual error, missing evidence/date, stale info, generic answer, not actionable, unverified, wrong tone, too verbose, misunderstood intent.
3. Write or revise a task-specific rubric with observable checklist items and cap rules.
4. Build a small golden set of representative prompts/tasks.
5. Evaluate candidate prompts/models/workflows against the golden set.
6. Improve prompt, retrieval, tool use, model choice, or workflow.
7. Re-run the same eval set to measure change.
8. Add new production failures back into the dataset.

## Influential methods and sources

- Hamel Husain, “Your AI Product Needs Evals” — published 2024-03-29, https://hamel.dev/blog/posts/evals/
  - Treat evals as the foundation for AI product quality.
  - Collect human critiques explaining why outputs are good/bad.
  - Iterate evaluator prompts/models until they align with human judgment.

- OpenAI Evals — repository created 2023-01-23T20:51:04Z, https://github.com/openai/evals
  - Framework and registry for evaluating LLMs and LLM systems.
  - Key transferable idea: use examples + expected behavior/scoring criteria instead of ad hoc judgment.

- Anthropic, “Building Effective AI Agents” — published 2024-12-19, https://www.anthropic.com/engineering/building-effective-agents
  - Highlights clear success criteria, feedback loops, and human oversight.
  - Useful pattern: evaluator-optimizer loop where one component generates and another evaluates/improves.

- Shinn et al., “Reflexion: Language Agents with Verbal Reinforcement Learning” — arXiv published 2023-03-20T18:08:50Z, https://arxiv.org/abs/2303.11366
  - Convert trial failures into natural-language reflections that improve subsequent attempts without model fine-tuning.
  - Useful for durable failure notes such as “latest-info questions require source/date verification.”

- Khattab et al., “DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines” — arXiv published 2023-10-05T17:37:25Z, https://arxiv.org/abs/2310.03714
  - Reframes prompt engineering as optimizing a program against data/metrics.
  - Use when repeated prompt tweaks should be measured against a golden set.

- Zheng et al., “Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena” — arXiv published 2023-06-09T05:55:52Z, https://arxiv.org/abs/2306.05685
  - Popularized LLM-as-a-judge and discusses limitations/biases.
  - Pairwise comparison can be easier and more reliable than absolute scoring for model/prompt selection.

- Chiang et al., “Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference” — arXiv published 2024-03-07T01:22:38Z, https://arxiv.org/abs/2403.04132
  - Human preference + pairwise comparison + Elo-style ranking.
  - Useful model for personal A/B tests between models or prompt versions.

- Es et al., “Ragas: Automated Evaluation of Retrieval Augmented Generation” — arXiv published 2023-09-26T19:23:54Z, https://arxiv.org/abs/2309.15217
  - For RAG quality, evaluate retrieval relevance, faithfulness, context support, and hallucination risk separately from general answer quality.

- Eugene Yan, “Patterns for Building LLM-based Systems & Products” — published 2023-07-30, https://eugeneyan.com/writing/llm-patterns/
  - Emphasizes user feedback as a concrete measure of satisfaction and product effectiveness.
  - Simple thumbs-up/down plus reason labels can become an eval dataset.

## Recommended deliverable shape for users

When answering this class of request, include:

- Recommendation criteria first.
- A concise ranked set of methods, not just a bibliography.
- Source link + publication time/date for each method.
- A concrete loop the user can start today.
- A lightweight template for logging failures.
- A rubric/golden-set/A-B-test path for maturing the loop.

## Lightweight templates

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
