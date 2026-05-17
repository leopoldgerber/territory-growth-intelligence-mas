import { useEffect, useState } from 'react';

import { getJob, getJobEvents, type JobEventItem, type JobItem } from '../api/client';

type JobProgressPanelProps = {
  jobId: string | null;
  title: string;
  onComplete?: (job: JobItem) => void;
};

export function JobProgressPanel({ jobId, title, onComplete }: JobProgressPanelProps) {
  const [job, setJob] = useState<JobItem | null>(null);
  const [events, setEvents] = useState<JobEventItem[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    if (jobId == null) {
      return;
    }
    let isMounted = true;
    const loadJob = async () => {
      try {
        const [jobData, eventData] = await Promise.all([getJob(jobId), getJobEvents(jobId)]);
        if (!isMounted) {
          return;
        }
        setJob(jobData);
        setEvents(eventData.items);
        if (['success', 'failed', 'cancelled', 'partial'].includes(jobData.status)) {
          onComplete?.(jobData);
          return;
        }
        window.setTimeout(() => void loadJob(), 1500);
      } catch (requestError) {
        const message = requestError instanceof Error ? requestError.message : 'Job progress request failed';
        if (isMounted) {
          setError(message);
        }
      }
    };
    void loadJob();
    return () => {
      isMounted = false;
    };
  }, [jobId, onComplete]);

  if (jobId == null) {
    return null;
  }

  const progress = Math.max(0, Math.min(100, Math.round(job?.progress_percent ?? 0)));

  return (
    <section className="jobProgressPanel" aria-label={title}>
      <div className="sectionHeader">
        <div>
          <h3>{title}</h3>
          <p>{job?.current_step || 'Queued'}</p>
        </div>
        <span className={`pill ${job?.status || 'queued'}`}>{job?.status || 'queued'}</span>
      </div>
      <div className="progressTrack">
        <span style={{ width: `${progress}%` }} />
      </div>
      <p className="mutedText">{progress}% complete · Job {jobId}</p>
      {job?.error_message && <p className="errorText">{job.error_message}</p>}
      {error && <p className="errorText">{error}</p>}
      <ol className="jobTimeline">
        {events.map((event) => (
          <li key={event.event_id}>
            <strong>{event.step_name || event.event_type}</strong>
            <span>{event.message || event.event_type}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}
