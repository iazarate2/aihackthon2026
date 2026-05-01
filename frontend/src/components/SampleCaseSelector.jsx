export default function SampleCaseSelector({ cases, selected, onSelect }) {
  if (!cases.length) return null;

  return (
    <div style={{ marginTop: '1rem' }}>
      <label>Or Select a Sample Case</label>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {cases.map(c => (
          <button
            key={c.id}
            onClick={() => onSelect(c.id === selected ? null : c.id)}
            className="card"
            style={{
              textAlign: 'left',
              cursor: 'pointer',
              border: c.id === selected ? '2px solid var(--orange)' : '1px solid var(--border)',
              padding: '0.75rem 1rem',
              transition: 'border-color 0.2s',
            }}
          >
            <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{c.title}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.15rem' }}>
              {c.description}
            </div>
            <span className="badge badge-dim" style={{ marginTop: '0.4rem' }}>
              Original: {c.original_call}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
