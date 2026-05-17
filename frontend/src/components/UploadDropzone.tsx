import { type DragEvent, type ChangeEvent } from 'react';

type UploadDropzoneProps = {
  file: File | null;
  onFileChange: (file: File | null) => void;
};

export function UploadDropzone({ file, onFileChange }: UploadDropzoneProps) {
  const handleDrop = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    const selectedFile = event.dataTransfer.files.item(0);
    onFileChange(selectedFile);
  };

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.item(0) ?? null;
    onFileChange(selectedFile);
  };

  return (
    <label
      className="dropzone"
      onDragOver={(event) => event.preventDefault()}
      onDrop={handleDrop}
    >
      <span className="dropzoneTitle">{file?.name ?? 'Choose .zip or .xlsx file'}</span>
      <span className="dropzoneMeta">{file ? `${Math.round(file.size / 1024)} KB` : 'Drop parser output here'}</span>
      <input accept=".zip,.xlsx" className="hiddenInput" type="file" onChange={handleChange} />
    </label>
  );
}
