from agent_app.agent.tasks import AgentTask, domain_tasks, initial_search, login_task, process_task


def build_plan(
    mode: str,
    domain_list: list[str],
    month_list: list[str],
    year: int,
    first_domain: str,
    stop_after_first: bool,
) -> list[AgentTask]:
    """Build task plan.
    Args:
        mode (str): Run mode.
        domain_list (list[str]): Domain names.
        month_list (list[str]): Month names.
        year (int): Report year.
        first_domain (str): First domain.
        stop_after_first (bool): Stop after first flag."""
    tasks = []
    if mode in ['download', 'full']:
        tasks.append(login_task())
        tasks.append(initial_search(first_domain))
        selected_domains = domain_list[:1] if stop_after_first else domain_list
        for domain in selected_domains:
            tasks.extend(domain_tasks(domain, month_list, year))
    if mode in ['process', 'full']:
        tasks.append(process_task())
    return tasks
