<p align="center">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="assets/hero/wordmark-dark.svg">
        <img alt="DeepEval" src="assets/hero/wordmark-light.svg" width="520">
    </picture>
</p>

<h1 align="center">LLM 평가 프레임워크</h1>

<p align="center">
    <a href="README.md">English</a> |
    <a href="guide/README.md"><strong>한국어 학습 가이드</strong></a> |
    <a href="https://deepeval.com/docs/getting-started">공식 문서</a>
</p>

> 이 문서는 2026-07-28의 원본 `README.md`와 DeepEval 4.1.4를 기준으로
> 작성한 한국어 번역본입니다. 변동될 수 있는 API와 지원 모델은
> [공식 문서](https://deepeval.com/docs/getting-started)도 함께 확인하세요.

**DeepEval**은 대규모 언어 모델(LLM) 시스템을 평가하는 사용하기 쉬운
오픈 소스 프레임워크입니다. Pytest와 비슷하지만 LLM 애플리케이션의 단위
테스트에 특화되어 있습니다. G-Eval, 작업 완료도, 답변 관련성, 환각 등의
최신 평가 방식을 제공하며, LLM-as-a-judge 또는 로컬에서 실행되는 NLP
모델을 이용합니다.

AI 에이전트, RAG 파이프라인, 챗봇을 LangChain이나 OpenAI 등 어떤
프레임워크로 구현했든 DeepEval로 모델·프롬프트·아키텍처를 비교할 수
있습니다. 이를 통해 품질 저하와 프롬프트 드리프트를 조기에 발견하고,
모델 공급자를 바꿀 때도 회귀 여부를 확인할 수 있습니다.

> [!IMPORTANT]
> 평가 데이터와 실행 이력을 팀 단위로 저장·비교하고 공유 보고서를
> 만들려면 [Confident AI](https://www.confident-ai.com)를 사용할 수
> 있습니다. 클라우드 사용 전에는 조직의 개인정보·보안 정책과
> [데이터 처리 안내](https://deepeval.com/docs/data-privacy)를 확인하세요.

## 메트릭과 주요 기능

DeepEval은 원하는 평가 모델, 통계 기법 또는 로컬 NLP 모델을 조합할 수
있으며 다음 범주를 지원합니다.

### 범용 사용자 정의 평가

- **G-Eval**: 평가 기준을 자연어로 정의하는 연구 기반
  LLM-as-a-judge 메트릭입니다.
- **DAG**: 판정 절차를 그래프로 구성해 더 결정론적인 평가 흐름을
  만드는 도구입니다.

### 에이전트 평가

- **Task Completion**: 에이전트가 목표를 달성했는지 평가합니다.
- **Tool Correctness / Tool Use**: 올바른 도구와 인자를 사용했는지
  확인합니다.
- **Goal Accuracy**: 의도한 목표를 정확히 달성했는지 측정합니다.
- **Step Efficiency**: 불필요한 단계가 있었는지 평가합니다.
- **Plan Adherence / Plan Quality**: 계획 준수 여부와 계획의 품질을
  평가합니다.
- **Argument Correctness**: 도구 호출 인자를 검증합니다.

### RAG 평가

- **Answer Relevancy**: 출력이 질문과 얼마나 관련 있는지 측정합니다.
- **Faithfulness**: 출력의 주장이 검색 문맥에 근거하는지 평가합니다.
- **Contextual Recall**: 정답에 필요한 정보가 검색 결과에 포함됐는지
  측정합니다.
- **Contextual Precision**: 관련 문서가 검색 순위 상단에 있는지
  평가합니다.
- **Contextual Relevancy**: 검색 문맥 전체가 질문과 관련 있는지
  평가합니다.
- **RAGAS**: 답변 관련성, 충실성, 문맥 정밀도와 재현율을 종합합니다.

### 대화·MCP·멀티모달 평가

- 다중 턴에서는 지식 유지, 대화 완결성, 턴 관련성·충실성, 역할 준수를
  평가할 수 있습니다.
- MCP 기반 에이전트에서는 작업 완료도, 서버·도구 사용, 다중 턴 MCP
  사용을 평가할 수 있습니다.
- 멀티모달에서는 텍스트-이미지 일치, 이미지 편집, 이미지 일관성,
  유용성, 참조 정확성을 다룹니다.

### 그 밖의 평가와 운영 기능

- 환각, 요약, 편향, 유해성, JSON 스키마 적합성, 프롬프트 지시 준수
- 엔드투엔드 평가와 컴포넌트 단위 평가
- 사용자 정의 메트릭
- 단일·다중 턴 합성 평가 데이터 생성
- CI/CD 통합과 회귀 테스트
- 평가 결과를 사용한 프롬프트 최적화
- MMLU, HellaSwag, DROP, BIG-Bench Hard, TruthfulQA, HumanEval,
  GSM8K 등 벤치마크 실행

## 통합

OpenAI, OpenAI Agents, Anthropic, LangChain, LangGraph, Pydantic AI,
CrewAI, AWS AgentCore, LlamaIndex, Google ADK, Strands 등과 연결할 수
있습니다. 프레임워크 통합은 애플리케이션의 호출·도구 사용·추적 정보를
수집하고, 평가 메트릭을 실행 흐름에 연결합니다.

Confident AI 플랫폼은 데이터셋 관리, 추적, 평가 실행, 프로덕션 모니터링
기능을 제공합니다. 플랫폼 연결은 선택 사항이며, 로컬 테스트만으로도
DeepEval 핵심 기능을 사용할 수 있습니다.

## 빠른 시작

### 1. 설치

DeepEval은 Python 3.9 이상을 지원합니다.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

python -m pip install -U deepeval
```

소스 저장소를 개발하려면 Poetry를 설치한 뒤 저장소 루트에서 실행합니다.

```bash
poetry install
```

### 2. 환경변수

기본 G-Eval 예제는 OpenAI 모델을 판정자로 사용하므로 키가 필요합니다.

```bash
# macOS/Linux
export OPENAI_API_KEY="..."

# Windows PowerShell
$env:OPENAI_API_KEY="..."
```

DeepEval은 import 시 현재 디렉터리의 `.env.local`, 그다음 `.env`를
자동으로 읽습니다. 우선순위는 **프로세스 환경변수 → `.env.local` →
`.env`**입니다. 자동 로드를 끄려면
`DEEPEVAL_DISABLE_DOTENV=1`을 설정합니다. `.env.local`은 Git에
커밋하지 마세요.

Confident AI에 평가 결과를 동기화하려면 다음 명령으로 로그인합니다.
클라우드를 쓰지 않는 로컬 평가에는 로그인이 필수는 아닙니다.

```bash
deepeval login
```

### 3. 첫 테스트 작성

`test_chatbot.py`를 만듭니다.

```python
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams


def test_refund_answer():
    metric = GEval(
        name="Correctness",
        criteria=(
            "Determine whether the actual output is correct "
            "based on the expected output."
        ),
        evaluation_params=[
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
        ],
        threshold=0.5,
    )
    test_case = LLMTestCase(
        input="신발이 맞지 않으면 어떻게 하나요?",
        actual_output="추가 비용 없이 30일 안에 전액 환불할 수 있습니다.",
        expected_output="모든 고객은 추가 비용 없이 30일 전액 환불 대상입니다.",
        retrieval_context=[
            "모든 고객은 추가 비용 없이 구매 후 30일 안에 전액 환불할 수 있습니다."
        ],
    )
    assert_test(test_case, [metric])
```

실행합니다.

```bash
deepeval test run test_chatbot.py
```

`input`은 사용자 입력, `actual_output`은 애플리케이션의 실제 응답,
`expected_output`은 이상적인 응답입니다. 점수는 일반적으로 0~1이고
`threshold` 이상이면 테스트가 통과합니다. 메트릭별 필수 필드는 서로
다르므로 메트릭 문서를 확인해야 합니다.

## Pytest 없이 평가

노트북이나 스크립트에서는 `evaluate()`를 직접 사용할 수 있습니다.

```python
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

case = LLMTestCase(
    input="신발이 맞지 않으면 어떻게 하나요?",
    actual_output="30일 안에 무료로 전액 환불할 수 있습니다.",
    retrieval_context=[
        "모든 고객은 추가 비용 없이 구매 후 30일 안에 전액 환불할 수 있습니다."
    ],
)
metric = AnswerRelevancyMetric(threshold=0.7)
result = evaluate([case], [metric])
```

독립 메트릭으로 `metric.measure(case)`를 실행한 뒤 `metric.score`,
`metric.reason`, `metric.is_successful()`을 확인할 수도 있습니다.

## 전체 추적이 포함된 평가

`observe()`로 컴포넌트를 계측하고 현재 span에 테스트 케이스를 연결하면
엔드투엔드와 컴포넌트 평가를 함께 수행할 수 있습니다.

```python
from deepeval.metrics import TaskCompletionMetric
from deepeval.test_case import LLMTestCase
from deepeval.tracing import observe, update_current_span


@observe()
def retrieve_and_answer(user_input: str) -> str:
    output = "검색 결과를 사용한 답변"
    update_current_span(
        test_case=LLMTestCase(input=user_input, actual_output=output)
    )
    return output


for golden in dataset.evals_iterator(metrics=[TaskCompletionMetric()]):
    retrieve_and_answer(golden.input)
```

프레임워크별 wrapper나 callback을 사용하면 OpenAI·Anthropic 호출,
LangChain·LangGraph 실행, CrewAI·AgentCore·LlamaIndex 에이전트의
trace에 평가를 연결할 수 있습니다.

## 운영 시 권장 사항

- 작은 대표 데이터셋으로 시작하고 실패 사례를 지속적으로 추가합니다.
- LLM 판정만 사용하지 말고 exact match, JSON schema, 금칙어 검사 같은
  결정론적 메트릭을 함께 둡니다.
- 판정 모델·프롬프트·temperature·DeepEval 버전을 기록해 재현성을
  높입니다.
- 점수 하나만 보지 말고 `reason`과 실패 샘플을 검토합니다.
- 모델 호출 비용과 지연을 줄이려면 캐시, 비동기 동시성 제한, 샘플링을
  사용합니다.
- 실제 개인정보나 비밀키를 평가 데이터·trace·클라우드 보고서에 넣지
  않습니다.
- CI에는 안정적인 회귀 게이트를, 실험 환경에는 더 넓고 비용이 큰
  평가를 배치합니다.

## 저장소 구조

- `deepeval/metrics/`: 내장·커뮤니티 메트릭
- `deepeval/test_case/`: 단일 턴, 대화, arena 테스트 케이스
- `deepeval/evaluate/`: 동기·비동기 평가 실행기와 설정
- `deepeval/dataset/`: golden과 평가 데이터셋 관리
- `deepeval/tracing/`: span·trace 계측과 오프라인 평가
- `deepeval/benchmarks/`: 표준 LLM 벤치마크
- `deepeval/red_teaming/`: 공격 시나리오와 안전성 평가
- `deepeval/integrations/`: 외부 프레임워크 연결
- `tests/`: core, metrics, integrations 테스트
- `examples/`: 공식 예제와 노트북
- `typescript/`: TypeScript 구현

## 더 깊이 학습하기

한국어 가이드에는 설치부터 사용자 정의 메트릭, RAG 회귀 테스트,
CI/CD, 비용·보안·확장 설계까지 단계별 설명과 실행 가능한 예제가
있습니다.

1. [가이드 시작점](guide/README.md)
2. [설치와 첫 평가](guide/01_getting_started.md)
3. [핵심 개념과 RAG 평가](guide/02_core_concepts.md)
4. [고급 운영과 확장](guide/03_advanced.md)
5. [실습 예제](guide/examples/README.md)

## 기여

개발 환경은 가상환경과 Poetry를 권장합니다. 새 커뮤니티 메트릭은
`deepeval/metrics/community/` 아래에서 시작하고, 기존 메트릭의
폴더·schema·template 구조를 따르며 테스트와 문서를 함께 추가합니다.
자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 읽으세요.

## 로드맵과 라이선스

DeepEval은 Confident AI 통합, G-Eval, RAG·대화 메트릭, 데이터셋 생성,
레드티밍을 제공합니다. DAG 사용자 정의 메트릭과 guardrail 관련 항목은
원본 로드맵에서 진행 중으로 표시되어 있으므로 최신 상태는
[원본 README](README.md)를 확인하세요.

이 프로젝트는 [Apache License 2.0](LICENSE.md)으로 배포됩니다.
