import { useState } from 'react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function displayError(message) {
  if (!message) return 'Review request failed.';
  if (message.includes('insufficient_quota') || message.includes('exceeded your current quota')) {
    return 'Real AI analysis is enabled, but the OpenAI account has no available quota. Add billing/credits or use another API key, then run the review again.';
  }
  if (message.startsWith('OpenAI analysis failed:')) {
    return message.replace('OpenAI analysis failed:', 'Real AI analysis failed:').trim();
  }
  return message;
}

export default function UploadPanel({ onResult, onLoading }) {
  const [originalCall, setOriginalCall] = useState('Charge');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    onLoading(true);

    const body = new FormData();
    body.append('original_call', originalCall);

    if (file) {
      body.append('file', file);
    } else {
      setError('Upload a video clip before running the review.');
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
      setError(displayError(err.message));
    } finally {
      setLoading(false);
      onLoading(false);
    }
  }

  return (
    <section>
      <div className="container">
        <div className="review-layout">
          <aside className="card glass-panel review-intro">
            <div className="review-eyebrow">Review Panel</div>
            <h2 className="review-title">Put the play on the floor.</h2>
            <p className="review-copy">
              Choose the original whistle and upload a clip. The backend extracts key frames, retrieves relevant NBA rule context, and reviews the play with AI.
            </p>
          </aside>

          <div className="card glass-panel">
            <form onSubmit={handleSubmit} className="review-form">
              <div className="form-row">
                <label htmlFor="call">Original Referee Call</label>
                <select id="call" value={originalCall} onChange={e => setOriginalCall(e.target.value)}>
                  <option>Charge</option>
                  <option>Blocking Foul</option>
                  <option>No Call</option>
                </select>
              </div>

              <div className="form-row">
                <label htmlFor="clip">Upload Video Clip</label>
                <label className="file-drop" htmlFor="clip">
                  <span className="file-drop-title">{file ? file.name : 'Choose a short basketball clip'}</span>
                  <span className="file-drop-meta">MP4, MOV, AVI, MKV, or WEBM</span>
                  <input
                    id="clip"
                    type="file"
                    accept="video/mp4,video/quicktime,video/x-msvideo,video/webm"
                    onChange={e => setFile(e.target.files?.[0] || null)}
                  />
                </label>
              </div>

              {error && <p className="error-box">{error}</p>}

              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? <><span className="spinner" /> Reviewing...</> : 'Run Review'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
