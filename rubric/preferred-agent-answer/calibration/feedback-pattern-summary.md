# 선호 답변 루브릭용 피드백 패턴 요약

## 분석 범위

- 원천 경로: `/Users/stark/wiki/raw/feedback`
- 분석 파일 수: 39
- 목적: 사용자가 실제로 불만족을 기록한 사건을 바탕으로 “선호하는 에이전트 답변”의 관찰 가능한 채점 기준을 도출한다.

## Category 집계

| category | count |
|---|---:|
| `requirement-miss` | 27 |
| `context-misread` | 21 |
| `specificity` | 18 |
| `verification` | 16 |
| `actionability` | 6 |
| `format` | 5 |
| `decision-criteria` | 5 |
| `evidence` | 4 |
| `tone` | 1 |
| `overconfidence` | 1 |

## Severity 집계

| severity | count |
|---|---:|
| `medium` | 22 |
| `low` | 8 |
| `high` | 8 |
| `critical` | 1 |

## Task type 집계

| task_type | count |
|---|---:|
| `automation` | 15 |
| `planning` | 13 |
| `review` | 4 |
| `other` | 2 |
| `coding` | 2 |
| `summarization` | 2 |
| `research` | 1 |

## 도출한 선호 패턴

| ID | 싫어한 실패 패턴 | 선호 답변 기준 | 루브릭 차원 | 근거 수 |
|---|---|---|---|---:|
| P1 | 명시 요구사항 또는 핵심 deliverable 누락 | 답변은 사용자의 명시 요구사항, 산출물, 제약을 빠짐없이 체크리스트화하고 실제 출력에 반영해야 한다. | D1 요구사항·의도 정합성 | 27 |
| P2 | 사용자 의도, 범위, reference/dependency 경계 오독 | 답변은 현재 요청의 의도와 승인된 scope를 좁게 해석하고, 참고자료를 직접 의존성으로 과잉 변환하지 않아야 한다. | D1 요구사항·의도 정합성 / D3 승인·scope·안전 경계 | 21 |
| P3 | 실행·검증 없이 결론 또는 완료 주장 | 답변은 live evidence, read-back, parse/lint/test, API/UI/log output 같은 실제 검증 근거로 결론을 뒷받침해야 한다. | D2 근거·검증·완료 주장 | 20 |
| P4 | generic하거나 현재 환경에 맞지 않는 조언 | 답변은 현재 파일, repo, OS/runtime, tool, 배포/게시 target, 사용자의 workflow에 맞춘 구체적 행동으로 내려와야 한다. | D4 구체성·맥락 적용·실행 가능성 | 18 |
| P5 | 승인 전 실행, 승인 범위 밖 state write, 외부 게시/자동화 기준 누락 | 답변은 plan/approval/execution/verification을 분리하고 위험 행동 전 target·account·body·scope·approval을 확인해야 한다. | D3 승인·scope·안전 경계 |  |
| P6 | 판단 기준·tradeoff·알림/릴리즈 기준 불명확 | 추천·분류·게시 여부·릴리즈 여부 같은 판단에는 명시적 criteria, threshold, 제외 조건, tradeoff가 있어야 한다. | D5 판단 품질·decision criteria | 5 |
| P7 | 요청한 형식, Korean-first, machine identifier 보존 경계 미준수 | 답변은 한국어 우선, 결론 먼저, bullet 중심, terminal-friendly 형식을 유지하되 path/key/command/API/enum은 원문으로 보존해야 한다. | D6 보고 형식·언어·가독성 | 6 |
| P8 | 실패 원인·영향·복구 경로 분리 부족 | 실패 시 command/tool/error, 확인된 원인과 추정, 영향, 복구 행동, 미검증 항목을 분리 보고해야 한다. | D7 실패 처리·복구 제안 | 6 |

## 대표 로그

- `/Users/stark/wiki/raw/feedback/2026-06-19/014738-1517208113118318595-overtranslated-structural-headings.md` — 피드백 로그: 구조용 제목까지 과하게 번역함 / severity=`low` / categories=`context-misread`, `format`, `tone`
- `/Users/stark/wiki/raw/feedback/2026-06-21/134153-unknown-session-misplaced-codex-script.md` — Feedback Log: Codex-Specific Script Left in Shared Skill Layout / severity=`medium` / categories=`requirement-miss`, `context-misread`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-21/141259-unknown-session-missing-routing-verification.md` — Feedback Log: Missing Skill Routing Verification / severity=`high` / categories=`verification`, `requirement-miss`, `context-misread`
- `/Users/stark/wiki/raw/feedback/2026-06-21/143622-20260621_141850_dedc2a-hard-coded-runtime-session-id.md` — 피드백 로그: 세션 ID 수정을 특정 런타임에만 맞춤 / severity=`medium` / categories=`context-misread`, `specificity`, `requirement-miss`
- `/Users/stark/wiki/raw/feedback/2026-06-21/152552-20260621_151815_34fc37-unsafe-artifact-storage.md` — Feedback Log: Unsafe Artifact Storage and Mixed Rubric Results / severity=`high` / categories=`requirement-miss`, `context-misread`, `verification`
- `/Users/stark/wiki/raw/feedback/2026-06-21/203617-20260621_155317_b5b241-executed-before-plan-approval.md` — Feedback Log: Executed File Edits Before Final Plan Approval / severity=`critical` / categories=`requirement-miss`, `context-misread`
- `/Users/stark/wiki/raw/feedback/2026-06-22/040446-20260621_083546_066dacf2-insufficient-session-verification.md` — Feedback Log: Insufficient Session Verification Before Warning Analysis / severity=`medium` / categories=`verification`, `evidence`, `overconfidence`
- `/Users/stark/wiki/raw/feedback/2026-06-22/040451-20260621_084014_09319e13-unapproved-extra-state-write.md` — Feedback Log: Unapproved Extra State Write Attempt / severity=`medium` / categories=`requirement-miss`, `verification`
- `/Users/stark/wiki/raw/feedback/2026-06-22/040522-20260621_163037_118ddae2-extra-slot-column-format.md` — Feedback Log: Extra Slot Column In Vending Transfer List / severity=`low` / categories=`format`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-22/040523-20260621_125901_993bed8b-generic-automation-section.md` — Feedback Log: Generic Automation Section Needed Replacement / severity=`medium` / categories=`specificity`, `actionability`
- `/Users/stark/wiki/raw/feedback/2026-06-22/040623-20260621_132151_b6209503-invalid-external-skills-config.md` — Feedback Log: External Skills Path Config Needed Rework / severity=`medium` / categories=`verification`, `requirement-miss`
- `/Users/stark/wiki/raw/feedback/2026-06-23/002843-20260623_000102_29f312-overly-domain-specific-skill-plan.md` — Feedback Log: Overly Domain-Specific Skill Plan / severity=`high` / categories=`context-misread`, `requirement-miss`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-23/002844-20260623_000102_29f312-missing-agent-isolation-rule.md` — Feedback Log: Missing Agent Isolation Rule in Rubric Loop / severity=`high` / categories=`requirement-miss`, `context-misread`, `verification`
- `/Users/stark/wiki/raw/feedback/2026-06-23/002845-20260623_000102_29f312-wrong-skill-target-path.md` — Feedback Log: Wrong Skill Target Path / severity=`high` / categories=`context-misread`, `verification`, `requirement-miss`
- `/Users/stark/wiki/raw/feedback/2026-06-23/010842-20260623_000102_29f312-reference-treated-as-dependency.md` — Feedback Log: Reference Treated as Dependency / severity=`medium` / categories=`context-misread`, `requirement-miss`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-23/010843-20260623_000102_29f312-missing-defaults-and-variables.md` — Feedback Log: Missing Defaults and Variables in Skill Plan / severity=`low` / categories=`requirement-miss`, `decision-criteria`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012201-20260619_004839_a87a6af4-raw-feedback-rejected-as-wiki-data.md` — Feedback Log: AI 품질 개선 피드백 루프 — raw-feedback-rejected-as-wiki-data / severity=`medium` / categories=`context-misread`, `requirement-miss`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012202-20260619_004839_a87a6af4-raw-feedback-status-fields.md` — Feedback Log: AI 품질 개선 피드백 루프 — raw-feedback-status-fields / severity=`low` / categories=`requirement-miss`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012203-20260620_081238_26c0d26d-missed-required-report-format.md` — Feedback Log: 정규 포맷 변환 요청 — missed-required-report-format / severity=`low` / categories=`format`, `requirement-miss`, `context-misread`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012204-20260621_133458_188f0f-overaggressive-auto-sync-frequency.md` — Feedback Log: 파일 변경 자동 커밋 푸시 — overaggressive-auto-sync-frequency / severity=`low` / categories=`decision-criteria`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012205-20260621_141838_d4a1b7-mixed-wiki-generation-into-rubric-plan.md` — Feedback Log: 마케팅 전문가 위키 루브릭 설계 — mixed-wiki-generation-into-rubric-plan / severity=`medium` / categories=`context-misread`, `requirement-miss`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012206-20260621_141838_d4a1b7-imagined-samples-instead-of-real-new-session-calibration.md` — Feedback Log: 마케팅 전문가 위키 루브릭 설계 — imagined-samples-instead-of-real-new-session-calibration / severity=`high` / categories=`verification`, `context-misread`, `evidence`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012207-20260621_152041_28de40-rubric-failed-general-answer-under-40-verification.md` — Feedback Log: B2B SaaS 초기 성장 마케팅 전략 — rubric-failed-general-answer-under-40-verification / severity=`high` / categories=`verification`, `evidence`, `decision-criteria`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012208-20260621_155317_b5b241-unnecessary-dual-mode-and-missing-idempotency.md` — Feedback Log: feedback-ai-logging 일괄 수집 개선 — unnecessary-dual-mode-and-missing-idempotency / severity=`medium` / categories=`requirement-miss`, `specificity`, `actionability`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012209-20260621_152002_3e3d33-rubric-skill-plan-ignored-user-workflow-and-target-location.md` — Feedback Log: 마케팅 전문가 답변 평가 루브릭 — rubric-skill-plan-ignored-user-workflow-and-target-location / severity=`medium` / categories=`context-misread`, `requirement-miss`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012210-20260621_152002_3e3d33-workflow-settings-mixed-into-rubric-artifact.md` — Feedback Log: 마케팅 전문가 답변 평가 루브릭 — workflow-settings-mixed-into-rubric-artifact / severity=`medium` / categories=`context-misread`, `requirement-miss`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012211-20260622_004940_73ebef-non-article-research-sources-missed.md` — Feedback Log: 마케팅의 기본 개념 #2 — non-article-research-sources-missed / severity=`medium` / categories=`evidence`, `requirement-miss`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012212-20260622_011539_7480da-feedback-logs-written-to-domain-wiki-path.md` — Feedback Log: 마케팅의 기본 개념 #7 — feedback-logs-written-to-domain-wiki-path / severity=`high` / categories=`context-misread`, `verification`, `requirement-miss`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012213-20260622_233019_ccd310-ad-hoc-wiki-health-check-lacked-fixed-rules.md` — Feedback Log: llm-wiki 읽기전용 상태점검 — ad-hoc-wiki-health-check-lacked-fixed-rules / severity=`medium` / categories=`verification`, `specificity`, `decision-criteria`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012214-20260622_233019_ccd310-rubric-files-not-namespaced-under-llm-wiki-directory.md` — Feedback Log: llm-wiki 읽기전용 상태점검 — rubric-files-not-namespaced-under-llm-wiki-directory / severity=`low` / categories=`requirement-miss`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-23/012215-20260623_010403_ed178a-korean-filename-requirement-not-checked.md` — Feedback Log: llm-wiki 읽기전용 상태점검 #2 — korean-filename-requirement-not-checked / severity=`medium` / categories=`requirement-miss`, `verification`, `format`
- `/Users/stark/wiki/raw/feedback/2026-06-24/040342-20260623_091829_aced5bf1-wrong-token-report-source-scope.md` — 피드백 로그: Token Report Scoped To Discord Instead Of All Hermes / severity=`medium` / categories=`requirement-miss`, `context-misread`, `specificity`
- `/Users/stark/wiki/raw/feedback/2026-06-24/040342-20260623_094205_dfa21284-codex-alpha-release-gate.md` — 피드백 로그: Codex Alpha Release Counted as Release / severity=`medium` / categories=`requirement-miss`, `decision-criteria`
- `/Users/stark/wiki/raw/feedback/2026-06-24/040346-20260623_093336_bfe5fe50-unsafe-incorrect-verification-command.md` — 피드백 로그: Unsafe Incorrect Verification Command / severity=`medium` / categories=`verification`, `actionability`
- `/Users/stark/wiki/raw/feedback/2026-06-24/040427-20260623_161841_81682e70-missing-rubric-reproducibility-gate.md` — 피드백 로그: Rubric Missing Same-Answer Reproducibility Gate / severity=`medium` / categories=`requirement-miss`, `verification`
- `/Users/stark/wiki/raw/feedback/2026-06-24/040438-20260623_231426_34958ad1-flat-skill-list-hard-to-distinguish.md` — 피드백 로그: Flat Skill Inventory Was Hard To Distinguish / severity=`low` / categories=`format`, `actionability`
- `/Users/stark/wiki/raw/feedback/2026-06-24/040439-20260623_231426_34958ad1-macos-bash-mapfile-in-cron-script.md` — 피드백 로그: macOS Bash 3 Incompatible mapfile in Cron Script / severity=`medium` / categories=`verification`, `context-misread`
- `/Users/stark/wiki/raw/feedback/2026-06-25/040028-20260624_094142_62e29f6e-official-gate-missing-for-news-briefing.md` — 피드백 로그: Official Announcement Gate Missing For News Briefing / severity=`medium` / categories=`requirement-miss`, `context-misread`, `actionability`
- `/Users/stark/wiki/raw/feedback/2026-06-26/040437-20260625_094324_a87fc371-fragile-credential-command-rework.md` — 피드백 로그: Credential Command Error Caused QA Rework / severity=`medium` / categories=`verification`, `context-misread`, `actionability`
