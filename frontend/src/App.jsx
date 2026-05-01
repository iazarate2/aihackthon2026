import { useState } from 'react';
import Header from './components/Header';
import HowItWorks from './components/HowItWorks';
import UploadPanel from './components/UploadPanel';
import ResultCard from './components/ResultCard';
import SupportedReviews from './components/SupportedReviews';

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="container">
      <Header />
      <HowItWorks />
      <UploadPanel onResult={setResult} onLoading={setLoading} />
      {loading && (
        <div className="card glow-orange" style={{ textAlign: 'center', padding: '2rem', margin: '2rem auto', maxWidth: 400 }}>
          <div className="spinner" style={{ margin: '0 auto 0.75rem' }} />
          <p style={{ color: 'var(--orange)', fontSize: '0.9rem', fontWeight: 600 }}>
            Reviewing play...
          </p>
          <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
            Analyzing frames against basketball rules
          </p>
        </div>
      )}
      <ResultCard result={result} />
      <SupportedReviews />
      <footer style={{ textAlign: 'center', padding: '2rem 0', borderTop: '1px solid var(--border)' }}>
        <p style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
          RefCheck AI — BorderHack '26 · Basketball Coach Challenge Review Assistant
        </p>
      </footer>
    </div>
  );
}
