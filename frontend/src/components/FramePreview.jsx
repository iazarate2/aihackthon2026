import { useEffect, useRef, useState } from 'react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function FramePreview({ frames }) {
  const [activeFrame, setActiveFrame] = useState(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!activeFrame) return;

    function handleKeyDown(e) {
      if (e.key === 'Escape') setActiveFrame(null);
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeFrame]);

  function toggleFrame(index, src) {
    if (activeFrame?.index === index) {
      setActiveFrame(null);
      return;
    }

    setActiveFrame({
      index,
      src,
    });
  }

  if (!frames || frames.length === 0) return null;

  return (
    <div ref={containerRef} className="frame-preview">
      <label>AI Key Frames</label>
      <div className="frame-grid">
        {frames.map((f, i) => {
          const src = `${API}${f}`;
          const isActive = activeFrame?.index === i;

          return (
            <div key={i} className={`frame-item ${isActive ? 'is-active' : ''}`}>
              <button
                className="frame-button"
                type="button"
                onClick={() => toggleFrame(i, src)}
                aria-expanded={isActive}
                aria-label={`${isActive ? 'Collapse' : 'Expand'} frame ${i + 1}`}
              >
                <img src={src} alt={`Frame ${i + 1}`} />
              </button>
            </div>
          );
        })}
      </div>

      {activeFrame && (
        <div className="frame-popover">
          <img src={activeFrame.src} alt={`Expanded frame ${activeFrame.index + 1}`} />
        </div>
      )}
    </div>
  );
}
