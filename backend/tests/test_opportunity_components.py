from datetime import date
import unittest

from app.schemas.channel import ChannelMetric, ChannelPeriod, ChannelScope, ChannelSummaryMetrics, ChannelSummaryResponse
from app.schemas.country import CountryMetricValues, MetricLeader
from app.services.opportunity_component_service import channel_score, localization_score, quality_score, traffic_score


class OpportunityComponentTest(unittest.TestCase):
    def test_weighted_quality(self) -> None:
        """Validate weighted quality score.
        Args:
            self (OpportunityComponentTest): Test case instance."""
        metrics = CountryMetricValues(
            total_competitor_traffic=1000,
            active_competitors_count=3,
            leader=MetricLeader(),
            leader_share=0.2,
            top_3_share=0.5,
            market_concentration_hhi=0.2,
            desktop_share=0.4,
            mobile_share=0.6,
            bounce_share=0.3,
            no_bounce_share=0.7,
            engagement_score=0.8,
            market_volatility_score=0.2,
        )
        score = quality_score(metrics)
        self.assertAlmostEqual(score, 0.76)

    def test_percentile_traffic(self) -> None:
        """Validate percentile traffic score.
        Args:
            self (OpportunityComponentTest): Test case instance."""
        metrics = CountryMetricValues(
            total_competitor_traffic=1000,
            active_competitors_count=3,
            leader=MetricLeader(),
            no_bounce_share=0.5,
        )
        score = traffic_score(metrics, 0.8)
        self.assertAlmostEqual(score, 0.71)

    def test_mobile_localization(self) -> None:
        """Validate mobile localization score.
        Args:
            self (OpportunityComponentTest): Test case instance."""
        metrics = CountryMetricValues(
            total_competitor_traffic=1000,
            active_competitors_count=3,
            leader=MetricLeader(),
            bounce_share=0.4,
            mobile_share=0.6,
        )
        score = localization_score(metrics, 0.8)
        self.assertAlmostEqual(score, 0.64)

    def test_mobile_baseline_localization(self) -> None:
        """Validate mobile baseline score.
        Args:
            self (OpportunityComponentTest): Test case instance."""
        metrics = CountryMetricValues(
            total_competitor_traffic=1000,
            active_competitors_count=3,
            leader=MetricLeader(),
            bounce_share=0.4,
            mobile_share=0.4,
        )
        score = localization_score(metrics, 0.8)
        self.assertAlmostEqual(score, 0.58)

    def test_channel_traffic_penalty(self) -> None:
        """Validate low traffic channel penalty.
        Args:
            self (OpportunityComponentTest): Test case instance."""
        summary = ChannelSummaryResponse(
            scope=ChannelScope(scope_type='country'),
            period=ChannelPeriod(date_from=date(2026, 1, 1), date_to=date(2026, 1, 31), days_count=31),
            summary=ChannelSummaryMetrics(channel_dependency_score=0.6),
            channels=[
                ChannelMetric(
                    channel_id=1,
                    channel_code='paid',
                    channel_name='Paid',
                    traffic_share=0.2,
                    interpretation='Test metric.',
                ),
                ChannelMetric(
                    channel_id=2,
                    channel_code='referral',
                    channel_name='Referral',
                    traffic_share=0.2,
                    interpretation='Test metric.',
                ),
                ChannelMetric(
                    channel_id=3,
                    channel_code='social',
                    channel_name='Social',
                    traffic_share=0.1,
                    interpretation='Test metric.',
                ),
            ],
            warnings=[],
            recommendation_hints=[],
        )
        score = channel_score(summary, 0.3)
        self.assertAlmostEqual(score, 0.61)


if __name__ == '__main__':
    unittest.main()
