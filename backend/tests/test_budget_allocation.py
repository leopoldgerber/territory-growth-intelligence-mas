from datetime import date
import unittest

from app.schemas.opportunity import OpportunityCalculation, OpportunityComponents, OpportunityScoreResponse, OpportunityScoreValues
from app.schemas.strategy import BudgetAssumptions
from app.services.budget_allocation_service import allocate_budget, goal_weights


class BudgetAllocationTest(unittest.TestCase):
    def test_brand_category(self) -> None:
        """Validate brand localization category.
        Args:
            self (BudgetAllocationTest): Test case instance."""
        opportunity = OpportunityScoreResponse(
            country={'country_id': 1, 'country_name_en': 'Test', 'has_data': True},
            period={'date_from': date(2026, 1, 1), 'date_to': date(2026, 1, 31), 'days_count': 31},
            score=OpportunityScoreValues(opportunity_score=0.7, recommended_priority='high', market_type='growth'),
            components=OpportunityComponents(),
            strengths=[],
            risks=[],
            explanation='Test score.',
            data_quality_status='passed',
            calculation=OpportunityCalculation(calculation_version='v1'),
        )
        allocation = allocate_budget(1000, 'brand_awareness', 'medium', BudgetAssumptions(), opportunity, None, 10000)
        category_codes = [item.channel_code for item in allocation]
        brand_item = next(item for item in allocation if item.channel_code == 'brand_localization')
        self.assertIn('brand_localization', category_codes)
        self.assertIsNone(brand_item.channel_id)
        self.assertEqual(goal_weights('brand_awareness')['brand_localization'], 0.25)


if __name__ == '__main__':
    unittest.main()
