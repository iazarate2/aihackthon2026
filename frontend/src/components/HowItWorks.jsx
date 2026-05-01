const STEPS = [
  { num: '1', label: 'Upload Clip', icon: '🎥' },
  { num: '2', label: 'AI Analyzes', icon: '🤖' },
  { num: '3', label: 'Compare Rulebook', icon: '📖' },
  { num: '4', label: 'Return Verdict', icon: '⚖️' },
];

export default function HowItWorks() {
  return (
    <section>
      <div className="container">
        <h2 className="section-heading">How It Works</h2>
        <div className="steps-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem' }}>
          {STEPS.map(s => (
            <div key={s.num} className="card" style={{ textAlign: 'center', padding: '1rem' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{s.icon}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--orange)', fontWeight: 700 }}>Step {s.num}</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
