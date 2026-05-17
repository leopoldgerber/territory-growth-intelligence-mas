export type HealthStatus = {
  status: string;
  backend: string;
  database: string;
  app_name: string;
  environment: string;
};

export type ProjectAccess = {
  project_id: number;
  project_name: string;
  project_slug: string;
  role: string;
};

export type UserInfo = {
  user_id: number;
  email: string;
  full_name: string | null;
  status: string;
  is_superadmin: boolean;
  projects: ProjectAccess[];
};

export type AuthResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserInfo;
};

export type JobQueuedResponse = {
  job_id: string;
  status: string;
  message: string;
  related_entity_type: string | null;
  related_entity_id: number | null;
};

export type JobItem = {
  job_id: string;
  job_type: string;
  status: string;
  project_id: number | null;
  user_id: number | null;
  related_entity_type: string | null;
  related_entity_id: number | null;
  progress_percent: number;
  current_step: string | null;
  result_payload: Record<string, unknown> | null;
  error_message: string | null;
  celery_task_id: string | null;
  created_at: string | null;
  started_at: string | null;
  finished_at: string | null;
  updated_at: string | null;
};

export type JobList = {
  items: JobItem[];
  total: number;
};

export type JobEventItem = {
  event_id: number;
  job_id: string;
  event_type: string;
  step_name: string | null;
  message: string | null;
  progress_percent: number | null;
  event_payload: Record<string, unknown> | null;
  created_at: string | null;
};

export type JobEventList = {
  items: JobEventItem[];
  total: number;
};

export type ProjectItem = {
  project_id: number;
  project_name: string;
  project_slug: string;
  description: string | null;
  own_company_id: number | null;
  default_currency_code: string;
  status: string;
  role: string | null;
};

export type ProjectList = {
  items: ProjectItem[];
  total: number;
};

export type ProjectMemberItem = {
  user_id: number;
  email: string;
  full_name: string | null;
  role: string;
  status: string;
};

export type ProjectMemberList = {
  items: ProjectMemberItem[];
  total: number;
};

export type ProjectCompetitorItem = {
  domain_id: number;
  domain: string | null;
  company_id: number | null;
  company_name: string | null;
  competitor_tier: string;
  priority: string;
  notes: string | null;
  is_active: boolean;
};

export type ProjectCompetitorList = {
  items: ProjectCompetitorItem[];
  total: number;
};

export type ProjectCountryItem = {
  country_id: number;
  country_name_en: string | null;
  country_name_ru: string | null;
  region_name_en: string | null;
  status: string;
  strategic_priority: string;
  notes: string | null;
};

export type ProjectCountryList = {
  items: ProjectCountryItem[];
  total: number;
};

export type UpdateScheduleItem = {
  schedule_id: number;
  project_id: number | null;
  schedule_name: string;
  update_type: string;
  frequency: string;
  cron_expression: string | null;
  timezone: string;
  is_active: boolean;
  lookback_days: number;
  default_granularity: string;
  config: Record<string, unknown> | null;
  next_run_at: string | null;
  last_run_at: string | null;
  last_run_status: string | null;
  created_at: string | null;
};

export type UpdateScheduleList = {
  items: UpdateScheduleItem[];
  total: number;
};

export type UpdateRunQueued = {
  update_run_id: number;
  job_id: string;
  status: string;
};

export type UpdateRunItem = {
  update_run_id: number;
  schedule_id: number | null;
  project_id: number | null;
  job_id: string | null;
  ingestion_run_id: number | null;
  run_type: string;
  status: string;
  period_start: string | null;
  period_end: string | null;
  started_at: string | null;
  finished_at: string | null;
  files_imported_count: number;
  rows_loaded_count: number;
  quality_status: string;
  metrics_recalculated: boolean;
  scores_recalculated: boolean;
  alerts_detected_count: number;
  error_message: string | null;
  result_payload: Record<string, unknown> | null;
  created_at: string | null;
};

export type UpdateRunList = {
  items: UpdateRunItem[];
  total: number;
};

export type UpdateRunStepItem = {
  update_run_step_id: number;
  update_run_id: number;
  step_order: number;
  step_name: string;
  step_status: string;
  started_at: string | null;
  finished_at: string | null;
  message: string | null;
  details: Record<string, unknown> | null;
};

export type UpdateRunStepList = {
  items: UpdateRunStepItem[];
  total: number;
};

export type UpdateLatestStatus = {
  project_id: number | null;
  last_successful_update_at: string | null;
  last_update_status: string | null;
  latest_data_period: {
    date_from: string | null;
    date_to: string | null;
  };
  quality_status: string;
  alerts_detected_count: number;
  data_freshness_status: string;
};

export type AlertCountry = {
  country_id: number | null;
  country_name_en: string | null;
  country_name_ru: string | null;
};

export type AlertCompetitor = {
  domain_id: number | null;
  domain: string | null;
  company_id: number | null;
  company_name: string | null;
};

export type AlertChannel = {
  channel_id: number | null;
  channel_code: string | null;
  channel_name: string | null;
};

export type AlertItem = {
  anomaly_id: number;
  event_type: string;
  event_category: string | null;
  event_date: string;
  severity: string | null;
  status: string;
  country: AlertCountry | null;
  competitor: AlertCompetitor | null;
  channel: AlertChannel | null;
  title: string;
  description: string | null;
  recommendation_hint: string | null;
  relative_change: number | null;
  created_at: string | null;
};

export type AlertDetail = AlertItem & {
  metric_name: string | null;
  previous_value: number | null;
  current_value: number | null;
  absolute_change: number | null;
  baseline_value: number | null;
  threshold_value: number | null;
  evidence: Record<string, unknown> | null;
  calculation_version: string | null;
  data_quality_status: string | null;
  detected_at: string | null;
  updated_at: string | null;
};

export type AlertList = {
  items: AlertItem[];
  total: number;
};

export type AlertSummary = {
  total_new: number;
  critical: number;
  high: number;
  medium: number;
  by_category: Record<string, number>;
};

export type AlertDetectRequest = {
  date_from: string;
  date_to: string;
  country_id: number | null;
  domain_id: number | null;
  calculation_version: string;
};

export type AlertDetectResponse = {
  status: string;
  detected_events: number;
  created_events: number;
  duplicates_skipped: number;
};

export type AlertFilters = {
  countryId: string;
  domainId: string;
  channelId: string;
  eventType: string;
  eventCategory: string;
  severity: string;
  status: string;
  dateFrom: string;
  dateTo: string;
};

export type WorkflowOptions = {
  countries: CountryItem[];
  campaign_goals: string[];
  risk_appetites: string[];
  currencies: string[];
  latest_data_quality_status: string | null;
};

export type WorkflowRequest = {
  project_id?: number | null;
  country_id: number;
  date_from: string;
  date_to: string;
  budget_amount: number | null;
  currency_code: string;
  campaign_goal: string;
  risk_appetite: string;
  user_query: string | null;
  save_result: boolean;
  calculation_version: string;
};

export type WorkflowResponse = {
  project_id: number | null;
  workflow_run_id: number;
  agent_run_id: number | null;
  report_id: number | null;
  strategy_id: number | null;
  summary_id: number | null;
  status: string;
  final_answer: string | null;
  recommendations: MASRecommendationItem[];
  budget_allocation: BudgetAllocationItem[];
  evidence: MASEvidenceItem[];
  steps: MASStepItem[];
  saved: boolean;
  warnings: string[];
};

export type WorkflowRunItem = {
  workflow_run_id: number;
  project_id: number | null;
  workflow_type: string;
  status: string;
  country_id: number | null;
  country_name_en: string | null;
  period_start: string | null;
  period_end: string | null;
  budget_amount: number | null;
  currency_code: string | null;
  campaign_goal: string | null;
  risk_appetite: string | null;
  agent_run_id: number | null;
  report_id: number | null;
  strategy_id: number | null;
  summary_id: number | null;
  final_answer: string | null;
  error_message: string | null;
  created_at: string | null;
};

export type WorkflowRunList = {
  items: WorkflowRunItem[];
  total: number;
};

export type WorkflowRunDetail = WorkflowRunItem & {
  input_params: Record<string, unknown> | null;
  result_payload: WorkflowResponse | null;
  mas_run: MASRunResponse | null;
};

export type UploadFileResult = {
  file_id: number | null;
  file_name: string;
  report_type: string;
  status: string;
  row_count: number;
  errors: string[];
  warnings: string[];
};

export type QualitySummary = {
  total_checks: number;
  passed: number;
  warnings: number;
  failed: number;
};

export type QualityCheck = {
  check_id: number;
  file_name: string | null;
  table_name: string | null;
  check_name: string;
  check_type: string | null;
  status: string | null;
  severity: string | null;
  message: string | null;
  affected_rows_count: number | null;
  quality_dimension: string | null;
};

export type QualityResult = {
  run_id: number;
  quality_status: string;
  summary: QualitySummary;
  checks: QualityCheck[];
};

export type QualityRunSummary = {
  run_id: number;
  started_at: string | null;
  status: string | null;
  quality_status: string | null;
  total_checks: number;
  failed: number;
  warnings: number;
};

export type UploadRunResult = {
  run_id: number;
  status: string;
  quality_status: string;
  quality_summary: QualitySummary | null;
  row_count: number;
  files: UploadFileResult[];
  errors: string[];
  warnings: string[];
};

export type UploadRunSummary = {
  run_id: number;
  source_name: string | null;
  run_type: string | null;
  granularity: string | null;
  status: string | null;
  quality_status: string | null;
  row_count: number;
  started_at: string | null;
  finished_at: string | null;
  error_message: string | null;
};

export type UploadRunDetail = UploadRunSummary & {
  files: UploadFileResult[];
};

export type UploadOptions = {
  sourceName: string;
  isSynthetic: boolean;
  granularity: string;
  periodStart: string;
  periodEnd: string;
};

export type CountryItem = {
  country_id: number;
  country_name_en: string;
  country_name_ru: string | null;
  region_name_en: string | null;
  region_name_ru: string | null;
  has_data: boolean;
};

export type CountryList = {
  items: CountryItem[];
  total: number;
};

export type CountryPeriod = {
  country_id: number;
  date_min: string | null;
  date_max: string | null;
  available_days: number;
};

export type CountrySummaryMetrics = {
  total_competitor_traffic: number;
  active_competitors_count: number;
  leader_domain: string | null;
  leader_company: string | null;
  leader_traffic: number | null;
  leader_share: number | null;
  top_3_share: number | null;
  desktop_traffic: number | null;
  mobile_traffic: number | null;
  desktop_share: number | null;
  mobile_share: number | null;
  traffic_no_bounce: number | null;
  traffic_bounce: number | null;
  no_bounce_share: number | null;
  bounce_share: number | null;
  avg_bounce_rate: number | null;
  avg_pages_per_visit: number | null;
  avg_visit_duration_seconds: number | null;
};

export type TopCompetitorItem = {
  rank: number;
  domain_id: number;
  domain: string;
  company_id: number | null;
  company_name: string | null;
  traffic: number;
  traffic_share: number | null;
  desktop_traffic: number | null;
  mobile_traffic: number | null;
  desktop_share: number | null;
  mobile_share: number | null;
  bounce_rate: number | null;
  traffic_no_bounce: number | null;
  traffic_bounce: number | null;
  no_bounce_share: number | null;
};

export type DailyTrendItem = {
  date: string;
  traffic: number;
  desktop_traffic: number | null;
  mobile_traffic: number | null;
  traffic_no_bounce: number | null;
  traffic_bounce: number | null;
};

export type CountrySummary = {
  country: CountryItem;
  period: {
    date_from: string;
    date_to: string;
    days_count: number;
  };
  summary: CountrySummaryMetrics;
  top_competitors: TopCompetitorItem[];
  daily_trend: DailyTrendItem[];
  generated_summary: string;
  quality_warning: string | null;
};

export type MetricLeader = {
  domain_id: number | null;
  domain: string | null;
  company_id: number | null;
  company_name: string | null;
  traffic: number | null;
  share: number | null;
};

export type CountryMetricValues = {
  total_competitor_traffic: number | null;
  active_competitors_count: number | null;
  leader: MetricLeader | null;
  leader_share: number | null;
  top_3_share: number | null;
  market_concentration_hhi: number | null;
  desktop_share: number | null;
  mobile_share: number | null;
  bounce_share: number | null;
  no_bounce_share: number | null;
  avg_bounce_rate: number | null;
  avg_pages_per_visit: number | null;
  avg_visit_duration_seconds: number | null;
  engagement_score: number | null;
  market_volatility_score: number | null;
};

export type CountryMetricsResponse = {
  country: CountryItem;
  period: {
    date_from: string;
    date_to: string;
    days_count: number;
  };
  metrics: CountryMetricValues;
  calculation: {
    calculation_version: string;
    calculated_at: string | null;
    data_quality_status: string | null;
  };
  warning: string | null;
};

export type DailyMetricItem = {
  date: string;
  total_competitor_traffic: number | null;
  active_competitors_count: number | null;
  leader_share: number | null;
  top_3_share: number | null;
  market_concentration_hhi: number | null;
  engagement_score: number | null;
  market_volatility_score: number | null;
};

export type DailyMetricsResponse = {
  country_id: number;
  items: DailyMetricItem[];
};

export type CountryReportRequest = {
  country_id: number;
  date_from: string;
  date_to: string;
  limit_competitors: number;
  include_channels: boolean;
  include_recommendations: boolean;
  calculation_version: string;
};

export type ReportResponse = {
  report_id: number;
  report_type: string;
  status: string;
  title: string;
  country: CountryItem | null;
  period: {
    date_from: string;
    date_to: string;
    days_count: number;
  } | null;
  data_quality_status: string | null;
  report_markdown: string | null;
  report_json: Record<string, unknown> | null;
  created_at: string | null;
};

export type ReportListItem = {
  report_id: number;
  report_type: string;
  title: string;
  report_status: string | null;
  country_name_en: string | null;
  period_start: string;
  period_end: string;
  data_quality_status: string | null;
  created_at: string | null;
};

export type ReportList = {
  items: ReportListItem[];
  total: number;
};

export type CompetitorItem = {
  domain_id: number;
  domain: string;
  company_id: number | null;
  company_name: string | null;
  has_data: boolean;
};

export type CompetitorList = {
  items: CompetitorItem[];
  total: number;
};

export type CompetitorPeriod = {
  domain_id: number;
  domain: string;
  date_min: string | null;
  date_max: string | null;
  available_days: number;
};

export type CompetitorSummaryMetrics = {
  total_traffic: number;
  active_countries_count: number;
  top_country: string | null;
  top_country_traffic: number | null;
  top_country_share: number | null;
  desktop_traffic: number | null;
  mobile_traffic: number | null;
  desktop_share: number | null;
  mobile_share: number | null;
  traffic_no_bounce: number | null;
  traffic_bounce: number | null;
  no_bounce_share: number | null;
  bounce_share: number | null;
  avg_bounce_rate: number | null;
  avg_pages_per_visit: number | null;
  avg_visit_duration_seconds: number | null;
};

export type CompetitorCountryItem = {
  rank: number;
  country_id: number;
  country_name_en: string;
  country_name_ru: string | null;
  region_name_en: string | null;
  traffic: number;
  traffic_share_in_domain: number | null;
  growth_rate: number | null;
  presence_stability_score: number | null;
  desktop_share: number | null;
  mobile_share: number | null;
  bounce_rate: number | null;
  no_bounce_share: number | null;
  country_role: string;
  quality_label: string;
  signal: string | null;
};

export type CompetitorSignalSet = {
  anchor_countries: CompetitorCountryItem[];
  peripheral_countries: CompetitorCountryItem[];
  growing_countries: CompetitorCountryItem[];
  declining_countries: CompetitorCountryItem[];
  new_market_signals: CompetitorCountryItem[];
  abandoned_market_signals: CompetitorCountryItem[];
};

export type CompetitorDailyTrend = {
  date: string;
  traffic: number;
  desktop_traffic: number | null;
  mobile_traffic: number | null;
  traffic_no_bounce: number | null;
  traffic_bounce: number | null;
};

export type CompetitorSummary = {
  competitor: CompetitorItem;
  period: {
    date_from: string;
    date_to: string;
    days_count: number;
  };
  summary: CompetitorSummaryMetrics;
  top_countries: CompetitorCountryItem[];
  signals: CompetitorSignalSet;
  daily_trend: CompetitorDailyTrend[];
  generated_summary: string;
  quality_warning: string | null;
};

export type ChannelScope = {
  scope_type: string;
  country_id: number | null;
  country_name_en: string | null;
  domain_id: number | null;
  domain: string | null;
  company_id: number | null;
  company_name: string | null;
  is_estimated: boolean;
};

export type DominantChannel = {
  channel_id: number | null;
  channel_code: string | null;
  channel_name: string | null;
  traffic: number | null;
  traffic_share: number | null;
};

export type ChannelMetric = {
  channel_id: number;
  channel_code: string;
  channel_name: string;
  traffic: number;
  traffic_share: number | null;
  growth_rate: number | null;
  stability_score: number | null;
  is_dominant_channel: boolean;
  dependency_score: number | null;
  role: string;
  interpretation: string;
};

export type ChannelSummaryMetrics = {
  total_channel_traffic: number;
  dominant_channel: DominantChannel | null;
  channel_dependency_score: number | null;
  channel_diversification_score: number | null;
  channel_profile: string;
};

export type ChannelSummary = {
  scope: ChannelScope;
  period: {
    date_from: string;
    date_to: string;
    days_count: number;
  };
  summary: ChannelSummaryMetrics;
  channels: ChannelMetric[];
  warnings: string[];
  recommendation_hints: string[];
};

export type ChannelTrendItem = {
  date: string;
  channel_id: number;
  channel_code: string;
  channel_name: string;
  traffic: number;
  traffic_share: number | null;
};

export type ChannelTrendResponse = {
  items: ChannelTrendItem[];
};

export type JourneySourceItem = {
  journey_source_id: number;
  source_name: string | null;
  source_type: string | null;
  traffic_type: string | null;
  channel_id: number | null;
  channel_code: string | null;
  channel_name: string | null;
  traffic: number;
  traffic_share: number | null;
  growth_rate: number | null;
  stability_score: number | null;
};

export type JourneySourcesResponse = {
  items: JourneySourceItem[];
  warnings: string[];
};

export type OpportunityScoreValues = {
  opportunity_score: number;
  recommended_priority: string;
  market_type: string;
};

export type OpportunityComponents = {
  traffic_score: number | null;
  competition_score: number | null;
  quality_score: number | null;
  channel_gap_score: number | null;
  volatility_score: number | null;
  localization_potential_score: number | null;
  entry_difficulty_score: number | null;
};

export type OpportunityScore = {
  country: CountryItem;
  period: {
    date_from: string;
    date_to: string;
    days_count: number;
  };
  score: OpportunityScoreValues;
  components: OpportunityComponents;
  strengths: string[];
  risks: string[];
  explanation: string;
  data_quality_status: string;
  calculation: {
    calculation_version: string;
    calculated_at: string | null;
  };
};

export type OpportunityCountryItem = {
  country_id: number;
  country_name_en: string;
  country_name_ru: string | null;
  region_name_en: string | null;
  period_start: string;
  period_end: string;
  opportunity_score: number;
  recommended_priority: string;
  market_type: string;
  traffic_score: number | null;
  competition_score: number | null;
  quality_score: number | null;
  channel_gap_score: number | null;
  entry_difficulty_score: number | null;
};

export type OpportunityCountryList = {
  items: OpportunityCountryItem[];
  total: number;
};

export type BudgetAssumptions = {
  traffic_capture_rate: number;
  visit_to_lead_rate: number;
  lead_to_client_rate: number;
};

export type BudgetStrategyRequest = {
  country_id: number;
  date_from: string;
  date_to: string;
  budget_amount: number;
  currency_code: string;
  campaign_goal: string;
  risk_appetite: string;
  assumptions: BudgetAssumptions | null;
  calculation_version: string;
};

export type BudgetAllocationItem = {
  channel_id: number | null;
  channel_code: string;
  channel_name: string | null;
  budget_share: number;
  budget_amount: number;
  priority: string;
  risk_level: string;
  rationale: string;
  expected_traffic: number;
  expected_leads: number;
  expected_clients: number;
  test_hypothesis: string;
  success_metric: string;
};

export type BudgetStrategyResponse = {
  strategy_id: number;
  country: CountryItem;
  period: {
    date_from: string;
    date_to: string;
    days_count: number;
  };
  budget: {
    amount: number;
    currency_code: string;
  };
  strategy: {
    recommended_strategy_type: string;
    confidence_score: number;
    summary: string;
  };
  allocation: BudgetAllocationItem[];
  expected_effect: {
    expected_traffic: number;
    expected_leads: number;
    expected_clients: number;
  };
  risks: string[];
  recommendations: string[];
  assumptions: BudgetAssumptions;
  data_quality_status: string | null;
};

export type BudgetStrategyListItem = {
  strategy_id: number;
  country_id: number;
  country_name_en: string;
  period_start: string;
  period_end: string;
  budget_amount: number;
  currency_code: string;
  campaign_goal: string | null;
  strategy_status: string | null;
  recommended_strategy_type: string | null;
  total_expected_traffic: number | null;
  confidence_score: number | null;
  created_at: string | null;
};

export type BudgetStrategyList = {
  items: BudgetStrategyListItem[];
  total: number;
};

export type MASAnalyzeRequest = {
  user_query: string;
  country_id: number | null;
  date_from: string | null;
  date_to: string | null;
  budget_amount: number | null;
  currency_code: string;
  campaign_goal: string;
  risk_appetite: string;
  calculation_version: string;
};

export type MASStepItem = {
  agent_step_id: number;
  step_order: number;
  agent_name: string;
  step_type: string | null;
  step_status: string | null;
  summary: string | null;
};

export type MASEvidenceItem = {
  evidence_id: number;
  evidence_type: string | null;
  source_name: string | null;
  source_ref: string | null;
  metric_name: string | null;
  metric_value: number | null;
};

export type MASInsightItem = {
  insight_id: number;
  agent_name: string | null;
  insight_type: string | null;
  title: string;
  summary: string | null;
  severity: string | null;
  confidence_score: number | null;
};

export type MASRecommendationItem = {
  recommendation_id: number;
  recommendation_type: string | null;
  priority: string | null;
  title: string;
  description: string | null;
  rationale: string | null;
  expected_impact: string | null;
  confidence_score: number | null;
};

export type MASRunResponse = {
  agent_run_id: number;
  user_query: string;
  run_status: string | null;
  run_type: string | null;
  country_id: number | null;
  period_start: string | null;
  period_end: string | null;
  budget_amount: number | null;
  currency_code: string | null;
  campaign_goal: string | null;
  final_answer: string | null;
  confidence_score: number | null;
  steps: MASStepItem[];
  evidence: MASEvidenceItem[];
  insights: MASInsightItem[];
  recommendations: MASRecommendationItem[];
};

export type MASRunListItem = {
  agent_run_id: number;
  user_query: string;
  run_status: string | null;
  run_type: string | null;
  country_id: number | null;
  period_start: string | null;
  period_end: string | null;
  confidence_score: number | null;
  created_at: string | null;
};

export type MASRunList = {
  items: MASRunListItem[];
  total: number;
};

export type HistoryReportItem = {
  report_id: number;
  report_type: string;
  title: string;
  country_id: number | null;
  country_name_en: string | null;
  period_start: string | null;
  period_end: string | null;
  data_quality_status: string | null;
  report_status: string | null;
  created_at: string | null;
};

export type HistoryReportList = {
  items: HistoryReportItem[];
  total: number;
};

export type HistoryAgentRunItem = {
  agent_run_id: number;
  run_type: string | null;
  user_query: string;
  country_id: number | null;
  country_name_en: string | null;
  period_start: string | null;
  period_end: string | null;
  budget_amount: number | null;
  currency_code: string | null;
  run_status: string | null;
  confidence_score: number | null;
  created_at: string | null;
};

export type HistoryAgentRunList = {
  items: HistoryAgentRunItem[];
  total: number;
};

export type HistoryInsightItem = {
  insight_id: number;
  agent_run_id: number;
  insight_type: string | null;
  title: string;
  summary: string | null;
  country_id: number | null;
  country_name_en: string | null;
  severity: string | null;
  confidence_score: number | null;
  created_at: string | null;
};

export type HistoryInsightList = {
  items: HistoryInsightItem[];
  total: number;
};

export type HistoryRecommendationItem = {
  recommendation_id: number;
  agent_run_id: number;
  recommendation_type: string | null;
  priority: string | null;
  title: string;
  description: string | null;
  country_id: number | null;
  country_name_en: string | null;
  expected_impact: string | null;
  confidence_score: number | null;
  created_at: string | null;
};

export type HistoryRecommendationList = {
  items: HistoryRecommendationItem[];
  total: number;
};

export type SavedSummaryItem = {
  summary_id: number;
  summary_type: string;
  title: string;
  summary_text: string;
  country_id: number | null;
  country_name_en: string | null;
  domain_id: number | null;
  domain: string | null;
  channel_id: number | null;
  channel_name: string | null;
  period_start: string | null;
  period_end: string | null;
  source_type: string;
  source_id: number;
  tags: string[];
  importance_score: number | null;
  confidence_score: number | null;
  data_quality_status: string | null;
  rag_ready: boolean;
  embedding_status: string;
  created_at: string | null;
  updated_at: string | null;
};

export type SavedSummaryList = {
  items: SavedSummaryItem[];
  total: number;
};

export type DataWarning = {
  source_name: string;
  status: string;
  message: string;
};

export type AudienceSummary = {
  project_id: number;
  total_traffic: number;
  audience_fit_score: number | null;
  segments: {
    segment_type: string;
    segment_name: string;
    segment_value: string | null;
    traffic: number;
    traffic_share: number | null;
  }[];
  warnings: DataWarning[];
};

export type KeywordList = {
  items: {
    keyword_id: number;
    keyword_text: string;
    country_id: number | null;
    country_name_en: string | null;
    domain: string | null;
    position: number | null;
    search_volume: number | null;
    estimated_traffic: number | null;
    traffic_share: number | null;
    keyword_difficulty: number | null;
    cpc: number | null;
    estimated_cost: number | null;
    competition: number | null;
    currency_code: string | null;
  }[];
  total: number;
  warnings: DataWarning[];
};

export type MarketingOpportunity = {
  project_id: number;
  opportunity_score: number | null;
  demand: number;
  difficulty: number | null;
  estimated_cost: number | null;
  recommendation: string;
  warnings: DataWarning[];
};

export type TopPageList = {
  items: {
    page_id: number;
    url: string;
    page_type: string;
    domain: string | null;
    country_id: number | null;
    estimated_traffic: number | null;
    organic_traffic: number | null;
    paid_traffic: number | null;
    keywords_count: number | null;
    backlinks_count: number | null;
  }[];
  total: number;
  warnings: DataWarning[];
};

export type CpcSummary = {
  project_id: number;
  average_cpc: number | null;
  min_cpc: number | null;
  max_cpc: number | null;
  total_estimated_cost: number;
  currency_codes: string[];
  warnings: DataWarning[];
};

export type AdCreativeList = {
  items: {
    creative_hash: string;
    domain: string | null;
    country_id: number | null;
    headline: string | null;
    description: string | null;
    cta: string | null;
    ad_network: string | null;
    estimated_spend: number | null;
    estimated_traffic: number | null;
  }[];
  total: number;
  warnings: DataWarning[];
};

export type AdsSummary = {
  project_id: number;
  creatives_count: number;
  estimated_spend: number;
  estimated_traffic: number;
  top_ctas: Record<string, unknown>[];
  warnings: DataWarning[];
};

export type ReferringDomainList = {
  items: {
    referring_domain: string;
    domain: string | null;
    country_id: number | null;
    source_url: string | null;
    target_url: string | null;
    backlinks_count: number | null;
    authority_score: number | null;
    estimated_referral_traffic: number | null;
  }[];
  total: number;
  warnings: DataWarning[];
};

export type BusinessAssumptionItem = {
  assumption_id: number;
  project_id: number;
  country_id: number | null;
  currency_code: string;
  visit_to_lead_rate: number | null;
  lead_to_client_rate: number | null;
  average_order_value: number | null;
  ltv: number | null;
  gross_margin: number | null;
  target_cac: number | null;
  monthly_budget: number | null;
  confidence_score: number | null;
  valid_from: string | null;
  valid_to: string | null;
  notes: string | null;
};

export type BusinessAssumptionList = {
  items: BusinessAssumptionItem[];
  total: number;
};

export type CampaignItem = {
  campaign_id: number;
  project_id: number;
  campaign_name: string;
  channel_code: string | null;
  country_id: number | null;
  status: string;
  currency_code: string;
  start_date: string | null;
  end_date: string | null;
  notes: string | null;
};

export type CampaignList = {
  items: CampaignItem[];
  total: number;
};

export type CampaignPerformanceList = {
  items: {
    campaign_performance_id: number;
    campaign_id: number;
    date: string;
    impressions: number | null;
    clicks: number | null;
    visits: number | null;
    spend: number | null;
    leads: number | null;
    clients: number | null;
    revenue: number | null;
    cac: number | null;
    roas: number | null;
    roi: number | null;
  }[];
  total: number;
  summary: Record<string, number | null>;
};

export type AdvancedAssumptions = {
  visit_to_lead_rate: number;
  lead_to_client_rate: number;
  average_order_value: number;
  lifetime_value: number;
  gross_margin: number;
  target_cac: number;
  traffic_capture_rate: number;
};

export type AdvancedStrategyRequest = {
  country_id: number;
  date_from: string;
  date_to: string;
  forecast_start: string | null;
  forecast_end: string | null;
  budget_amount: number;
  currency_code: string;
  campaign_goal: string;
  risk_appetite: string;
  scenario_mode: string;
  assumptions: AdvancedAssumptions | null;
  calculation_version: string;
};

export type AdvancedScoreValues = {
  advanced_score_id: number | null;
  competitor_threat_score: number | null;
  market_maturity_score: number | null;
  paid_dependency_score: number | null;
  seo_opportunity_score: number | null;
  audience_fit_score: number | null;
  roi_potential_score: number | null;
  growth_feasibility_score: number | null;
  strategic_priority_score: number | null;
};

export type GrowthScenarioItem = {
  growth_scenario_id: number | null;
  scenario_name: string;
  budget_amount: number;
  currency_code: string;
  expected_traffic_capture: number;
  expected_leads: number;
  expected_clients: number;
  expected_revenue: number;
  expected_gross_profit: number;
  estimated_cac: number | null;
  estimated_roi: number | null;
  payback_period_days: number | null;
  confidence_score: number;
};

export type AdvancedAllocationItem = {
  advanced_allocation_id: number | null;
  growth_scenario_id: number | null;
  allocation_category: string;
  budget_share: number;
  budget_amount: number;
  expected_traffic: number;
  expected_leads: number;
  expected_clients: number;
  expected_revenue: number;
  estimated_cac: number | null;
  rationale: string;
  risk_level: string;
  success_metric: string;
};

export type AdvancedStrategyResponse = {
  country: CountryItem;
  period: {
    date_from: string;
    date_to: string;
    days_count: number;
  };
  forecast_period: {
    forecast_start: string | null;
    forecast_end: string | null;
  };
  advanced_scores: AdvancedScoreValues;
  recommended_strategy_type: string;
  scenarios: GrowthScenarioItem[];
  recommended_allocation: AdvancedAllocationItem[];
  sensitivity: {
    factor_name: string;
    base_value: number;
    low_value: number;
    high_value: number;
    low_clients: number;
    high_clients: number;
    low_roi: number | null;
    high_roi: number | null;
  }[];
  recommendations: string[];
  risks: string[];
  explanation: string;
  assumptions: AdvancedAssumptions;
  warnings: string[];
};

export type GrowthScenarioList = {
  items: GrowthScenarioItem[];
  total: number;
};

export type RecommendationFeedbackItem = {
  feedback_id: number;
  project_id: number;
  recommendation_id: number | null;
  agent_run_id: number | null;
  strategy_id: number | null;
  growth_scenario_id: number | null;
  campaign_id: number | null;
  country_id: number | null;
  channel_id: number | null;
  feedback_status: string;
  decision_reason: string | null;
  decision_tags: string[];
  decided_by_user_id: number | null;
  decided_at: string | null;
  created_at: string | null;
};

export type RecommendationFeedbackList = {
  items: RecommendationFeedbackItem[];
  total: number;
};

export type CampaignSnapshotItem = {
  campaign_result_snapshot_id: number;
  project_id: number;
  campaign_id: number;
  country_id: number | null;
  channel_id: number | null;
  period_start: string;
  period_end: string;
  budget_amount: number | null;
  actual_spend: number | null;
  impressions: number | null;
  clicks: number | null;
  visits: number | null;
  leads: number | null;
  clients: number | null;
  revenue: number | null;
  gross_profit: number | null;
  cac: number | null;
  cpl: number | null;
  roas: number | null;
  roi: number | null;
  currency_code: string;
  data_quality_status: string;
  source_type: string;
  created_at: string | null;
};

export type CampaignSnapshotList = {
  items: CampaignSnapshotItem[];
  total: number;
};

export type ForecastComparisonItem = {
  comparison_id: number;
  project_id: number;
  country_id: number | null;
  channel_id: number | null;
  campaign_id: number | null;
  recommendation_id: number | null;
  strategy_id: number | null;
  growth_scenario_id: number | null;
  campaign_result_snapshot_id: number;
  metric_name: string;
  forecast_value: number | null;
  actual_value: number | null;
  absolute_error: number | null;
  relative_error: number | null;
  accuracy_score: number | null;
  bias_direction: string;
  comparison_details: Record<string, unknown> | null;
  created_at: string | null;
};

export type ForecastComparisonList = {
  items: ForecastComparisonItem[];
  total: number;
};

export type ScoringWeightVersionItem = {
  weight_version_id: number;
  model_name: string;
  version_name: string;
  weights: Record<string, unknown>;
  status: string;
  created_from_version_id: number | null;
  created_by_user_id: number | null;
  created_at: string | null;
  activated_at: string | null;
};

export type ScoringWeightVersionList = {
  items: ScoringWeightVersionItem[];
  total: number;
};

export type ScoringWeightAdjustmentItem = {
  weight_adjustment_id: number;
  project_id: number;
  model_name: string;
  current_weight_version_id: number | null;
  proposed_version_name: string;
  proposed_weights: Record<string, unknown>;
  reason: string | null;
  evidence: Record<string, unknown> | null;
  expected_improvement: number | null;
  status: string;
  reviewed_by_user_id: number | null;
  reviewed_at: string | null;
  created_at: string | null;
  updated_at: string | null;
};

export type ScoringWeightAdjustmentList = {
  items: ScoringWeightAdjustmentItem[];
  total: number;
};

export type LearningSummary = {
  project_id: number;
  recommendation_acceptance_rate: number | null;
  recommendation_counts: Record<string, number>;
  average_forecast_accuracy: number | null;
  accuracy_by_metric: Record<string, number>;
  bias_by_metric: Record<string, Record<string, number>>;
  overestimated_signals: Record<string, unknown>[];
  underestimated_signals: Record<string, unknown>[];
  weight_adjustment_proposals: ScoringWeightAdjustmentItem[];
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

let authToken = localStorage.getItem('tgi_access_token') ?? '';
let refreshToken = localStorage.getItem('tgi_refresh_token') ?? '';

export function setAuthTokens(accessToken: string, nextRefreshToken: string): void {
  authToken = accessToken;
  refreshToken = nextRefreshToken;
  localStorage.setItem('tgi_access_token', accessToken);
  localStorage.setItem('tgi_refresh_token', nextRefreshToken);
}

export function clearAuthTokens(): void {
  authToken = '';
  refreshToken = '';
  localStorage.removeItem('tgi_access_token');
  localStorage.removeItem('tgi_refresh_token');
}

export function getStoredRefreshToken(): string {
  return refreshToken;
}

function authHeaders(): HeadersInit {
  if (authToken === '') {
    return {};
  }
  return {
    Authorization: `Bearer ${authToken}`,
  };
}

function jsonHeaders(): HeadersInit {
  return {
    ...authHeaders(),
    'Content-Type': 'application/json',
  };
}

export async function registerUser(email: string, password: string, fullName: string): Promise<AuthResponse> {
  const response = await fetch(`${apiBaseUrl}/auth/register`, {
    body: JSON.stringify({ email, password, full_name: fullName === '' ? null : fullName }),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Registration failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${apiBaseUrl}/auth/login`, {
    body: JSON.stringify({ email, password }),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Login failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function refreshUser(): Promise<AuthResponse> {
  const response = await fetch(`${apiBaseUrl}/auth/refresh`, {
    body: JSON.stringify({ refresh_token: refreshToken }),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error(`Refresh failed: ${response.status}`);
  }

  return response.json();
}

export async function logoutUser(): Promise<void> {
  if (refreshToken === '') {
    return;
  }
  await fetch(`${apiBaseUrl}/auth/logout`, {
    body: JSON.stringify({ refresh_token: refreshToken }),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
  });
}

export async function getCurrentUser(): Promise<UserInfo> {
  const response = await fetch(`${apiBaseUrl}/auth/me`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Current user request failed: ${response.status}`);
  }

  return response.json();
}

export async function getProjects(): Promise<ProjectList> {
  const response = await fetch(`${apiBaseUrl}/projects`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Projects request failed: ${response.status}`);
  }

  return response.json();
}

export async function createProject(payload: {
  project_name: string;
  project_slug: string;
  description: string | null;
  default_currency_code: string;
}): Promise<ProjectItem> {
  const response = await fetch(`${apiBaseUrl}/projects`, {
    body: JSON.stringify(payload),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Project create failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getProjectMembers(projectId: number): Promise<ProjectMemberList> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/members`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Project members request failed: ${response.status}`);
  }

  return response.json();
}

export async function addProjectMember(projectId: number, email: string, role: string): Promise<ProjectMemberItem> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/members`, {
    body: JSON.stringify({ email, role }),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Project member add failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function updateProjectMember(projectId: number, userId: number, role: string, status: string): Promise<ProjectMemberItem> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/members/${userId}`, {
    body: JSON.stringify({ role, status }),
    headers: jsonHeaders(),
    method: 'PATCH',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Project member update failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getProjectCompetitors(projectId: number): Promise<ProjectCompetitorList> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/competitors`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Project competitors request failed: ${response.status}`);
  }

  return response.json();
}

export async function addProjectCompetitor(projectId: number, payload: {
  domain_id: number;
  company_id: number | null;
  competitor_tier: string;
  priority: string;
  notes: string | null;
}): Promise<ProjectCompetitorItem> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/competitors`, {
    body: JSON.stringify(payload),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Project competitor add failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function removeProjectCompetitor(projectId: number, domainId: number): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/competitors/${domainId}`, {
    headers: authHeaders(),
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`Project competitor remove failed: ${response.status}`);
  }
}

export async function getProjectTargetCountries(projectId: number): Promise<ProjectCountryList> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/target-countries`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Project countries request failed: ${response.status}`);
  }

  return response.json();
}

export async function addProjectTargetCountry(projectId: number, payload: {
  country_id: number;
  status: string;
  strategic_priority: string;
  notes: string | null;
}): Promise<ProjectCountryItem> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/target-countries`, {
    body: JSON.stringify(payload),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Project country add failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function updateProjectTargetCountry(projectId: number, countryId: number, payload: {
  status: string;
  strategic_priority: string;
  notes: string | null;
}): Promise<ProjectCountryItem> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/target-countries/${countryId}`, {
    body: JSON.stringify(payload),
    headers: jsonHeaders(),
    method: 'PATCH',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Project country update failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getUpdateSchedules(projectId: number | null): Promise<UpdateScheduleList> {
  const params = new URLSearchParams({ limit: '50' });
  if (projectId != null) {
    params.set('project_id', String(projectId));
  }
  const response = await fetch(`${apiBaseUrl}/update-schedules?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Update schedules request failed: ${response.status}`);
  }

  return response.json();
}

export async function createUpdateSchedule(payload: {
  project_id: number | null;
  schedule_name: string;
  update_type: string;
  frequency: string;
  cron_expression: string | null;
  timezone: string;
  lookback_days: number;
  default_granularity: string;
  config: Record<string, unknown>;
}): Promise<UpdateScheduleItem> {
  const response = await fetch(`${apiBaseUrl}/update-schedules`, {
    body: JSON.stringify(payload),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Update schedule create failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function updateUpdateSchedule(scheduleId: number, payload: Partial<UpdateScheduleItem>): Promise<UpdateScheduleItem> {
  const response = await fetch(`${apiBaseUrl}/update-schedules/${scheduleId}`, {
    body: JSON.stringify(payload),
    headers: jsonHeaders(),
    method: 'PATCH',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Update schedule update failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function runUpdateNow(scheduleId: number): Promise<UpdateRunQueued> {
  const response = await fetch(`${apiBaseUrl}/update-schedules/${scheduleId}/run-now`, {
    body: JSON.stringify({ run_type: 'manual' }),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Run now failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getUpdateRuns(projectId: number | null): Promise<UpdateRunList> {
  const params = new URLSearchParams({ limit: '50' });
  if (projectId != null) {
    params.set('project_id', String(projectId));
  }
  const response = await fetch(`${apiBaseUrl}/update-runs?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Update runs request failed: ${response.status}`);
  }

  return response.json();
}

export async function getUpdateRunSteps(updateRunId: number): Promise<UpdateRunStepList> {
  const response = await fetch(`${apiBaseUrl}/update-runs/${updateRunId}/steps`);

  if (!response.ok) {
    throw new Error(`Update run steps request failed: ${response.status}`);
  }

  return response.json();
}

export async function getLatestUpdateStatus(projectId: number | null): Promise<UpdateLatestStatus> {
  const params = new URLSearchParams();
  if (projectId != null) {
    params.set('project_id', String(projectId));
  }
  const suffix = params.toString() === '' ? '' : `?${params.toString()}`;
  const response = await fetch(`${apiBaseUrl}/update-status/latest${suffix}`);

  if (!response.ok) {
    throw new Error(`Latest update status request failed: ${response.status}`);
  }

  return response.json();
}

export async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch(`${apiBaseUrl}/health`);

  if (!response.ok) {
    throw new Error(`Health request failed: ${response.status}`);
  }

  return response.json();
}

export async function uploadDataFile(file: File, options: UploadOptions): Promise<JobQueuedResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('source_name', options.sourceName);
  formData.append('is_synthetic', String(options.isSynthetic));
  formData.append('granularity', options.granularity);

  if (options.periodStart !== '') {
    formData.append('period_start', options.periodStart);
  }

  if (options.periodEnd !== '') {
    formData.append('period_end', options.periodEnd);
  }

  const response = await fetch(`${apiBaseUrl}/data/upload`, {
    body: formData,
    method: 'POST',
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Upload failed: ${response.status} ${errorBody}`);
  }

  return response.json();
}

export async function getUploadRuns(): Promise<UploadRunSummary[]> {
  const response = await fetch(`${apiBaseUrl}/data/uploads`);

  if (!response.ok) {
    throw new Error(`Upload history request failed: ${response.status}`);
  }

  return response.json();
}

export async function getUploadRun(runId: number): Promise<UploadRunDetail> {
  const response = await fetch(`${apiBaseUrl}/data/uploads/${runId}`);

  if (!response.ok) {
    throw new Error(`Upload run request failed: ${response.status}`);
  }

  return response.json();
}

export async function getQualityChecks(runId: number): Promise<QualityResult> {
  const response = await fetch(`${apiBaseUrl}/data/uploads/${runId}/quality-checks`);

  if (!response.ok) {
    throw new Error(`Quality checks request failed: ${response.status}`);
  }

  return response.json();
}

export async function runQualityChecks(runId: number): Promise<QualityResult> {
  const response = await fetch(`${apiBaseUrl}/data/uploads/${runId}/quality-checks/run`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error(`Quality checks run failed: ${response.status}`);
  }

  return response.json();
}

export async function getQualitySummary(): Promise<QualityRunSummary[]> {
  const response = await fetch(`${apiBaseUrl}/data/quality-summary`);

  if (!response.ok) {
    throw new Error(`Quality summary request failed: ${response.status}`);
  }

  return response.json();
}

export async function getJobs(): Promise<JobList> {
  const response = await fetch(`${apiBaseUrl}/jobs?limit=25`);

  if (!response.ok) {
    throw new Error(`Jobs request failed: ${response.status}`);
  }

  return response.json();
}

export async function getJob(jobId: string): Promise<JobItem> {
  const response = await fetch(`${apiBaseUrl}/jobs/${jobId}`);

  if (!response.ok) {
    throw new Error(`Job request failed: ${response.status}`);
  }

  return response.json();
}

export async function getJobEvents(jobId: string): Promise<JobEventList> {
  const response = await fetch(`${apiBaseUrl}/jobs/${jobId}/events`);

  if (!response.ok) {
    throw new Error(`Job events request failed: ${response.status}`);
  }

  return response.json();
}

export async function getCountries(search = ''): Promise<CountryList> {
  const params = new URLSearchParams({ has_data: 'true', limit: '200' });
  if (search !== '') {
    params.set('search', search);
  }

  const response = await fetch(`${apiBaseUrl}/countries?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Countries request failed: ${response.status}`);
  }

  return response.json();
}

export async function getCountryPeriod(countryId: number): Promise<CountryPeriod> {
  const response = await fetch(`${apiBaseUrl}/countries/${countryId}/available-period`);

  if (!response.ok) {
    throw new Error(`Country period request failed: ${response.status}`);
  }

  return response.json();
}

export async function getCountrySummary(
  countryId: number,
  dateFrom: string,
  dateTo: string,
  limitCompetitors = 10,
): Promise<CountrySummary> {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
    limit_competitors: String(limitCompetitors),
  });

  const response = await fetch(`${apiBaseUrl}/countries/${countryId}/summary?${params.toString()}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Country summary request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getCountryMetrics(
  countryId: number,
  dateFrom: string,
  dateTo: string,
): Promise<CountryMetricsResponse> {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
    calculation_version: 'v1',
    recalculate_if_missing: 'true',
  });

  const response = await fetch(`${apiBaseUrl}/countries/${countryId}/metrics?${params.toString()}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Country metrics request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getCountryDailyMetrics(
  countryId: number,
  dateFrom: string,
  dateTo: string,
): Promise<DailyMetricsResponse> {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
  });

  const response = await fetch(`${apiBaseUrl}/countries/${countryId}/metrics/daily?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Country daily metrics request failed: ${response.status}`);
  }

  return response.json();
}

export async function createCountryReport(request: CountryReportRequest): Promise<JobQueuedResponse> {
  const response = await fetch(`${apiBaseUrl}/reports/country`, {
    body: JSON.stringify(request),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Country report request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getReport(reportId: number): Promise<ReportResponse> {
  const response = await fetch(`${apiBaseUrl}/reports/${reportId}`);

  if (!response.ok) {
    throw new Error(`Report request failed: ${response.status}`);
  }

  return response.json();
}

export async function getReports(): Promise<ReportList> {
  const response = await fetch(`${apiBaseUrl}/reports?report_type=country_report&limit=50`);

  if (!response.ok) {
    throw new Error(`Reports request failed: ${response.status}`);
  }

  return response.json();
}

export async function getCompetitors(search = ''): Promise<CompetitorList> {
  const params = new URLSearchParams({ has_data: 'true', limit: '200' });
  if (search !== '') {
    params.set('search', search);
  }

  const response = await fetch(`${apiBaseUrl}/competitors?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Competitors request failed: ${response.status}`);
  }

  return response.json();
}

export async function getCompetitorPeriod(domainId: number): Promise<CompetitorPeriod> {
  const response = await fetch(`${apiBaseUrl}/competitors/${domainId}/available-period`);

  if (!response.ok) {
    throw new Error(`Competitor period request failed: ${response.status}`);
  }

  return response.json();
}

export async function getCompetitorSummary(
  domainId: number,
  dateFrom: string,
  dateTo: string,
  limitCountries = 10,
): Promise<CompetitorSummary> {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
    limit_countries: String(limitCountries),
  });

  const response = await fetch(`${apiBaseUrl}/competitors/${domainId}/summary?${params.toString()}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Competitor summary request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getChannelSummary(
  dateFrom: string,
  dateTo: string,
  countryId: number | null,
  domainId: number | null,
): Promise<ChannelSummary> {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
    calculation_version: 'v1',
    recalculate_if_missing: 'true',
  });
  if (countryId != null) {
    params.set('country_id', String(countryId));
  }
  if (domainId != null) {
    params.set('domain_id', String(domainId));
  }

  const response = await fetch(`${apiBaseUrl}/channels/summary?${params.toString()}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Channel summary request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getChannelTrend(
  dateFrom: string,
  dateTo: string,
  countryId: number | null,
  domainId: number | null,
): Promise<ChannelTrendResponse> {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
  });
  if (countryId != null) {
    params.set('country_id', String(countryId));
  }
  if (domainId != null) {
    params.set('domain_id', String(domainId));
  }

  const response = await fetch(`${apiBaseUrl}/channels/trend?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Channel trend request failed: ${response.status}`);
  }

  return response.json();
}

export async function getJourneySources(
  dateFrom: string,
  dateTo: string,
  countryId: number | null,
  domainId: number | null,
): Promise<JourneySourcesResponse> {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
    limit: '30',
  });
  if (countryId != null) {
    params.set('country_id', String(countryId));
  }
  if (domainId != null) {
    params.set('domain_id', String(domainId));
  }

  const response = await fetch(`${apiBaseUrl}/channels/journey-sources?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Journey sources request failed: ${response.status}`);
  }

  return response.json();
}

export async function getOpportunityScore(
  countryId: number,
  dateFrom: string,
  dateTo: string,
): Promise<OpportunityScore> {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
    calculation_version: 'v1',
    calculate_if_missing: 'true',
    force_recalculate: 'false',
  });

  const response = await fetch(`${apiBaseUrl}/countries/${countryId}/opportunity-score?${params.toString()}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Opportunity score request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getOpportunityCountries(
  dateFrom: string,
  dateTo: string,
  priority = '',
): Promise<OpportunityCountryList> {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
    limit: '50',
    calculate_if_missing: 'true',
    force_recalculate: 'false',
  });
  if (priority !== '') {
    params.set('priority', priority);
  }

  const response = await fetch(`${apiBaseUrl}/opportunities/countries?${params.toString()}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Opportunity countries request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function createBudgetStrategy(request: BudgetStrategyRequest): Promise<BudgetStrategyResponse> {
  const response = await fetch(`${apiBaseUrl}/strategy/budget`, {
    body: JSON.stringify(request),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Budget strategy request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getBudgetStrategies(): Promise<BudgetStrategyList> {
  const response = await fetch(`${apiBaseUrl}/strategy/budget?limit=25`);

  if (!response.ok) {
    throw new Error(`Budget strategy history request failed: ${response.status}`);
  }

  return response.json();
}

export async function getBudgetStrategy(strategyId: number): Promise<BudgetStrategyResponse> {
  const response = await fetch(`${apiBaseUrl}/strategy/budget/${strategyId}`);

  if (!response.ok) {
    throw new Error(`Budget strategy request failed: ${response.status}`);
  }

  return response.json();
}

export async function analyzeMAS(request: MASAnalyzeRequest): Promise<JobQueuedResponse> {
  const response = await fetch(`${apiBaseUrl}/mas/analyze`, {
    body: JSON.stringify(request),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`MAS analysis request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getMASRuns(): Promise<MASRunList> {
  const response = await fetch(`${apiBaseUrl}/mas/runs?limit=25`);

  if (!response.ok) {
    throw new Error(`MAS runs request failed: ${response.status}`);
  }

  return response.json();
}

export async function getMASRun(runId: number): Promise<MASRunResponse> {
  const response = await fetch(`${apiBaseUrl}/mas/runs/${runId}`);

  if (!response.ok) {
    throw new Error(`MAS run request failed: ${response.status}`);
  }

  return response.json();
}

export async function getHistoryReports(): Promise<HistoryReportList> {
  const response = await fetch(`${apiBaseUrl}/history/reports?limit=50`);

  if (!response.ok) {
    throw new Error(`History reports request failed: ${response.status}`);
  }

  return response.json();
}

export async function getHistoryAgentRuns(): Promise<HistoryAgentRunList> {
  const response = await fetch(`${apiBaseUrl}/history/agent-runs?limit=50`);

  if (!response.ok) {
    throw new Error(`History agent runs request failed: ${response.status}`);
  }

  return response.json();
}

export async function getHistoryInsights(): Promise<HistoryInsightList> {
  const response = await fetch(`${apiBaseUrl}/history/insights?limit=50`);

  if (!response.ok) {
    throw new Error(`History insights request failed: ${response.status}`);
  }

  return response.json();
}

export async function getHistoryRecommendations(): Promise<HistoryRecommendationList> {
  const response = await fetch(`${apiBaseUrl}/history/recommendations?limit=50`);

  if (!response.ok) {
    throw new Error(`History recommendations request failed: ${response.status}`);
  }

  return response.json();
}

export async function getSavedSummaries(): Promise<SavedSummaryList> {
  const response = await fetch(`${apiBaseUrl}/history/summaries?limit=50`);

  if (!response.ok) {
    throw new Error(`Saved summaries request failed: ${response.status}`);
  }

  return response.json();
}

export async function updateSavedSummary(summaryId: number, payload: Partial<SavedSummaryItem>): Promise<SavedSummaryItem> {
  const response = await fetch(`${apiBaseUrl}/history/summaries/${summaryId}`, {
    body: JSON.stringify(payload),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'PATCH',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Saved summary update failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getAlertSummary(): Promise<AlertSummary> {
  const response = await fetch(`${apiBaseUrl}/alerts/summary`);

  if (!response.ok) {
    throw new Error(`Alert summary request failed: ${response.status}`);
  }

  return response.json();
}

export async function getAlerts(filters: AlertFilters): Promise<AlertList> {
  const params = new URLSearchParams({
    limit: '50',
  });
  const mappings: [keyof AlertFilters, string][] = [
    ['countryId', 'country_id'],
    ['domainId', 'domain_id'],
    ['channelId', 'channel_id'],
    ['eventType', 'event_type'],
    ['eventCategory', 'event_category'],
    ['severity', 'severity'],
    ['status', 'status'],
    ['dateFrom', 'date_from'],
    ['dateTo', 'date_to'],
  ];
  for (const [sourceKey, targetKey] of mappings) {
    if (filters[sourceKey] !== '') {
      params.set(targetKey, filters[sourceKey]);
    }
  }

  const response = await fetch(`${apiBaseUrl}/alerts?${params.toString()}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Alerts request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getAlertDetail(anomalyId: number): Promise<AlertDetail> {
  const response = await fetch(`${apiBaseUrl}/alerts/${anomalyId}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Alert detail request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function detectAlerts(request: AlertDetectRequest): Promise<JobQueuedResponse> {
  const response = await fetch(`${apiBaseUrl}/alerts/detect`, {
    body: JSON.stringify(request),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Alert detection failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function updateAlertStatus(anomalyId: number, status: string): Promise<AlertDetail> {
  const response = await fetch(`${apiBaseUrl}/alerts/${anomalyId}/status`, {
    body: JSON.stringify({ status }),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'PATCH',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Alert status update failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getWorkflowOptions(): Promise<WorkflowOptions> {
  const response = await fetch(`${apiBaseUrl}/workflow/options`);

  if (!response.ok) {
    throw new Error(`Workflow options request failed: ${response.status}`);
  }

  return response.json();
}

export async function runStrategyWorkflow(request: WorkflowRequest): Promise<JobQueuedResponse> {
  const response = await fetch(`${apiBaseUrl}/workflow/strategy-analysis`, {
    body: JSON.stringify(request),
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Workflow analysis failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function runProjectStrategyWorkflow(projectId: number, request: WorkflowRequest): Promise<JobQueuedResponse> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/workflow/strategy-analysis`, {
    body: JSON.stringify({ ...request, project_id: projectId }),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Project workflow analysis failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getRecentWorkflows(): Promise<WorkflowRunList> {
  const response = await fetch(`${apiBaseUrl}/workflow/recent?limit=20`);

  if (!response.ok) {
    throw new Error(`Workflow history request failed: ${response.status}`);
  }

  return response.json();
}

export async function getWorkflowRun(workflowRunId: number): Promise<WorkflowRunDetail> {
  const response = await fetch(`${apiBaseUrl}/workflow/runs/${workflowRunId}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Workflow run request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

async function projectGet<T>(projectId: number, path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}${path}`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Project marketing request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getAudienceSummary(projectId: number): Promise<AudienceSummary> {
  return projectGet<AudienceSummary>(projectId, '/audience/summary');
}

export async function getSeoKeywords(projectId: number): Promise<KeywordList> {
  return projectGet<KeywordList>(projectId, '/seo/keywords');
}

export async function getSeoOpportunity(projectId: number): Promise<MarketingOpportunity> {
  return projectGet<MarketingOpportunity>(projectId, '/seo/opportunity');
}

export async function getSeoTopPages(projectId: number): Promise<TopPageList> {
  return projectGet<TopPageList>(projectId, '/seo/top-pages');
}

export async function getPpcKeywords(projectId: number): Promise<KeywordList> {
  return projectGet<KeywordList>(projectId, '/ppc/keywords');
}

export async function getPpcOpportunity(projectId: number): Promise<MarketingOpportunity> {
  return projectGet<MarketingOpportunity>(projectId, '/ppc/opportunity');
}

export async function getPpcCpcSummary(projectId: number): Promise<CpcSummary> {
  return projectGet<CpcSummary>(projectId, '/ppc/cpc-summary');
}

export async function getAdsCreatives(projectId: number): Promise<AdCreativeList> {
  return projectGet<AdCreativeList>(projectId, '/ads/creatives');
}

export async function getAdsSummary(projectId: number): Promise<AdsSummary> {
  return projectGet<AdsSummary>(projectId, '/ads/summary');
}

export async function getReferringDomains(projectId: number): Promise<ReferringDomainList> {
  return projectGet<ReferringDomainList>(projectId, '/backlinks/referring-domains');
}

export async function getBacklinkOpportunity(projectId: number): Promise<MarketingOpportunity> {
  return projectGet<MarketingOpportunity>(projectId, '/backlinks/opportunity');
}

export async function getBusinessAssumptions(projectId: number): Promise<BusinessAssumptionList> {
  return projectGet<BusinessAssumptionList>(projectId, '/business-assumptions');
}

export async function createBusinessAssumption(
  projectId: number,
  payload: Partial<BusinessAssumptionItem>,
): Promise<BusinessAssumptionItem> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/business-assumptions`, {
    body: JSON.stringify(payload),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Business assumption create failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getCampaigns(projectId: number): Promise<CampaignList> {
  return projectGet<CampaignList>(projectId, '/campaigns');
}

export async function createCampaign(projectId: number, payload: Partial<CampaignItem>): Promise<CampaignItem> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/campaigns`, {
    body: JSON.stringify(payload),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Campaign create failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getCampaignPerformance(projectId: number, campaignId: number): Promise<CampaignPerformanceList> {
  return projectGet<CampaignPerformanceList>(projectId, `/campaigns/${campaignId}/performance`);
}

export async function createAdvancedStrategy(
  projectId: number,
  request: AdvancedStrategyRequest,
): Promise<AdvancedStrategyResponse> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/advanced-strategy`, {
    body: JSON.stringify(request),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Advanced strategy request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getAdvancedScenarios(projectId: number): Promise<GrowthScenarioList> {
  return projectGet<GrowthScenarioList>(projectId, '/advanced-strategy/scenarios');
}

export async function getLearningSummary(projectId: number): Promise<LearningSummary> {
  return projectGet<LearningSummary>(projectId, '/feedback/learning-summary');
}

export async function getRecommendationFeedback(projectId: number): Promise<RecommendationFeedbackList> {
  return projectGet<RecommendationFeedbackList>(projectId, '/feedback/recommendations');
}

export async function createRecommendationFeedback(
  projectId: number,
  payload: Partial<RecommendationFeedbackItem>,
): Promise<RecommendationFeedbackItem> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/feedback/recommendations`, {
    body: JSON.stringify(payload),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Recommendation feedback failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getCampaignSnapshots(projectId: number): Promise<CampaignSnapshotList> {
  return projectGet<CampaignSnapshotList>(projectId, '/feedback/campaign-snapshots');
}

export async function createCampaignSnapshot(
  projectId: number,
  payload: Partial<CampaignSnapshotItem>,
): Promise<CampaignSnapshotItem> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/feedback/campaign-snapshots`, {
    body: JSON.stringify(payload),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Campaign snapshot failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getForecastComparisons(projectId: number): Promise<ForecastComparisonList> {
  return projectGet<ForecastComparisonList>(projectId, '/feedback/forecast-comparisons');
}

export async function createForecastComparisons(
  projectId: number,
  payload: {
    growth_scenario_id: number | null;
    campaign_result_snapshot_id: number;
    recommendation_id: number | null;
    strategy_id: number | null;
    metric_names: string[];
  },
): Promise<ForecastComparisonList> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/feedback/forecast-comparisons`, {
    body: JSON.stringify(payload),
    headers: jsonHeaders(),
    method: 'POST',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Forecast comparison failed: ${response.status} ${errorText}`);
  }

  return response.json();
}

export async function getScoringWeights(projectId: number): Promise<ScoringWeightVersionList> {
  return projectGet<ScoringWeightVersionList>(projectId, '/feedback/scoring-weights');
}

export async function getScoringAdjustments(projectId: number): Promise<ScoringWeightAdjustmentList> {
  return projectGet<ScoringWeightAdjustmentList>(projectId, '/feedback/scoring-adjustments');
}

export async function updateScoringAdjustment(
  projectId: number,
  adjustmentId: number,
  status: string,
): Promise<ScoringWeightAdjustmentItem> {
  const response = await fetch(`${apiBaseUrl}/projects/${projectId}/feedback/scoring-adjustments/${adjustmentId}`, {
    body: JSON.stringify({ status }),
    headers: jsonHeaders(),
    method: 'PATCH',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Scoring adjustment update failed: ${response.status} ${errorText}`);
  }

  return response.json();
}
