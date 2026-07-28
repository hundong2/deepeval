# 01. 설치와 첫 평가

## 1. 평가 환경 만들기

Python 3.9 이상을 준비하고 프로젝트마다 가상환경을 분리합니다.

```bash
python --version
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -U deepeval
deepeval --help
```

이 저장소 자체를 수정한다면 `pip install` 대신 Poetry 기반 개발 환경을
사용합니다.

```bash
poetry install
poetry run deepeval --help
```

## 2. 환경변수 이해하기

LLM-as-a-judge 메트릭은 판정 모델의 자격 증명이 필요합니다. OpenAI를
기본으로 사용할 때:

```powershell
# 현재 PowerShell 프로세스에만 적용
$env:OPENAI_API_KEY="..."
```

```bash
# macOS/Linux 현재 shell에만 적용
export OPENAI_API_KEY="..."
```

프로젝트 로컬 설정은 `.env.local`에 둘 수 있습니다.

```dotenv
OPENAI_API_KEY=...
DEEPEVAL_TELEMETRY_OPT_OUT=1
```

DeepEval 4.1.4는 import 시 현재 작업 디렉터리의 `.env.local`, `.env`
순으로 로드합니다. 이미 프로세스에 있는 값이 우선합니다. 로드하지
않으려면 `DEEPEVAL_DISABLE_DOTENV=1`을 사용합니다.

주의할 점:

- `.env`, `.env.local`을 Git에 커밋하지 않습니다.
- 키를 코드·테스트 데이터·실패 로그에 출력하지 않습니다.
- CI에서는 저장소 secret을 환경변수로 주입합니다.
- Confident AI의 `deepeval login`은 플랫폼 동기화용이며, 로컬 전용
  테스트 자체에는 필수가 아닙니다.

## 3. 테스트 케이스의 최소 구조

```python
from deepeval.test_case import LLMTestCase

case = LLMTestCase(
    input="환불 기간은 얼마인가요?",
    actual_output="구매 후 30일 안에 환불할 수 있습니다.",
    expected_output="구매일로부터 30일 이내에 환불할 수 있습니다.",
    retrieval_context=["환불은 구매 후 30일 이내에 요청해야 합니다."],
)
```

필드의 의미:

- `input`: 사용자 입력 또는 작업
- `actual_output`: 평가할 시스템의 실제 출력
- `expected_output`: 사람이 작성한 기준 답변
- `retrieval_context`: 검색기가 실제로 반환한 문서 조각
- `context`: 참조 가능한 일반 문맥
- `tools_called`, `expected_tools`: 에이전트가 호출한 도구와 기대 도구
- `metadata`, `tags`, `name`: 분석·필터링을 위한 부가 정보
- `token_cost`, `completion_time`: 비용·지연 회귀 분석용 정보

모든 필드를 항상 채우는 것은 아닙니다. 선택한 메트릭이 요구하는 필드를
채워야 합니다.

## 4. `assert_test`로 회귀 테스트 만들기

```python
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams


def test_refund_policy():
    case = LLMTestCase(
        input="환불 기한은?",
        actual_output="상품 수령 후 30일 이내입니다.",
        expected_output="상품 수령 후 30일 이내입니다.",
    )
    correctness = GEval(
        name="정확성",
        criteria="실제 출력이 기대 출력의 정책과 일치하는지 판정한다.",
        evaluation_params=[
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
        ],
        threshold=0.8,
    )
    assert_test(case, [correctness])
```

```bash
deepeval test run test_refund.py
```

`assert_test()`는 임계값을 통과하지 못한 메트릭이 있으면
`AssertionError`를 발생시켜 테스트를 실패시킵니다. LLM 판정은
비결정적일 수 있으므로 처음부터 지나치게 촘촘한 임계값을 정하지 말고,
사람이 라벨링한 표본으로 분포를 확인한 후 정하세요.

## 5. `evaluate`로 실험 실행하기

```python
from deepeval import evaluate
from deepeval.evaluate.configs import AsyncConfig, CacheConfig, DisplayConfig
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

cases = [
    LLMTestCase(
        input="배송은 며칠 걸리나요?",
        actual_output="보통 2~3영업일 걸립니다.",
    ),
]

result = evaluate(
    test_cases=cases,
    metrics=[AnswerRelevancyMetric(threshold=0.7)],
    identifier="checkout-chatbot-v2",
    async_config=AsyncConfig(run_async=True, max_concurrent=5),
    cache_config=CacheConfig(write_cache=True, use_cache=True),
    display_config=DisplayConfig(
        show_indicator=True,
        print_results=True,
        results_folder=".deepeval_results",
    ),
)
```

`evaluate()`는 노트북·배치 실험에 적합합니다. `identifier`에 모델과
프롬프트 버전을 넣고, 결과 파일은 아티팩트로 보관하면 비교가 쉬워집니다.

## 6. 첫 실패를 디버깅하는 순서

1. 예외가 인증·rate limit·timeout인지, 실제 점수 실패인지 구분합니다.
2. 메트릭에 필요한 `expected_output`, `retrieval_context` 등이 있는지
   확인합니다.
3. `score`, `reason`, 입력·실제 출력·근거를 함께 읽습니다.
4. 같은 케이스를 소수 반복해 판정 분산을 확인합니다.
5. 기준 문장이 모호하면 메트릭 criteria와 기대 출력을 구체화합니다.
6. 검색 문맥 자체가 틀렸다면 생성 모델이 아니라 retrieval을 수정합니다.

다음: [핵심 개념과 RAG 평가](02_core_concepts.md)
