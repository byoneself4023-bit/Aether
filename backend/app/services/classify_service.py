"""
분류 서비스 — 비즈니스 로직
"""
from loguru import logger

from app.resources.registry import registry
from app.core.exceptions import ClassificationError, ResourceNotReadyError


class ClassifyService:
    def classify_domain(self, text: str) -> dict:
        """도메인 분류"""
        try:
            result = registry.domain_classifier.predict(text)
            logger.info(f"분류 완료: '{text[:30]}...' → {result['domain']} ({result['confidence']:.1%})")
            return result
        except ResourceNotReadyError:
            raise
        except Exception as e:
            logger.error(f"분류 실패: {e}")
            raise ClassificationError(f"분류 중 오류 발생: {str(e)}")

    def classify_batch(self, texts: list[str]) -> list[dict]:
        """배치 도메인 분류"""
        try:
            results = registry.domain_classifier.predict_batch(texts)
            logger.info(f"배치 분류 완료: {len(results)}건")
            return results
        except ResourceNotReadyError:
            raise
        except Exception as e:
            logger.error(f"배치 분류 실패: {e}")
            raise ClassificationError(f"분류 중 오류 발생: {str(e)}")

    def classify_full(self, text: str) -> dict:
        """domain + category 2-level 분류"""
        result = self.classify_domain(text)

        # category 분류 (모델 배치됐을 때만)
        try:
            cat_clf = registry.category_classifier
            if cat_clf.available:
                cat_result = cat_clf.predict(text)
                result["category"] = cat_result["category"]
                result["category_id"] = cat_result["category_id"]
                result["category_confidence"] = cat_result["confidence"]
                logger.info(f"카테고리 분류: {cat_result['category']} ({cat_result['confidence']:.1%})")
        except Exception as e:
            logger.debug(f"카테고리 분류 스킵: {e}")

        return result

    def get_domain_labels(self) -> dict:
        """도메인 레이블 목록"""
        mapping = registry.domain_classifier.label_mapping
        return {"labels": mapping, "count": len(mapping)}

    def classify_category(self, text: str) -> dict:
        """카테고리 분류"""
        cat_clf = registry.category_classifier
        if not cat_clf.available:
            raise ResourceNotReadyError("카테고리 분류 모델")
        try:
            result = cat_clf.predict(text)
            logger.info(f"카테고리 분류 완료: '{text[:30]}...' → {result['category']} ({result['confidence']:.1%})")
            return result
        except ResourceNotReadyError:
            raise
        except Exception as e:
            logger.error(f"카테고리 분류 실패: {e}")
            raise ClassificationError(f"카테고리 분류 중 오류 발생: {str(e)}")

    def get_category_labels(self) -> dict:
        """카테고리 레이블 목록"""
        cat_clf = registry.category_classifier
        if not cat_clf.available:
            raise ResourceNotReadyError("카테고리 분류 모델")
        mapping = cat_clf.label_mapping
        return {"labels": mapping, "count": len(mapping)}
