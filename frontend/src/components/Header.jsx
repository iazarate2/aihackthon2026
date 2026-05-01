export default function Header() {
  return (
    <header style={{ padding: '2.5rem 0 1.5rem', textAlign: 'center' }}>
      <h1 style={{ fontSize: '2.25rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
        Ref<span style={{ color: 'var(--orange)' }}>Check</span> AI
      </h1>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '0.25rem' }}>
        Basketball Coach Challenge Review Assistant
      </p>
      <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '0.75rem', maxWidth: 520, margin: '0.75rem auto 0' }}>
        Upload a charge/block clip and see whether the call should be upheld, overturned, or stand as called.
      </p>
      <p style={{ color: 'var(--text-dim)', fontSize: '0.7rem', marginTop: '0.5rem', fontStyle: 'italic' }}>
        RefCheck AI is designed to explain basketball calls, not replace referees.
      </p>
    </header>
  );
}
