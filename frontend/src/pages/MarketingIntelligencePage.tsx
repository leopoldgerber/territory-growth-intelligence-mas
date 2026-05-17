import { useCallback, useEffect, useState } from 'react';

import {
  createBusinessAssumption,
  createCampaign,
  getAdsCreatives,
  getAdsSummary,
  getAudienceSummary,
  getBacklinkOpportunity,
  getBusinessAssumptions,
  getCampaigns,
  getPpcCpcSummary,
  getPpcKeywords,
  getPpcOpportunity,
  getReferringDomains,
  getSeoKeywords,
  getSeoOpportunity,
  getSeoTopPages,
  type AdCreativeList,
  type AdsSummary,
  type AudienceSummary,
  type BusinessAssumptionList,
  type CampaignList,
  type CpcSummary,
  type KeywordList,
  type MarketingOpportunity,
  type ReferringDomainList,
  type TopPageList,
} from '../api/client';
import { useAuth } from '../components/AuthProvider';

type MarketingState = {
  audience: AudienceSummary | null;
  seoKeywords: KeywordList | null;
  seoOpportunity: MarketingOpportunity | null;
  topPages: TopPageList | null;
  ppcKeywords: KeywordList | null;
  ppcOpportunity: MarketingOpportunity | null;
  cpc: CpcSummary | null;
  ads: AdCreativeList | null;
  adsSummary: AdsSummary | null;
  backlinks: ReferringDomainList | null;
  backlinkOpportunity: MarketingOpportunity | null;
  assumptions: BusinessAssumptionList | null;
  campaigns: CampaignList | null;
};

const emptyState: MarketingState = {
  audience: null,
  seoKeywords: null,
  seoOpportunity: null,
  topPages: null,
  ppcKeywords: null,
  ppcOpportunity: null,
  cpc: null,
  ads: null,
  adsSummary: null,
  backlinks: null,
  backlinkOpportunity: null,
  assumptions: null,
  campaigns: null,
};

function formatNumber(value: number | null | undefined): string {
  if (value == null) {
    return 'No data';
  }
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
}

function warningText(warnings: { message: string }[] | undefined): string {
  if (warnings == null || warnings.length === 0) {
    return '';
  }
  return warnings.map((warning) => warning.message).join(' ');
}

export function MarketingIntelligencePage() {
  const { activeProject } = useAuth();
  const [state, setState] = useState<MarketingState>(emptyState);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [assumptionStatus, setAssumptionStatus] = useState('');
  const [campaignStatus, setCampaignStatus] = useState('');

  const loadData = useCallback(async () => {
    if (activeProject == null) {
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const [
        audience,
        seoKeywords,
        seoOpportunity,
        topPages,
        ppcKeywords,
        ppcOpportunity,
        cpc,
        ads,
        adsSummary,
        backlinks,
        backlinkOpportunity,
        assumptions,
        campaigns,
      ] = await Promise.all([
        getAudienceSummary(activeProject.project_id),
        getSeoKeywords(activeProject.project_id),
        getSeoOpportunity(activeProject.project_id),
        getSeoTopPages(activeProject.project_id),
        getPpcKeywords(activeProject.project_id),
        getPpcOpportunity(activeProject.project_id),
        getPpcCpcSummary(activeProject.project_id),
        getAdsCreatives(activeProject.project_id),
        getAdsSummary(activeProject.project_id),
        getReferringDomains(activeProject.project_id),
        getBacklinkOpportunity(activeProject.project_id),
        getBusinessAssumptions(activeProject.project_id),
        getCampaigns(activeProject.project_id),
      ]);
      setState({
        audience,
        seoKeywords,
        seoOpportunity,
        topPages,
        ppcKeywords,
        ppcOpportunity,
        cpc,
        ads,
        adsSummary,
        backlinks,
        backlinkOpportunity,
        assumptions,
        campaigns,
      });
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Marketing intelligence request failed';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [activeProject]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const addAssumption = async () => {
    if (activeProject == null) {
      return;
    }
    setAssumptionStatus('');
    await createBusinessAssumption(activeProject.project_id, {
      currency_code: 'EUR',
      visit_to_lead_rate: 0.03,
      lead_to_client_rate: 0.15,
      average_order_value: 1000,
      ltv: 3000,
      gross_margin: 0.6,
      target_cac: 400,
      monthly_budget: 5000,
      confidence_score: 0.6,
      notes: 'Baseline assumption from UI quick add.',
    });
    setAssumptionStatus('Baseline assumption added.');
    await loadData();
  };

  const addCampaign = async () => {
    if (activeProject == null) {
      return;
    }
    setCampaignStatus('');
    await createCampaign(activeProject.project_id, {
      campaign_name: 'Market validation campaign',
      channel_code: 'paid',
      status: 'active',
      currency_code: 'EUR',
      notes: 'Baseline campaign from UI quick add.',
    });
    setCampaignStatus('Campaign added.');
    await loadData();
  };

  if (activeProject == null) {
    return (
      <section className="countryOverview" aria-label="Marketing intelligence">
        <p className="mutedText">Select a project to view marketing intelligence.</p>
      </section>
    );
  }

  return (
    <section className="countryOverview" aria-label="Marketing intelligence">
      <div className="sectionHeader">
        <div>
          <h2>Marketing Intelligence</h2>
          <p>Audience, SEO, PPC, creative, backlinks, assumptions, and campaign evidence for the active project.</p>
        </div>
        <button className="secondaryButton" type="button" onClick={loadData} disabled={isLoading}>
          Refresh
        </button>
      </div>

      {error !== '' && <p className="errorText">{error}</p>}
      {isLoading && <p className="mutedText">Loading marketing sources...</p>}

      <div className="summaryGrid">
        <article className="overviewPanel">
          <h3>Audience Intelligence</h3>
          <p className="metricValue">{formatNumber(state.audience?.audience_fit_score)}</p>
          <p className="mutedText">{warningText(state.audience?.warnings) || `${state.audience?.segments.length ?? 0} audience segments loaded.`}</p>
        </article>
        <article className="overviewPanel">
          <h3>SEO Intelligence</h3>
          <p className="metricValue">{formatNumber(state.seoOpportunity?.opportunity_score)}</p>
          <p className="mutedText">{state.seoOpportunity?.recommendation ?? 'Organic keyword data is not loaded yet.'}</p>
        </article>
        <article className="overviewPanel">
          <h3>PPC Intelligence</h3>
          <p className="metricValue">{formatNumber(state.ppcOpportunity?.opportunity_score)}</p>
          <p className="mutedText">Average CPC: {formatNumber(state.cpc?.average_cpc)}</p>
        </article>
        <article className="overviewPanel">
          <h3>Backlink Referral</h3>
          <p className="metricValue">{formatNumber(state.backlinkOpportunity?.opportunity_score)}</p>
          <p className="mutedText">{state.backlinkOpportunity?.recommendation ?? 'Backlink data is not loaded yet.'}</p>
        </article>
      </div>

      <div className="splitLayout">
        <article className="workspacePanel">
          <h3>SEO Keywords</h3>
          <table className="dataTable">
            <thead>
              <tr>
                <th>Keyword</th>
                <th>Domain</th>
                <th>Volume</th>
                <th>Traffic</th>
              </tr>
            </thead>
            <tbody>
              {(state.seoKeywords?.items ?? []).slice(0, 8).map((item) => (
                <tr key={`${item.keyword_id}-${item.domain ?? ''}`}>
                  <td>{item.keyword_text}</td>
                  <td>{item.domain ?? 'No data'}</td>
                  <td>{formatNumber(item.search_volume)}</td>
                  <td>{formatNumber(item.estimated_traffic)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>

        <article className="workspacePanel">
          <h3>PPC Keywords</h3>
          <table className="dataTable">
            <thead>
              <tr>
                <th>Keyword</th>
                <th>CPC</th>
                <th>Cost</th>
                <th>Traffic</th>
              </tr>
            </thead>
            <tbody>
              {(state.ppcKeywords?.items ?? []).slice(0, 8).map((item) => (
                <tr key={`${item.keyword_id}-${item.currency_code ?? ''}`}>
                  <td>{item.keyword_text}</td>
                  <td>{formatNumber(item.cpc)}</td>
                  <td>{formatNumber(item.estimated_cost)}</td>
                  <td>{formatNumber(item.estimated_traffic)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
      </div>

      <div className="splitLayout">
        <article className="workspacePanel">
          <h3>Competitor Top Pages</h3>
          <table className="dataTable">
            <thead>
              <tr>
                <th>URL</th>
                <th>Type</th>
                <th>Traffic</th>
              </tr>
            </thead>
            <tbody>
              {(state.topPages?.items ?? []).slice(0, 6).map((item) => (
                <tr key={item.page_id}>
                  <td>{item.url}</td>
                  <td>{item.page_type}</td>
                  <td>{formatNumber(item.estimated_traffic)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>

        <article className="workspacePanel">
          <h3>Ads Creative</h3>
          <p className="mutedText">
            {state.adsSummary?.creatives_count ?? 0} creatives, estimated spend {formatNumber(state.adsSummary?.estimated_spend)}
          </p>
          <table className="dataTable">
            <thead>
              <tr>
                <th>Headline</th>
                <th>CTA</th>
                <th>Spend</th>
              </tr>
            </thead>
            <tbody>
              {(state.ads?.items ?? []).slice(0, 6).map((item) => (
                <tr key={item.creative_hash}>
                  <td>{item.headline ?? 'No headline'}</td>
                  <td>{item.cta ?? 'No CTA'}</td>
                  <td>{formatNumber(item.estimated_spend)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
      </div>

      <article className="workspacePanel">
        <h3>Backlink / Referral Intelligence</h3>
        <table className="dataTable">
          <thead>
            <tr>
              <th>Referring Domain</th>
              <th>Competitor</th>
              <th>Authority</th>
              <th>Backlinks</th>
            </tr>
          </thead>
          <tbody>
            {(state.backlinks?.items ?? []).slice(0, 8).map((item) => (
              <tr key={`${item.referring_domain}-${item.domain ?? ''}`}>
                <td>{item.referring_domain}</td>
                <td>{item.domain ?? 'No data'}</td>
                <td>{formatNumber(item.authority_score)}</td>
                <td>{formatNumber(item.backlinks_count)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>

      <div className="splitLayout">
        <article className="workspacePanel">
          <div className="sectionHeader compactHeader">
            <h3>Business Assumptions</h3>
            <button className="secondaryButton" type="button" onClick={addAssumption}>
              Add baseline
            </button>
          </div>
          <p className="mutedText">{assumptionStatus || `${state.assumptions?.total ?? 0} assumption rows.`}</p>
          <table className="dataTable">
            <thead>
              <tr>
                <th>Currency</th>
                <th>LTV</th>
                <th>Target CAC</th>
              </tr>
            </thead>
            <tbody>
              {(state.assumptions?.items ?? []).slice(0, 5).map((item) => (
                <tr key={item.assumption_id}>
                  <td>{item.currency_code}</td>
                  <td>{formatNumber(item.ltv)}</td>
                  <td>{formatNumber(item.target_cac)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>

        <article className="workspacePanel">
          <div className="sectionHeader compactHeader">
            <h3>Campaign Performance</h3>
            <button className="secondaryButton" type="button" onClick={addCampaign}>
              Add campaign
            </button>
          </div>
          <p className="mutedText">{campaignStatus || `${state.campaigns?.total ?? 0} campaigns configured.`}</p>
          <table className="dataTable">
            <thead>
              <tr>
                <th>Campaign</th>
                <th>Channel</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {(state.campaigns?.items ?? []).slice(0, 5).map((item) => (
                <tr key={item.campaign_id}>
                  <td>{item.campaign_name}</td>
                  <td>{item.channel_code ?? 'No data'}</td>
                  <td>{item.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>
      </div>
    </section>
  );
}
