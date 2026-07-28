"""API 키 없이 DeepEval 사용자 정의 메트릭을 실행하는 최소 예제.

실행:
    python guide/examples/offline_keyword_metric.py
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class KeywordCoverageMetric(BaseMetric):
    """응답에 필수 핵심어가 얼마나 포함됐는지 측정합니다."""

    def __init__(
        self,
        required_keywords: Sequence[str],
        threshold: float = 0.75,
    ) -> None:
        if not required_keywords:
            raise ValueError("required_keywords에는 한 개 이상의 값이 필요합니다.")
        self.required_keywords = tuple(
            keyword.casefold() for keyword in required_keywords
        )
        self.threshold = threshold
        self.score = None
        self.reason = None
        self.success = None
        self.error = None
        self.async_mode = True
        self.strict_mode = False
        self.include_reason = True
        self.evaluation_model = "deterministic-keyword-check"

    @property
    def __name__(self) -> str:
        return "Keyword Coverage"

    def measure(
        self,
        test_case: LLMTestCase,
        *args: object,
        **kwargs: object,
    ) -> float:
        output = (test_case.actual_output or "").casefold()
        matched = [
            keyword for keyword in self.required_keywords if keyword in output
        ]
        missing = [
            keyword
            for keyword in self.required_keywords
            if keyword not in output
        ]
        self.score = len(matched) / len(self.required_keywords)
        self.reason = (
            f"포함: {matched or ['없음']}; 누락: {missing or ['없음']}"
        )
        self.success = self.is_successful()
        return self.score

    async def a_measure(
        self,
        test_case: LLMTestCase,
        *args: object,
        **kwargs: object,
    ) -> float:
        # 계산이 가벼워 별도 thread가 필요 없지만 DeepEval의 비동기
        # 실행 계약을 만족하도록 같은 결정론적 로직을 호출합니다.
        return self.measure(test_case, *args, **kwargs)


def main() -> None:
    case = LLMTestCase(
        input="반품 조건을 알려 주세요.",
        actual_output=(
            "구매 후 30일 이내이며, 단순 변심의 배송비는 고객 부담입니다."
        ),
        expected_output=(
            "30일 이내 반품할 수 있고 단순 변심 배송비는 고객이 부담합니다."
        ),
    )
    metric = KeywordCoverageMetric(
        required_keywords=["30일", "배송비", "고객"],
        threshold=0.75,
    )

    score = asyncio.run(metric.a_measure(case))
    status = "PASS" if metric.is_successful() else "FAIL"
    print(
        f"{status} | score={score:.3f} | "
        f"threshold={metric.threshold:.3f}"
    )
    print(metric.reason)

    if not metric.is_successful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
