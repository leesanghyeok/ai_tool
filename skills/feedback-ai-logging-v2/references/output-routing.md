# Output routing

## 목적

feedback raw log가 프로젝트별 domain wiki로 잘못 저장되지 않게 output root와 subdir 결정 기준을 고정한다.

## Routing priority

1. `INPUT_OUTPUT_ROOT`가 명시되어 있으면 사용한다.
2. 없으면 `FEEDBACK_WIKI_PATH` 환경값을 사용한다.
3. 없으면 일반 feedback/wiki 용도로 명시된 `WIKI_PATH`를 사용한다.
4. 없으면 `$HOME/wiki`를 사용한다.
5. `WIKI_PATHS`나 `WIKI_DEFAULT`가 domain routing을 가리키더라도 사용자가 feedback 목적지로 명시하지 않았으면 default로 쓰지 않는다.

`INPUT_OUTPUT_SUBDIR` 기본값은 `raw/feedback`이다.

## Recovery

잘못된 domain wiki에 raw feedback file을 썼다면 body를 수정하지 말고 올바른 root로 이동한다. Filename과 frontmatter가 틀리지 않았다면 보존하고, 이동 후 validator로 body-only hash를 확인한다.
