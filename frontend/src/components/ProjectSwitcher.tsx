import { useAuth } from './AuthProvider';

export function ProjectSwitcher({ onOpenSettings }: { onOpenSettings: () => void }) {
  const { activeProject, logout, setActiveProjectId, user } = useAuth();

  if (user == null) {
    return null;
  }

  return (
    <div className="topBar">
      <label className="projectSwitcher">
        Project
        <select
          value={activeProject?.project_id ?? ''}
          onChange={(event) => setActiveProjectId(Number(event.target.value))}
        >
          {user.projects.map((project) => (
            <option key={project.project_id} value={project.project_id}>
              {project.project_name} · {project.role}
            </option>
          ))}
        </select>
      </label>
      <div className="userMenu">
        <span>{user.full_name || user.email}</span>
        <button className="secondaryButton" type="button" onClick={onOpenSettings}>
          Project Settings
        </button>
        <button className="secondaryButton" type="button" onClick={() => void logout()}>
          Logout
        </button>
      </div>
    </div>
  );
}
