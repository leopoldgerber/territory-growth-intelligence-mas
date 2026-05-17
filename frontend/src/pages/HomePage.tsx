import { lazy, Suspense, useCallback, useEffect, useState } from 'react';

import { fetchHealth, type HealthStatus } from '../api/client';
import { ProjectSwitcher } from '../components/ProjectSwitcher';
import { SystemStatusCard } from '../components/SystemStatusCard';

const AlertsPage = lazy(() => import('./AlertsPage').then((module) => ({ default: module.AlertsPage })));
const AdvancedStrategyPage = lazy(() => import('./AdvancedStrategyPage').then((module) => ({ default: module.AdvancedStrategyPage })));
const BudgetStrategyPage = lazy(() => import('./BudgetStrategyPage').then((module) => ({ default: module.BudgetStrategyPage })));
const ChannelIntelligencePage = lazy(() => import('./ChannelIntelligencePage').then((module) => ({ default: module.ChannelIntelligencePage })));
const CompetitorOverviewPage = lazy(() => import('./CompetitorOverviewPage').then((module) => ({ default: module.CompetitorOverviewPage })));
const CountryOverviewPage = lazy(() => import('./CountryOverviewPage').then((module) => ({ default: module.CountryOverviewPage })));
const DataUploadPage = lazy(() => import('./DataUploadPage').then((module) => ({ default: module.DataUploadPage })));
const DataUpdatesPage = lazy(() => import('./DataUpdatesPage').then((module) => ({ default: module.DataUpdatesPage })));
const KnowledgeHistoryPage = lazy(() => import('./KnowledgeHistoryPage').then((module) => ({ default: module.KnowledgeHistoryPage })));
const LearningFeedbackPage = lazy(() => import('./LearningFeedbackPage').then((module) => ({ default: module.LearningFeedbackPage })));
const MarketingIntelligencePage = lazy(() => import('./MarketingIntelligencePage').then((module) => ({ default: module.MarketingIntelligencePage })));
const OpportunitiesPage = lazy(() => import('./OpportunitiesPage').then((module) => ({ default: module.OpportunitiesPage })));
const ProjectSettingsPage = lazy(() => import('./ProjectSettingsPage').then((module) => ({ default: module.ProjectSettingsPage })));
const StrategyAssistantPage = lazy(() => import('./StrategyAssistantPage').then((module) => ({ default: module.StrategyAssistantPage })));
const StrategyWorkspacePage = lazy(() => import('./StrategyWorkspacePage').then((module) => ({ default: module.StrategyWorkspacePage })));

type AppPage = 'home' | 'workspace' | 'upload' | 'updates' | 'country' | 'competitors' | 'channels' | 'marketing' | 'opportunities' | 'alerts' | 'budget' | 'advanced' | 'feedback' | 'mas' | 'history' | 'settings';

const NAV_ITEMS: { id: AppPage; label: string }[] = [
  { id: 'home', label: 'Home' },
  { id: 'workspace', label: 'Strategy Workspace' },
  { id: 'upload', label: 'Upload' },
  { id: 'updates', label: 'Data Updates' },
  { id: 'country', label: 'Country Overview' },
  { id: 'competitors', label: 'Competitors' },
  { id: 'channels', label: 'Channels' },
  { id: 'marketing', label: 'Marketing Intelligence' },
  { id: 'opportunities', label: 'Opportunities' },
  { id: 'alerts', label: 'Alerts' },
  { id: 'budget', label: 'Budget Strategy' },
  { id: 'advanced', label: 'Advanced Strategy' },
  { id: 'feedback', label: 'Learning & Feedback' },
  { id: 'mas', label: 'MAS Assistant' },
  { id: 'history', label: 'Knowledge History' },
  { id: 'settings', label: 'Project Settings' },
];

export function HomePage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [activePage, setActivePage] = useState<AppPage>('home');

  const loadHealth = useCallback(async () => {
    setIsLoading(true);
    setError('');

    try {
      const healthData = await fetchHealth();
      setHealth(healthData);
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown healthcheck error';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadHealth();
  }, [loadHealth]);

  return (
    <main className="pageShell">
      <ProjectSwitcher onOpenSettings={() => setActivePage('settings')} />
      <section className="introSection">
        <p className="eyebrow">Stage 16 auth and projects</p>
        <h1>Territory Growth Intelligence MAS</h1>
        <p className="leadText">Upload parser reports, validate data, score markets, and orchestrate strategy agents over country signals.</p>
      </section>

      <nav className="appNavigation" aria-label="Application sections">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            className={activePage === item.id ? 'secondaryButton active' : 'secondaryButton'}
            type="button"
            onClick={() => setActivePage(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <SystemStatusCard health={health} isLoading={isLoading} error={error} onRefresh={loadHealth} />
      <Suspense fallback={<p className="mutedText">Loading section...</p>}>
        {activePage === 'home' && (
          <section className="countryOverview" aria-label="Home">
            <div className="sectionHeader">
              <div>
                <h2>Workspace</h2>
                <p>Select a section above to load only the workflow you need.</p>
              </div>
            </div>
          </section>
        )}
        {activePage === 'workspace' && <StrategyWorkspacePage />}
        {activePage === 'upload' && <DataUploadPage />}
        {activePage === 'updates' && <DataUpdatesPage />}
        {activePage === 'country' && <CountryOverviewPage />}
        {activePage === 'competitors' && <CompetitorOverviewPage />}
        {activePage === 'channels' && <ChannelIntelligencePage />}
        {activePage === 'marketing' && <MarketingIntelligencePage />}
        {activePage === 'opportunities' && <OpportunitiesPage />}
        {activePage === 'alerts' && <AlertsPage />}
        {activePage === 'budget' && <BudgetStrategyPage />}
        {activePage === 'advanced' && <AdvancedStrategyPage />}
        {activePage === 'feedback' && <LearningFeedbackPage />}
        {activePage === 'mas' && <StrategyAssistantPage />}
        {activePage === 'history' && <KnowledgeHistoryPage />}
        {activePage === 'settings' && <ProjectSettingsPage />}
      </Suspense>
    </main>
  );
}
