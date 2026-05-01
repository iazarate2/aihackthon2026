import { useState, useEffect } from 'react';
import SampleCaseSelector from './SampleCaseSelector';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function UploadPanel({ onResult, onLoading }) {
  const [originalCall, setOriginalCall] = useState('Charge');
  const [file, setFile] = useState(null);
  const [sampleCaseId, setSampleCaseId] = useState(null);
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API}/sample-cases`)
      .then(r => r.json())
      .then(d => setCases(d.cases || []))
      .catch(() => {});
  }, []);

  // When a sample case is selected, auto-fill original call
  useEffect(() => {
    if (sampleCaseId) {
      const c = cases.find(c => c.id === sampleCaseId);
      if (c) setOriginalCall(c.original_call);
      setFile(null);
    }
  }, [sampleCaseId, cases]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    onLoading(true);

    const body = new FormData();
    body.append('original_call', originalCall);

    if (sampleCaseId) {
      body.append('sample_case_id', sampleCaseId);
    } else if (file) {
      body.append('file', file);
    } else {
      setError('Select a sample case or upload a video clip.');
      setLoading(false);
      onLoading(false);
      return;
    }

    try {
      const res = await fetch(`${API}/review`, { method: 'POST', body });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Request failed (${res.status})`);
      }
      const data = await res.json();
      onResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      onLoading(false);
    }
  }

  return (
    <section>
      <div className="container">
        <h2 style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-dim)', marginBottom: '1rem' }}>
          Review Panel
        </h2>
        <form onSubmit={handleSubmit} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Original call */}
          <div>
            <label htmlFor="call">Original Referee Call</label>
            <select id="call" value={originalCall} onChange={e => setOriginalCall(e.target.value)}>
              <option>Charge</option>
              <option>Blocking Foul</option>
              <option>No Call</option>
            </select>
          </div>

          {/* File upload */}
          <div>
            <label>Upload Video Clip</label>
            <input
              type="file"
              accept="video/mp4,video/quicktime,video/x-msvideo,video/webm"
              onChange={e => { setFile(e.target.files?.[0] || null); setSampleCaseId(null); }}
            />
            {file && <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem', display: 'block' }}>{file.name}</span>}
          </div>

          {/* Divider */}
          <div style={{ textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.75rem' }}>— or —</div>

          {/* Sample cases */}
          <SampleCaseSelector cases={cases} selected={sampleCaseId} onSelect={setSampleCaseId} />

          {/* Error */}
          {error && <p style={{ color: 'var(--red)', fontSize: '0.85rem' }}>{error}</p>}

          {/* Submit */}
          <button type="submit" className="btn btn-primary" disabled={loading} style={{ marginTop: '0.5rem' }}>
            {loading ? <><span className="spinner" /> Reviewing...</> : '🏀 Run Review'}
          </button>
        </form>
      </div>
    </section>
  );
}
