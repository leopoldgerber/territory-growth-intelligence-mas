EMAIL_INPUT = 'email'
PASSWORD_INPUT = 'password'
FIRST_SEARCH_INPUT = '//*[@class="___SValue_12tss-red-team _size_l_12tss-red-team"]'
SEARCH_CLEAR_BUTTON = '//*[@class="srf-icon"]'
SEARCH_INPUT = '//*[@class="srf-searchbar__form__input js-searchbar-input"]'
DOMAIN_OVERVIEW_LINK = '//*[@id="srf-sidebar"]//div[contains(@class,"srf-report-sidebar-main__group js-sidebar-group")]//div[contains(@id,"accordion-content-seo")]//a[contains(@data-test,"seo_domain_overview")]'
TRAFFIC_ANALYTICS_LINK = '//*[@id="srf-sidebar"]//div[contains(@class,"srf-report-sidebar-main__group js-sidebar-group")]//div[contains(@id,"accordion-content-seo")]//a[contains(@data-test,"seo_traffic_analytics")]'
JOURNEY_TAB = '//*[@class="sc-1bc4zew-0 ccJnmu"]//div[contains(@class,"___STabLine_nxhjn_gg_ __underlined_nxhjn_gg_ _size_m_nxhjn_gg_")]//button[contains(@data-test,"reportTab journey")]'
GEO_TAB = '//*[@class="sc-1bc4zew-0 ccJnmu"]//div[contains(@class,"___STabLine_nxhjn_gg_ __underlined_nxhjn_gg_ _size_m_nxhjn_gg_")]//button[contains(@data-test,"reportTab geo")]'
MONTH_PICKER = '//a[@data-ui-name="MonthRangePicker.Trigger"]'
MONTH_APPLY = '//div[@data-ui-name="Dropdown.Popper"]//button[@data-test="selector-apply"]'
TRAFFIC_CHART_EXPORT = '//*[@id="chartOverviewVisitsHistory"]//*[@class="___SBoxInline_8om4t_gg_ ___SButton_1gip4_gg_ _size_m_1gip4_gg_ _size_m_wus9c_gg_ _theme_secondary-muted_1gip4_gg_"]'
TRAFFIC_CSV_OPTION = '//*[@class="___SContainer_6papi_gg_"]//div//div[contains(@class,"___SDropdownMenuItem_wus9c_gg_ _size_m_wus9c_gg_ ___SFlex_3onux_gg_")][2]'
VISITS_BUTTON = '//*[@id="chartOverviewVisitsHistory"]//*[@class="___SPills_b6lww_gg_ _size_m_b6lww_gg_"]//button[@value="visits"]'
USERS_BUTTON = '//*[@id="chartOverviewVisitsHistory"]//*[@class="___SPills_b6lww_gg_ _size_m_b6lww_gg_"]//button[@value="users"]'
DURATION_BUTTON = '//*[@id="chartOverviewVisitsHistory"]//*[@class="___SPills_b6lww_gg_ _size_m_b6lww_gg_"]//button[@value="time_on_site"]'
BOUNCE_BUTTON = '//*[@id="chartOverviewVisitsHistory"]//*[@class="___SPills_b6lww_gg_ _size_m_b6lww_gg_"]//button[@value="bounce_rate"]'
TRAFFIC_SOURCES_EXPORT = '//div[contains(@class,"sc-1h9cu94-0 hSKyfN")]//button[contains(@class, "___SBoxInline_8om4t_gg_ ___SButton_1gip4_gg_ _size_m_1gip4_gg_ _size_m_wus9c_gg_ _theme_secondary-muted_1gip4_gg_")]'
JOURNEY_CSV_BUTTON = '//button[contains(@data-test, "csv-button")]'
GEO_CSV_BUTTON = '//div[contains(@data-test,"geoDistributionList")]//button[contains(@class, "___SButton_1gip4_gg_ _size_m_1gip4_gg_ _theme_secondary-muted_1gip4_gg_")]'


def month_button(month_name: str, year: int) -> str:
    """Build month button selector.
    Args:
        month_name (str): Month name.
        year (int): Calendar year."""
    return f'//button[@aria-label="{month_name} 1, {year}"]'
