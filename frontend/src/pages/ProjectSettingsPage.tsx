import { useCallback, useEffect, useState } from 'react';

import {
  addProjectCompetitor,
  addProjectMember,
  addProjectTargetCountry,
  createProject,
  getProjectCompetitors,
  getProjectMembers,
  getProjectTargetCountries,
  updateProjectMember,
  type ProjectCompetitorItem,
  type ProjectCountryItem,
  type ProjectMemberItem,
} from '../api/client';
import { useAuth } from '../components/AuthProvider';

export function ProjectSettingsPage() {
  const { activeProject, reloadUser, user } = useAuth();
  const [members, setMembers] = useState<ProjectMemberItem[]>([]);
  const [competitors, setCompetitors] = useState<ProjectCompetitorItem[]>([]);
  const [countries, setCountries] = useState<ProjectCountryItem[]>([]);
  const [projectName, setProjectName] = useState('');
  const [projectSlug, setProjectSlug] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [memberEmail, setMemberEmail] = useState('');
  const [memberRole, setMemberRole] = useState('viewer');
  const [domainId, setDomainId] = useState('');
  const [countryId, setCountryId] = useState('');
  const [countryStatus, setCountryStatus] = useState('watchlist');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const canManage = activeProject?.role === 'admin' || user?.is_superadmin === true;

  const loadSettings = useCallback(async () => {
    if (activeProject == null) {
      return;
    }
    setError('');
    try {
      const [memberData, competitorData, countryData] = await Promise.all([
        getProjectMembers(activeProject.project_id),
        getProjectCompetitors(activeProject.project_id),
        getProjectTargetCountries(activeProject.project_id),
      ]);
      setMembers(memberData.items);
      setCompetitors(competitorData.items);
      setCountries(countryData.items);
    } catch (requestError) {
      const detail = requestError instanceof Error ? requestError.message : 'Project settings request failed';
      setError(detail);
    }
  }, [activeProject]);

  useEffect(() => {
    void loadSettings();
  }, [loadSettings]);

  const submitProject = async () => {
    setError('');
    setMessage('');
    try {
      await createProject({
        project_name: projectName,
        project_slug: projectSlug,
        description: projectDescription === '' ? null : projectDescription,
        default_currency_code: 'EUR',
      });
      setMessage('Project created.');
      setProjectName('');
      setProjectSlug('');
      setProjectDescription('');
      await reloadUser();
    } catch (requestError) {
      const detail = requestError instanceof Error ? requestError.message : 'Project create failed';
      setError(detail);
    }
  };

  const submitMember = async () => {
    if (activeProject == null) {
      return;
    }
    setError('');
    setMessage('');
    try {
      await addProjectMember(activeProject.project_id, memberEmail, memberRole);
      setMessage('Member saved.');
      setMemberEmail('');
      await loadSettings();
      await reloadUser();
    } catch (requestError) {
      const detail = requestError instanceof Error ? requestError.message : 'Member save failed';
      setError(detail);
    }
  };

  const changeMember = async (member: ProjectMemberItem, role: string) => {
    if (activeProject == null) {
      return;
    }
    await updateProjectMember(activeProject.project_id, member.user_id, role, member.status);
    await loadSettings();
  };

  const submitCompetitor = async () => {
    if (activeProject == null || domainId === '') {
      return;
    }
    setError('');
    setMessage('');
    try {
      await addProjectCompetitor(activeProject.project_id, {
        domain_id: Number(domainId),
        company_id: null,
        competitor_tier: 'unknown',
        priority: 'medium',
        notes: null,
      });
      setMessage('Competitor saved.');
      setDomainId('');
      await loadSettings();
    } catch (requestError) {
      const detail = requestError instanceof Error ? requestError.message : 'Competitor save failed';
      setError(detail);
    }
  };

  const submitCountry = async () => {
    if (activeProject == null || countryId === '') {
      return;
    }
    setError('');
    setMessage('');
    try {
      await addProjectTargetCountry(activeProject.project_id, {
        country_id: Number(countryId),
        status: countryStatus,
        strategic_priority: 'medium',
        notes: null,
      });
      setMessage('Target country saved.');
      setCountryId('');
      await loadSettings();
    } catch (requestError) {
      const detail = requestError instanceof Error ? requestError.message : 'Country save failed';
      setError(detail);
    }
  };

  return (
    <section className="projectSettings" aria-label="Project settings">
      <div className="sectionHeader">
        <div>
          <h2>Project Settings</h2>
          <p>{activeProject == null ? 'Create a project to start using project-aware workflows.' : activeProject.project_name}</p>
        </div>
        {activeProject && <span className="pill">{activeProject.role}</span>}
      </div>

      <div className="workspacePanel">
        <h3>Create project</h3>
        <div className="settingsForm">
          <label>
            Project name
            <input value={projectName} onChange={(event) => setProjectName(event.target.value)} />
          </label>
          <label>
            Slug
            <input value={projectSlug} onChange={(event) => setProjectSlug(event.target.value)} />
          </label>
          <label>
            Description
            <input value={projectDescription} onChange={(event) => setProjectDescription(event.target.value)} />
          </label>
          <button type="button" onClick={submitProject}>
            Create project
          </button>
        </div>
      </div>

      {activeProject && (
        <>
          <div className="workspacePanel">
            <h3>Members</h3>
            {canManage && (
              <div className="settingsForm compactForm">
                <label>
                  Email
                  <input value={memberEmail} onChange={(event) => setMemberEmail(event.target.value)} />
                </label>
                <label>
                  Role
                  <select value={memberRole} onChange={(event) => setMemberRole(event.target.value)}>
                    <option value="viewer">viewer</option>
                    <option value="analyst">analyst</option>
                    <option value="admin">admin</option>
                  </select>
                </label>
                <button type="button" onClick={submitMember}>
                  Add member
                </button>
              </div>
            )}
            <div className="tableWrap">
              <table className="dataTable">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {members.map((member) => (
                    <tr key={member.user_id}>
                      <td>{member.full_name || '-'}</td>
                      <td>{member.email}</td>
                      <td>
                        {canManage ? (
                          <select value={member.role} onChange={(event) => void changeMember(member, event.target.value)}>
                            <option value="viewer">viewer</option>
                            <option value="analyst">analyst</option>
                            <option value="admin">admin</option>
                          </select>
                        ) : (
                          member.role
                        )}
                      </td>
                      <td>{member.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="workspaceGrid">
            <div className="workspacePanel">
              <h3>Competitors</h3>
              <div className="settingsForm compactForm">
                <label>
                  Domain ID
                  <input value={domainId} onChange={(event) => setDomainId(event.target.value)} />
                </label>
                <button type="button" onClick={submitCompetitor}>
                  Add competitor
                </button>
              </div>
              <div className="compactList">
                {competitors.map((competitor) => (
                  <div key={competitor.domain_id} className="resultCard">
                    <strong>{competitor.domain || `Domain #${competitor.domain_id}`}</strong>
                    <span>{competitor.priority} · {competitor.competitor_tier} · {competitor.is_active ? 'active' : 'inactive'}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="workspacePanel">
              <h3>Target countries</h3>
              <div className="settingsForm compactForm">
                <label>
                  Country ID
                  <input value={countryId} onChange={(event) => setCountryId(event.target.value)} />
                </label>
                <label>
                  Status
                  <select value={countryStatus} onChange={(event) => setCountryStatus(event.target.value)}>
                    <option value="watchlist">watchlist</option>
                    <option value="testing">testing</option>
                    <option value="active">active</option>
                    <option value="avoid">avoid</option>
                    <option value="priority">priority</option>
                  </select>
                </label>
                <button type="button" onClick={submitCountry}>
                  Add country
                </button>
              </div>
              <div className="compactList">
                {countries.map((country) => (
                  <div key={country.country_id} className="resultCard">
                    <strong>{country.country_name_en || `Country #${country.country_id}`}</strong>
                    <span>{country.status} · {country.strategic_priority}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {message && <p className="successText">{message}</p>}
      {error && <p className="errorText">{error}</p>}
    </section>
  );
}
