export default function SampleCaseSelector({ cases, selected, onSelect }) {
  if (!cases.length) return null;

  return (
    <div style={{ marginTop: '1rem' }}>
      <label>Or Select a Sample Case</label>
      <div className="sample-list">
        {cases.map(c => (
          <button
            key={c.id}
            onClick={() => onSelect(c.id === selected ? null : c.id)}
            className={`card sample-card ${c.id === selected ? 'is-selected' : ''}`}
            type="button"
          >
            <div className="sample-title">{c.title}</div>
            <div className="sample-description">
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
