# DeepEval 실습 예제

## 예제 1: API 키 없는 사용자 정의 메트릭

파일: [offline_keyword_metric.py](offline_keyword_metric.py)

학습 목표:

- `LLMTestCase`와 `BaseMetric`의 관계 이해
- `measure()`와 `a_measure()` 구현
- 점수·이유·임계값 판정
- 외부 모델 없이 평가 하네스 자체를 검증

저장소 루트에서:

```bash
python -m guide.examples.offline_keyword_metric
```

예상 결과:

```text
PASS | score=1.000 | threshold=0.750
```

이 예제는 핵심어 포함률만 측정하므로 의미적 정확성을 보장하지 않습니다.
빠르고 결정론적인 1차 gate 예제로 사용하세요.

## 예제 2: RAG 회귀 테스트

파일: [test_rag_quality.py](test_rag_quality.py)

학습 목표:

- 검색 문맥과 실제·기대 출력 구성
- Faithfulness와 Answer Relevancy의 역할 분리
- `deepeval test run`으로 CI 스타일 테스트 실행

환경변수를 준비한 뒤:

```powershell
$env:OPENAI_API_KEY="..."
deepeval test run guide/examples/test_rag_quality.py
```

```bash
export OPENAI_API_KEY="..."
deepeval test run guide/examples/test_rag_quality.py
```

기본 메트릭 모델을 쓰지 않는다면 공식 문서의 custom LLM 설정을 적용해
판정 모델을 주입하세요.

## 실습 과제

1. 오프라인 예제의 `required_keywords`에 존재하지 않는 단어를 추가해
   실패 결과와 `reason`을 확인합니다.
2. RAG 예제의 검색 문맥에서 반품 배송비 문장을 제거하고 Faithfulness와
   Answer Relevancy가 어떻게 달라지는지 비교합니다.
3. `metadata={"locale": "ko", "domain": "returns"}`와 tag를 넣어
   실패를 분류합니다.
4. 20개 케이스로 데이터셋을 확장하고 threshold별 통과율을 계산합니다.
5. 비용·지연을 기록하고 CI smoke와 nightly suite로 나눕니다.

상위 문서: [DeepEval 한국어 학습 가이드](../README.md)
