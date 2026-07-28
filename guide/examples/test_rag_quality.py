"""LLM 판정자를 사용하는 RAG 품질 회귀 테스트.

실행:
    deepeval test run guide/examples/test_rag_quality.py

기본 판정 모델을 사용할 때 OPENAI_API_KEY가 필요합니다.
"""

from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase


def test_return_shipping_policy() -> None:
    """검색 근거를 지키면서 질문에 직접 답하는지 검증합니다."""
    case = LLMTestCase(
        name="return-shipping-policy-ko",
        input="반품 배송비는 누가 내나요?",
        actual_output=(
            "단순 변심이면 고객이 부담하고, 상품 불량이나 오배송이면 "
            "판매자가 부담합니다."
        ),
        expected_output=(
            "구매자 변심은 구매자 부담, 상품 하자나 오배송은 판매자 "
            "부담입니다."
        ),
        retrieval_context=[
            "단순 변심으로 반품할 때 왕복 배송비는 구매자가 부담합니다.",
            "상품 불량 또는 오배송의 반품 배송비는 판매자가 부담합니다.",
        ],
        metadata={"locale": "ko", "domain": "returns"},
        tags=["rag", "regression", "korean"],
    )

    metrics = [
        FaithfulnessMetric(threshold=0.8),
        AnswerRelevancyMetric(threshold=0.7),
    ]
    assert_test(case, metrics)
