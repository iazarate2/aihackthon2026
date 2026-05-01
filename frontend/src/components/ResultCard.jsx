import { useEffect, useRef } from 'react';
import RuleCard from './RuleCard';
import FramePreview from './FramePreview';
import Icon from './Icon';

function verdictBadge(verdict) {
  if (verdict === 'Fair Call') return 'badge-green';
  if (verdict === 'Bad Call') return 'badge-red';
  return 'badge-yellow';
}

function verdictGlow(verdict) {
  if (verdict === 'Fair Call') return 'glow-green';
  if (verdict === 'Bad Call') return 'glow-red';
  return 'glow-yellow';
}

function recBadge(rec) {
  if (rec === 'Uphold Call') return 'badge-green';
  if (rec === 'Overturn Call') return 'badge-red';
  return 'badge-yellow';
}

function confColor(conf) {
  if (conf >= 0.7) return 'var(--green)';
  if (conf >= 0.55) return 'var(--yellow)';
  return 'var(--red)';
}

function verdictIcon(verdict) {
  if (verdict === 'Fair Call') return 'check';
  if (verdict === 'Bad Call') return 'x';
  return 'alert';
}

function verdictIconColor(verdict) {
  if (verdict === 'Fair Call') return 'var(--green)';
  if (verdict === 'Bad Call') return 'var(--red)';
  return 'var(--yellow)';
}

export default function ResultCard({ result }) {
  const ref = useRef(null);

  // Scroll to result when it appears
  useEffect(() => {
    if (result && ref.current) {
      ref.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [result]);

  if (!result) return null;
  const pct = Math.round(result.confidence * 100);

  return (
    <section ref={ref} id="result">
      <div className="container">
        <h2 className="section-heading">Review Result</h2>
        <div className={`card animate-in ${verdictGlow(result.verdict)}`} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

          {/* Verdict hero */}
          <div className="verdict-hero">
            <div className="verdict-icon" style={{ color: verdictIconColor(result.verdict) }}>
              <Icon name={verdictIcon(result.verdict)} size={30} />
            </div>
            <span className={`badge badge-verdict ${verdictBadge(result.verdict)}`}>
              {result.verdict}
            </span>
            <div>
              <span className={`badge ${recBadge(result.challenge_recommendation)}`}>
                Coach Recommendation: {result.challenge_recommendation}
              </span>
            </div>
          </div>

          {/* Confidence */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.3rem' }}>
              <span>Confidence</span>
              <span style={{ color: confColor(result.confidence), fontWeight: 700, fontSize: '0.85rem' }}>{pct}%</span>
            </div>
            <div className="conf-bar">
              <div className="conf-fill" style={{ width: `${pct}%`, background: confColor(result.confidence) }} />
            </div>
          </div>

          {/* Call comparison */}
          <div className="calls-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem', textAlign: 'center' }}>
            <div className="card" style={{ padding: '0.85rem 0.5rem' }}>
              <div style={{ fontSize: '0.6rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Original Call</div>
              <div style={{ fontWeight: 700, fontSize: '1rem', marginTop: '0.2rem' }}>{result.original_call}</div>
            </div>
            <div className="card" style={{ padding: '0.85rem 0.5rem', position: 'relative' }}>
              <div style={{ fontSize: '0.6rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>AI Predicted</div>
              <div style={{ fontWeight: 700, fontSize: '1rem', marginTop: '0.2rem', color: result.original_call !== result.predicted_call ? 'var(--orange)' : 'var(--text)' }}>
                {result.predicted_call}
              </div>
              {result.original_call !== result.predicted_call && result.predicted_call !== 'Inconclusive' && (
                <div style={{ fontSize: '0.6rem', color: 'var(--orange)', marginTop: '0.15rem' }}>≠ differs</div>
              )}
            </div>
            <div className="card" style={{ padding: '0.85rem 0.5rem' }}>
              <div style={{ fontSize: '0.6rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Review Type</div>
              <div style={{ fontWeight: 700, fontSize: '1rem', marginTop: '0.2rem' }}>{result.review_type}</div>
            </div>
          </div>

          {/* Evidence */}
          <div>
            <label className="label-with-icon"><Icon name="fileText" size={14} /> Evidence</label>
            <ul style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {result.evidence.map((e, i) => (
                <li key={i} style={{ lineHeight: 1.5 }}>{e}</li>
              ))}
            </ul>
          </div>

          {/* Rule */}
          <RuleCard
            rule={result.rule_reference}
            retrievedRules={result.retrieved_rules}
            citedRules={result.cited_rules}
          />

          {/* Frames */}
          <FramePreview frames={result.key_frames} />

          {/* Limitations */}
          {result.limitations?.length > 0 && (
            <div style={{ padding: '0.85rem', background: 'rgba(234, 179, 8, 0.05)', borderRadius: '8px', border: '1px solid rgba(234, 179, 8, 0.15)' }}>
              <label className="label-with-icon"><Icon name="alert" size={14} /> Limitations</label>
              <ul style={{ paddingLeft: '1.25rem', fontSize: '0.8rem', color: 'var(--text-dim)', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {result.limitations.map((l, i) => <li key={i}>{l}</li>)}
              </ul>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
