import { useCallback, useEffect, useState } from 'react';

import {
  getQualityChecks,
  getUploadRuns,
  runQualityChecks,
  uploadDataFile,
  type QualityResult,
  type UploadOptions,
  type UploadRunResult,
  type UploadRunSummary,
  type JobItem,
} from '../api/client';
import { DataQualitySummaryCard } from '../components/DataQualitySummaryCard';
import { JobProgressPanel } from '../components/JobProgressPanel';
import { UploadDropzone } from '../components/UploadDropzone';
import { UploadHistoryTable } from '../components/UploadHistoryTable';
import { UploadOptionsForm } from '../components/UploadOptionsForm';
import { UploadResultCard } from '../components/UploadResultCard';

const defaultOptions: UploadOptions = {
  sourceName: 'manual_upload',
  isSynthetic: false,
  granularity: 'daily',
  periodStart: '',
  periodEnd: '',
};

export function DataUploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [options, setOptions] = useState<UploadOptions>(defaultOptions);
  const [result, setResult] = useState<UploadRunResult | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [quality, setQuality] = useState<QualityResult | null>(null);
  const [runs, setRuns] = useState<UploadRunSummary[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isQualityRunning, setIsQualityRunning] = useState(false);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [error, setError] = useState('');

  const loadHistory = useCallback(async () => {
    setIsHistoryLoading(true);
    try {
      const uploadRuns = await getUploadRuns();
      setRuns(uploadRuns);
    } finally {
      setIsHistoryLoading(false);
    }
  }, []);

  const submitUpload = async () => {
    if (!file) {
      setError('Select .zip or .xlsx file before upload.');
      return;
    }

    setError('');
    setIsUploading(true);

    try {
      const queuedJob = await uploadDataFile(file, options);
      setJobId(queuedJob.job_id);
      await loadHistory();
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : 'Unknown upload error';
      setError(message);
    } finally {
      setIsUploading(false);
    }
  };

  const finishJob = async (job: JobItem) => {
    if (job.result_payload == null || job.related_entity_id == null) {
      return;
    }
    const uploadResult = job.result_payload as unknown as UploadRunResult;
    setResult(uploadResult);
    if (job.status !== 'failed') {
      const qualityResult = await getQualityChecks(job.related_entity_id);
      setQuality(qualityResult);
    }
    await loadHistory();
    setIsUploading(false);
  };

  const rerunQuality = async () => {
    if (!result) {
      return;
    }

    setIsQualityRunning(true);
    try {
      const qualityResult = await runQualityChecks(result.run_id);
      setQuality(qualityResult);
      await loadHistory();
    } finally {
      setIsQualityRunning(false);
    }
  };

  useEffect(() => {
    void loadHistory();
  }, [loadHistory]);

  return (
    <section className="dataUploadLayout" aria-label="Data upload">
      <div className="uploadPanel">
        <div className="sectionHeader">
          <div>
            <h2>Data upload</h2>
            <p>Load parser output into PostgreSQL dimensions and daily facts.</p>
          </div>
        </div>
        <UploadDropzone file={file} onFileChange={setFile} />
        <UploadOptionsForm options={options} onOptionsChange={setOptions} />
        <button type="button" onClick={submitUpload} disabled={isUploading}>
          {isUploading ? 'Uploading' : 'Upload data'}
        </button>
        {error !== '' && <p className="errorText">{error}</p>}
      </div>

      <JobProgressPanel jobId={jobId} title="Upload progress" onComplete={(job) => void finishJob(job)} />
      <UploadResultCard result={result} />
      <DataQualitySummaryCard
        quality={quality}
        fallbackStatus={result?.quality_status}
        fallbackSummary={result?.quality_summary}
        onRerun={result ? rerunQuality : undefined}
        isRunning={isQualityRunning}
      />
      <UploadHistoryTable runs={runs} isLoading={isHistoryLoading} />
    </section>
  );
}
