const STEPS = [
  { num: '1', label: 'Upload Clip', icon: '01' },
  { num: '2', label: 'AI Reviews', icon: '02' },
  { num: '3', label: 'Rulebook Check', icon: '03' },
  { num: '4', label: 'Verdict', icon: '04' },
];

export default function HowItWorks() {
  return (
    <section>
      <div className="container">
        <h2 className="section-heading">How It Works</h2>
        <div className="steps-grid">
          {STEPS.map(s => (
            <div key={s.num} className="card step-card">
              <div className="step-icon">{s.icon}</div>
              <div className="step-num">Step {s.num}</div>
              <div className="step-label">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
