"""
Module 10: Final Interview Report.

Numeric averages are computed deterministically here. The qualitative
strong_areas/weak_areas/final_recommendation come from QwenService, which
is given the computed averages so its narrative is grounded in real numbers
rather than re-deriving (and potentially miscalculating) them itself.
"""
from app.core.logging import get_logger
from app.schemas.interview import AnswerEvaluationResponse, FinalReportResponse
from app.services.qwen_service import QwenService

logger = get_logger(__name__)


class ReportAggregator:
    def __init__(self, qwen_service: QwenService | None = None) -> None:
        self._qwen = qwen_service or QwenService()

    async def build_final_report(
        self, evaluations: list[AnswerEvaluationResponse]
    ) -> FinalReportResponse:
        n = len(evaluations)

        technical_avg = sum(e.technical for e in evaluations) / n
        communication_avg = sum(e.communication for e in evaluations) / n
        confidence_avg = sum(e.confidence for e in evaluations) / n
        relevance_avg = sum(e.relevance for e in evaluations) / n
        completeness_avg = sum(e.completeness for e in evaluations) / n
        overall_avg = sum(e.overall for e in evaluations) / n

        averages = {
            "technical_average": round(technical_avg, 2),
            "communication_average": round(communication_avg, 2),
            "confidence_average": round(confidence_avg, 2),
            "relevance_average": round(relevance_avg, 2),
            "completeness_average": round(completeness_avg, 2),
            "overall_score": round(overall_avg, 2),
            "questions_answered": n,
        }

        eval_dicts = [e.model_dump() for e in evaluations]
        qualitative = await self._qwen.generate_final_report(eval_dicts, averages)

        report = FinalReportResponse(
            overall_score=averages["overall_score"],
            technical_average=averages["technical_average"],
            communication_average=averages["communication_average"],
            confidence_average=averages["confidence_average"],
            strong_areas=qualitative["strong_areas"],
            weak_areas=qualitative["weak_areas"],
            final_recommendation=qualitative["final_recommendation"],
        )

        logger.info("Final report built: overall_score=%.2f over %d answers", report.overall_score, n)
        return report
