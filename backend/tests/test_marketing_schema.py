from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]


class MarketingSchemaTest(unittest.TestCase):
    def test_marketing_migration(self) -> None:
        """Check marketing migration.
        Args:
            None (None): No arguments are required."""
        migration = ROOT_DIR / 'alembic' / 'versions' / '20260516_0017_create_extended_marketing_sources.py'
        content = migration.read_text(encoding='utf-8')
        for table_name in [
            'dim_audience_segment',
            'dim_keyword',
            'dim_page',
            'fact_audience_demographics_daily',
            'fact_organic_keyword_daily',
            'fact_paid_keyword_daily',
            'fact_top_page_daily',
            'fact_ad_creative_daily',
            'fact_referring_domain_daily',
            'business_assumptions',
            'campaigns',
            'campaign_performance_daily',
        ]:
            self.assertIn(table_name, content)

    def test_marketing_routes(self) -> None:
        """Check marketing routes.
        Args:
            None (None): No arguments are required."""
        routes = (ROOT_DIR / 'app' / 'api' / 'routes' / 'marketing.py').read_text(encoding='utf-8')
        for route_text in [
            '/audience/summary',
            '/countries/{country_id}/audience-fit',
            '/seo/keywords',
            '/seo/opportunity',
            '/seo/top-pages',
            '/ppc/keywords',
            '/ppc/opportunity',
            '/ppc/cpc-summary',
            '/ads/creatives',
            '/ads/summary',
            '/backlinks/referring-domains',
            '/backlinks/opportunity',
            '/business-assumptions',
            '/campaigns',
            '/campaigns/{campaign_id}/performance',
            '/campaigns/{campaign_id}/performance/upload',
        ]:
            self.assertIn(route_text, routes)

    def test_report_detector(self) -> None:
        """Check report detector.
        Args:
            None (None): No arguments are required."""
        detector = (ROOT_DIR / 'app' / 'services' / 'report_detector.py').read_text(encoding='utf-8')
        for report_type in [
            'audience_demographics_daily',
            'organic_keywords_daily',
            'paid_keywords_daily',
            'top_pages_daily',
            'ads_creatives_daily',
            'backlinks_daily',
            'referring_domains_daily',
        ]:
            self.assertIn(report_type, detector)

    def test_mas_tools(self) -> None:
        """Check MAS tools.
        Args:
            None (None): No arguments are required."""
        registry = (ROOT_DIR / 'app' / 'services' / 'mas_tool_registry_service.py').read_text(encoding='utf-8')
        for tool_name in [
            'get_audience_summary',
            'get_audience_fit_score',
            'get_organic_keywords',
            'get_seo_opportunity',
            'get_paid_keywords',
            'get_ppc_opportunity',
            'get_top_pages',
            'get_ads_creatives',
            'get_referring_domains',
            'get_backlink_opportunity',
            'get_business_assumptions',
            'get_campaign_performance',
        ]:
            self.assertIn(tool_name, registry)


if __name__ == '__main__':
    unittest.main()
