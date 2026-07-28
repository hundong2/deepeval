# 03. 고급 운영과 확장

## 1. 사용자 정의 메트릭

`BaseMetric` 구현에는 동기·비동기 측정, 점수, 이유, 임계값 판정이
필요합니다.

```python
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class NonEmptyMetric(BaseMetric):
    def __init__(self, threshold: float = 1.0):
        self.threshold = threshold
        self.score = None
        self.reason = None
        self.success = None
        self.error = None
        self.async_mode = True

    @property
    def __name__(self):
        return "Non Empty"

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        self.score = float(bool((test_case.actual_output or "").strip()))
        self.reason = "출력이 비어 있지 않은지 확인했습니다."
        self.success = self.is_successful()
        return self.score

    async def a_measure(
        self, test_case: LLMTestCase, *args, **kwargs
    ) -> float:
        return self.measure(test_case, *args, **kwargs)
```

실제 예제는
[offline_keyword_metric.py](examples/offline_keyword_metric.py)에 있습니다.
커뮤니티에 새 메트릭을 기여할 때는
`deepeval/metrics/community/`의 기존 폴더를 따라 class, `schema.py`,
`template.py`, export, 문서, 테스트를 함께 추가합니다.

## 2. 동시성·재시도·비용

`AsyncConfig(max_concurrent=N)`은 판정 요청 동시성을 제한합니다.
공급자의 rate limit, 요청당 token, 조직 quota에 맞춰 작은 값부터
늘리세요.

비용을 안정적으로 비교하려면:

- 동일한 평가셋 snapshot과 판정 모델 버전을 사용합니다.
- 응답과 판정 결과 캐시의 hit 여부를 기록합니다.
- 개발 중에는 계층별 대표 표본만, 야간에는 전체 평가셋을 실행합니다.
- 먼저 저비용 결정론적 검사로 실패를 거르고 LLM 판정을 실행합니다.
- 입력·출력 token과 `evaluation_cost`를 결과와 함께 보관합니다.

캐시는 오래된 판정을 숨길 수 있습니다. 메트릭 prompt나 판정 모델이
바뀌면 새 baseline을 만들고 캐시 무효화 정책을 명시하세요.

## 3. Trace 기반 컴포넌트 평가

`@observe()`로 함수를 span으로 만들고 `update_current_span()`으로
테스트 케이스를 연결할 수 있습니다. 외부 프레임워크는 wrapper 또는
callback 통합을 사용합니다.

좋은 trace는 다음 질문에 답해야 합니다.

- 어떤 prompt·model·retriever 버전이 사용됐는가?
- 어느 span에서 latency와 token이 늘었는가?
- 잘못된 최종 답변의 근거 문서와 도구 호출은 무엇인가?
- retry나 fallback이 품질을 회복했는가?

span에 원문 개인정보, 접근 token, 내부 시스템 prompt 전체를 무조건
저장하지 마세요. 최소 수집, 마스킹, 보존 기간, 접근 통제를 정합니다.

## 4. CI/CD 구성

평가를 세 계층으로 나누는 예:

| 계층 | 시점 | 범위 | 실패 처리 |
|---|---|---|---|
| PR smoke | 코드 변경마다 | 10~30개, 결정론적 중심 | 즉시 차단 |
| nightly | 매일 | 대표 전체셋, LLM judge | 경고·추세 |
| release gate | 배포 전 | 핵심 업무·안전성 | 승인 필요 |

GitHub Actions 개념 예:

```yaml
name: llm-eval
on: [pull_request]
jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -U deepeval
      - run: deepeval test run evals/test_smoke.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

실제 저장소에서는 action SHA 고정, 최소 권한, dependency lock, 결과
artifact 보존을 추가하세요. 외부 fork PR에는 secret이 노출되지 않도록
워크플로 트리거와 권한을 별도로 설계합니다.

## 5. 재현성과 회귀 분석

평가 실행마다 다음 정보를 남깁니다.

- 애플리케이션 commit SHA
- DeepEval 버전
- 생성 모델과 판정 모델의 정확한 식별자
- system prompt와 평가 criteria의 버전/hash
- 데이터셋 버전과 필터
- temperature, seed 등 생성 파라미터
- 실행 시각, 비용, 지연, 오류·retry 수

LLM 공급자의 고정되지 않은 model alias는 시간이 지나며 동작이 바뀔 수
있습니다. 가능하면 날짜·버전이 포함된 model ID를 사용하고, 바뀔 때
baseline을 재측정합니다.

## 6. 보안과 레드티밍

평가 시스템도 공격 표면입니다.

- 평가 데이터의 문서를 판정 prompt에 넣을 때 prompt injection을
  비신뢰 입력으로 취급합니다.
- 판정 모델이 입력의 명령을 따르지 않고 기준만 적용하도록 구조를
  분리합니다.
- production trace를 학습·평가에 재사용하기 전에 개인정보와 secret을
  제거합니다.
- 모델이 생성한 코드·도구 인자를 실제 운영 권한으로 실행하지 않습니다.
- 공격 성공률뿐 아니라 정상 요청 거부율도 함께 측정합니다.
- 테넌트별 데이터와 평가 보고서 접근 권한을 분리합니다.

레드팀 결과는 취약한 prompt 한 줄의 문제가 아니라 입력 필터, 권한,
도구 schema, 실행 sandbox, 출력 검사 전체의 방어 설계로 연결해야
합니다.

## 7. 성능과 확장

대규모 평가에서는 메트릭마다 필요한 필드를 미리 검증하고, 케이스를
도메인·언어·난이도별로 shard합니다. 공급자 장애와 rate limit을
품질 실패로 집계하지 말고 별도 오류 지표로 분리하세요.

컴포넌트 확장 지점:

- `metrics/`: 도메인 평가 기준
- `models/`, `model_integrations/`: 사용자 정의 판정 모델
- `integrations/`: 프레임워크 계측
- `dataset/`: 외부 golden 저장소 연동
- `tracing/`: span exporter와 오프라인 평가
- `benchmarks/`: 표준화된 task 묶음

## 8. 디버깅 체크리스트

- `python`과 `deepeval` 실행 파일이 같은 가상환경을 가리키는가?
- 작업 디렉터리가 달라 `.env.local`을 못 읽는 것은 아닌가?
- 선택한 메트릭의 필수 필드를 모두 넣었는가?
- 비동기 event loop를 중첩 실행하고 있지 않은가?
- rate limit과 timeout이 점수 0으로 잘못 처리되지 않았는가?
- 캐시가 이전 model·prompt 결과를 재사용하지 않는가?
- 다국어 케이스에서 판정 criteria가 언어별로 일관적인가?
- 평균만 보고 특정 안전성 실패를 놓치지 않았는가?

## 9. 다음 학습 경로

1. [예제 두 개](examples/README.md)를 실행하고 실패 케이스를 추가합니다.
2. 실제 서비스의 과거 장애 20개를 golden으로 만듭니다.
3. 결정론적 메트릭과 LLM 메트릭의 사람 라벨 일치율을 비교합니다.
4. retrieval과 generation 실패 대시보드를 분리합니다.
5. trace 기반 컴포넌트 평가와 release gate를 구축합니다.

가이드 시작점: [guide/README.md](README.md)
