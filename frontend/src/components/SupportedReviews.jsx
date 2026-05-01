import Icon from './Icon';

const ACTIVE = ['Charge vs. Block'];
const COMING = ['Shooting Foul', 'Out of Bounds', 'Goaltending', 'Traveling', 'Flagrant Foul'];

const CHECKS = [
  'Accepts short sports video',
  'Uses AI / multimodal analysis',
  'Compares play to rules',
  'Returns clear verdict',
  'Explains reasoning',
  'Supports basketball well',
  'Public GitHub ready',
  'Deploy ready',
];

export default function SupportedReviews() {
  return (
    <section>
      <div className="container supported-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Supported reviews */}
        <div>
          <h2 style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-dim)', marginBottom: '0.75rem' }}>
            Supported Reviews
          </h2>
          {ACTIVE.map(r => (
            <div key={r} className="badge badge-green badge-with-icon" style={{ marginBottom: '0.4rem' }}>
              <Icon name="check" size={14} /> {r}
            </div>
          ))}
          <div style={{ marginTop: '0.75rem' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Coming Soon</span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.35rem' }}>
              {COMING.map(r => (
                <span key={r} className="badge badge-dim badge-with-icon" style={{ opacity: 0.5 }}>
                  <Icon name="lock" size={13} /> {r}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Hackathon checklist */}
        <div>
          <h2 style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-dim)', marginBottom: '0.75rem' }}>
            Hackathon Requirements
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            {CHECKS.map(c => (
              <div key={c} style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Icon name="check" size={14} style={{ color: 'var(--green)', flex: '0 0 auto' }} /> {c}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
