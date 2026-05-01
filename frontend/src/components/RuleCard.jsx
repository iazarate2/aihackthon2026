export default function RuleCard({ rule, retrievedRules = [], citedRules = [] }) {
  if (!rule) return null;
  const citedIds = new Set(citedRules.map(r => r.id));
  const rulesToShow = retrievedRules.length ? retrievedRules : citedRules;
  const sourceLinks = [
    rule.source_url && { label: 'NBA Rulebook', href: rule.source_url },
    rule.video_rulebook_url && { label: 'NBA Video Rulebook', href: rule.video_rulebook_url },
  ].filter(Boolean);

  return (
    <div className="card" style={{ marginTop: '1rem', borderColor: 'var(--orange)', borderWidth: '1px' }}>
      <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--orange)', fontWeight: 700, marginBottom: '0.25rem' }}>
        Official Rule Reference
      </div>
      <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{rule.title}</div>
      {rule.source_label && (
        <div style={{ color: 'var(--orange)', fontSize: '0.75rem', marginTop: '0.25rem', fontWeight: 700 }}>
          {rule.source_label}
        </div>
      )}
      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.35rem', lineHeight: 1.5 }}>
        {rule.summary}
      </p>
      {sourceLinks.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
          {sourceLinks.map(link => (
            <a
              key={link.href}
              href={link.href}
              target="_blank"
              rel="noreferrer"
              className="badge badge-orange"
              style={{ textDecoration: 'none' }}
            >
              {link.label}
            </a>
          ))}
        </div>
      )}

      {rulesToShow.length > 0 && (
        <div style={{ marginTop: '1rem' }}>
          <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-dim)', fontWeight: 700, marginBottom: '0.5rem' }}>
            Retrieved Rule Context
          </div>
          <div style={{ display: 'grid', gap: '0.5rem' }}>
            {rulesToShow.map(r => (
              <div key={r.id} style={{ padding: '0.75rem', border: '1px solid var(--border)', borderRadius: 8, background: 'rgba(5, 8, 13, 0.45)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.75rem', alignItems: 'center' }}>
                  <strong style={{ fontSize: '0.82rem' }}>{r.title}</strong>
                  {citedIds.has(r.id) && <span className="badge badge-orange">Cited</span>}
                </div>
                {r.source_label && (
                  <div style={{ color: 'var(--orange)', fontSize: '0.68rem', marginTop: '0.2rem', fontWeight: 700 }}>
                    {r.source_label}
                  </div>
                )}
                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.25rem', lineHeight: 1.45 }}>
                  {r.summary}
                </p>
                {(r.source_url || r.video_rulebook_url) && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.55rem' }}>
                    {r.source_url && (
                      <a href={r.source_url} target="_blank" rel="noreferrer" className="badge badge-dim" style={{ textDecoration: 'none' }}>
                        NBA Rulebook
                      </a>
                    )}
                    {r.video_rulebook_url && (
                      <a href={r.video_rulebook_url} target="_blank" rel="noreferrer" className="badge badge-dim" style={{ textDecoration: 'none' }}>
                        Video Rulebook
                      </a>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
