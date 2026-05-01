export default function Header() {
  return (
    <header className="hero">
      <div className="container">
        <div className="hero-inner">
          <div className="hero-court-mark" aria-hidden="true" />
          <div className="hero-kicker">Charge vs. Block Review</div>
          <h1 className="hero-title">
            Ref<span>Check</span> AI
          </h1>
          <p className="hero-subtitle">
            Upload a basketball clip and get a court-aware review of the original call, visual evidence, rule context, and coach challenge recommendation.
          </p>
          <p className="hero-note">
            Built to explain officiating decisions, not replace officials.
          </p>
        </div>
      </div>
    </header>
  );
}
