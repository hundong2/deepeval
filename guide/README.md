# DeepEval 한국어 학습 가이드

작성일: 2026-07-28
기준 버전: DeepEval 4.1.4, 저장소 commit `bc296f8`

## 학습 목표

이 가이드는 LLM 평가를 처음 접하는 개발자가 로컬 테스트를 만들고,
숙련자가 RAG·에이전트 평가를 CI와 운영 관측 체계로 확장할 수 있도록
구성했습니다. 예제는 이 저장소의 주 언어인 Python을 사용합니다.

DeepEval은 “그럴듯해 보이는 응답”을 수동으로 확인하는 과정을 반복
가능한 테스트로 바꿉니다. 일반 단위 테스트와 달리 LLM 출력은 표현이
달라질 수 있으므로, 결정론적 검사와 LLM-as-a-judge를 목적에 맞게
조합해야 합니다.

## 학습 순서

1. [설치와 첫 평가](01_getting_started.md)
   - 가상환경, 환경변수, `LLMTestCase`, `assert_test`, CLI
2. [핵심 개념과 RAG 평가](02_core_concepts.md)
   - 테스트 데이터 설계, 메트릭 선택, 임계값, 실패 분석
3. [고급 운영과 확장](03_advanced.md)
   - 사용자 정의 메트릭, 비동기·캐시, trace, CI/CD, 보안과 비용
4. [실습 예제](examples/README.md)
   - API 키 없는 오프라인 메트릭
   - 실제 LLM 판정자를 이용하는 RAG 회귀 테스트

## 30분 빠른 경로

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1       # Windows PowerShell
# source .venv/bin/activate        # macOS/Linux
python -m pip install -U deepeval

python -m guide.examples.offline_keyword_metric
deepeval test run guide/examples/test_rag_quality.py
```

첫 명령은 API 키가 필요 없습니다. 두 번째 예제는 기본 판정 모델을
사용하므로 `OPENAI_API_KEY` 또는 사용자 정의 판정 모델 설정이
필요합니다.

## 평가 설계 지도

| 평가 대상 | 먼저 볼 신호 | 권장 메트릭 예 |
|---|---|---|
| 정형 출력 | 파싱 성공, schema, 필수 필드 | JSON Correctness, 사용자 정의 검사 |
| RAG 검색기 | 정답 근거 포함·순위 | Contextual Recall, Precision, Relevancy |
| RAG 생성기 | 근거 준수·질문 응답 | Faithfulness, Answer Relevancy |
| 에이전트 | 목표·도구·단계 | Task Completion, Tool Correctness, Step Efficiency |
| 대화 | 기억·역할·턴 품질 | Knowledge Retention, Role Adherence, Turn Relevancy |
| 안전성 | 공격 성공과 유해 출력 | Red Teaming, Bias, Toxicity |

하나의 종합 점수만 CI 게이트로 쓰지 마세요. “검색 실패”, “생성 환각”,
“출력 형식 오류”처럼 수정 주체가 다른 실패를 별도 메트릭으로 분리해야
원인을 빠르게 찾을 수 있습니다.

## 저장소 코드 읽기

평가가 실행되는 핵심 흐름은 다음과 같습니다.

```text
LLMTestCase / ConversationalTestCase
             │
             ▼
assert_test() 또는 evaluate()
             │
             ▼
동기·비동기 executor → metric.measure()/a_measure()
             │
             ▼
score + reason + threshold 판정 → 콘솔/파일/Confident AI
```

- `deepeval/test_case/llm_test_case.py`: 입력·출력·검색 문맥·도구 호출
  필드 정의
- `deepeval/evaluate/evaluate.py`: `assert_test()`와 `evaluate()` 진입점
- `deepeval/evaluate/configs.py`: 동시성, 캐시, 표시, 오류 처리 설정
- `deepeval/metrics/base_metric.py`: 사용자 정의 메트릭 계약
- `deepeval/dataset/dataset.py`: 데이터셋 생성·로드·반복 평가
- `deepeval/tracing/`: 실행 span과 평가 결과 연결

## 원본 문서와 지원

- [한국어 README](../README_kor.md)
- [원본 README](../README.md)
- [공식 문서](https://deepeval.com/docs/getting-started)
- [기여 안내](../CONTRIBUTING.md)
- [라이선스](../LICENSE.md)

문서와 구현이 다를 때는 현재 checkout의 코드, release note, 공식 문서
순으로 확인하고 사용 중인 버전을 테스트 결과에 기록하세요.
