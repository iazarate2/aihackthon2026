const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function FramePreview({ frames }) {
  if (!frames || frames.length === 0) return null;

  return (
    <div style={{ marginTop: '1rem' }}>
      <label>AI Key Frames</label>
      <div className="frame-grid">
        {frames.map((f, i) => (
          <img key={i} src={`${API}${f}`} alt={`Frame ${i + 1}`} />
        ))}
      </div>
    </div>
  );
}
