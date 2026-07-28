# 02. 핵심 개념과 RAG 평가

## 1. 평가 단위를 먼저 정의하기

평가는 세 계층으로 나누면 설계가 선명해집니다.

- **컴포넌트**: query rewrite, retrieval, reranker, tool selection
- **엔드투엔드**: 사용자의 입력에서 최종 응답까지
- **운영**: 품질과 함께 지연, 비용, 오류율, 안전성 추세

엔드투엔드 점수가 낮아도 어느 컴포넌트가 문제인지 모르면 수정하기
어렵습니다. 반대로 컴포넌트 점수만 좋아도 최종 사용자 경험이 좋다는
보장은 없습니다. 두 계층을 함께 측정하세요.

## 2. 좋은 평가 데이터셋

대표 데이터셋은 평균적인 질문만 모은 목록이 아닙니다.

1. 정상 경로: 가장 자주 발생하는 질문
2. 경계값: 날짜·금액·수량·정책 예외
3. 긴 꼬리: 드물지만 중요한 업무
4. 공격·오용: 프롬프트 인젝션, 권한 우회, 유해 요청
5. 과거 장애: 실제 실패를 재현하는 회귀 케이스
6. 거절 필요: 근거가 없거나 답하면 안 되는 입력

각 golden에는 입력뿐 아니라 기대 행동, 허용 가능한 변형, 근거 출처,
난이도, 도메인 tag를 기록합니다. train·prompt 개발용과 최종 평가용을
분리해 평가셋 과적합을 피하세요.

## 3. RAG 실패를 분해하기

```text
질문 → 검색 → 순위화 → 문맥 조립 → 생성 → 후처리
        │       │          │         │
      Recall  Precision   길이/중복  Faithfulness
```

- **Contextual Recall**이 낮음: 필요한 근거를 검색하지 못했습니다.
- **Contextual Precision**이 낮음: 관련 근거가 뒤에 묻혀 있습니다.
- **Contextual Relevancy**가 낮음: 무관한 문맥이 많습니다.
- **Faithfulness**가 낮음: 응답이 주어진 근거를 벗어났습니다.
- **Answer Relevancy**가 낮음: 근거와 맞더라도 질문에 직접 답하지
  않았습니다.

하나의 RAGAS 평균만 보면 서로 상쇄될 수 있으므로 개별 점수도
보존합니다.

## 4. 실제 RAG 평가

```python
from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

case = LLMTestCase(
    input="반품 배송비는 누가 내나요?",
    actual_output=(
        "단순 변심이면 고객이 부담하고, 상품 하자면 판매자가 부담합니다."
    ),
    expected_output=(
        "구매자 변심은 구매자 부담, 상품 불량은 판매자 부담입니다."
    ),
    retrieval_context=[
        "단순 변심으로 반품할 때 배송비는 구매자가 부담합니다.",
        "상품 불량 또는 오배송의 반품 배송비는 판매자가 부담합니다.",
    ],
)

evaluate(
    [case],
    [
        ContextualRecallMetric(threshold=0.7),
        ContextualPrecisionMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.8),
        AnswerRelevancyMetric(threshold=0.7),
    ],
)
```

이 코드는 기본 판정 모델을 호출하므로 키와 비용이 필요합니다. 먼저
`python -m guide.examples.offline_keyword_metric`으로 하네스가
동작하는지 확인한
뒤 LLM 메트릭을 추가하면 환경 문제와 평가 문제를 분리할 수 있습니다.

## 5. 결정론적 검사와 LLM 판정 결합

다음 항목은 가능한 한 코드로 먼저 검사합니다.

- JSON parsing과 schema
- 필수 citation 존재
- 허용된 URL domain
- 금지된 개인정보 패턴
- 수치 범위와 단위
- 도구 호출 이름·인자 타입

그 다음 의미적 정확성, 설명의 유용성, 복합 지시 준수처럼 규칙으로
표현하기 어려운 영역을 LLM 판정자에게 맡깁니다. 이 순서는 비용을 줄이고
실패 이유를 더 명확하게 만듭니다.

## 6. 임계값 보정

1. 도메인 전문가가 50~200개 표본을 통과/실패로 라벨링합니다.
2. 후보 메트릭 점수 분포와 사람 라벨의 혼동 행렬을 계산합니다.
3. 심각한 오답을 통과시키는 false positive 비용을 우선 고려합니다.
4. CI 차단용 임계값과 모니터링 경고 임계값을 분리합니다.
5. 판정 모델이나 prompt가 바뀌면 다시 보정합니다.

표본이 적을 때 소수점 셋째 자리 차이를 품질 개선으로 해석하지 마세요.
점수 평균과 함께 통과율, 신뢰구간, 실패 범주별 건수를 봅니다.

## 7. 에이전트와 대화 평가

에이전트 평가에는 최종 답변 외에도 궤적이 필요합니다.

- 의도한 목표와 완료 조건
- 호출 가능한 도구와 실제 호출
- 기대 도구·인자
- 계획과 실행 단계
- 불필요한 반복 또는 loop
- 권한 경계와 민감 작업 승인

대화 평가에서는 개별 턴을 독립 샘플로 잘라내지 말고
`ConversationalTestCase`로 맥락을 보존합니다. 개인 정보나 세션 secret은
평가용 trace에 넣기 전에 익명화하세요.

## 8. 결과 해석 체크리스트

- 점수가 낮은가, 실행 오류인가?
- 판정 이유가 입력·근거와 일치하는가?
- 동일 케이스를 사람이 같은 기준으로 판정할 수 있는가?
- 특정 언어·길이·고객군에서만 실패하는가?
- 모델 변경 효과인지 retrieval·prompt·데이터 변경 효과인지 분리했는가?
- 평균은 좋아졌지만 심각한 실패가 늘지는 않았는가?

다음: [고급 운영과 확장](03_advanced.md)
