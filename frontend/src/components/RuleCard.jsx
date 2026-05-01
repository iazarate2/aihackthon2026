export default function RuleCard({ rule }) {
  if (!rule) return null;

  return (
    <div className="card" style={{ marginTop: '1rem', borderColor: 'var(--orange)', borderWidth: '1px' }}>
      <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--orange)', fontWeight: 700, marginBottom: '0.25rem' }}>
        📖 Rule Reference
      </div>
      <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{rule.title}</div>
      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.35rem', lineHeight: 1.5 }}>
        {rule.summary}
      </p>
    </div>
  );
}
