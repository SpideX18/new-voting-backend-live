import React, { useState } from 'react';
import theme from '../styles/theme';
import { useStudy } from '../context/StudyContext';
import { useAuth } from '../context/AuthContext';
import { sm2Update } from '../utils/aiEngine';
import { Card, Button, PageHeader, EmptyState, Pill } from '../components/UI';

const T = theme;

const FlashCard = ({ card, index, total, onRate, flipped, setFlipped }) => {
  return (
    <div>
      {/* Progress */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <span style={{ fontSize: '0.82rem', color: T.muted }}>Card {index + 1} of {total}</span>
        <div style={{ display: 'flex', gap: 4 }}>
          {Array.from({ length: total }).map((_, i) => (
            <div key={i} style={{ width: 8, height: 8, borderRadius: '50%', background: i === index ? T.accent : T.border }} />
          ))}
        </div>
      </div>

      {/* Card flip */}
      <div onClick={() => setFlipped((f) => !f)}
        style={{
          minHeight: 220, borderRadius: 16, cursor: 'pointer',
          background: flipped
            ? `linear-gradient(135deg, rgba(61,142,240,.12), rgba(108,71,255,.12))`
            : T.surface2,
          border: `2px solid ${flipped ? T.accent : T.border}`,
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', padding: 32, textAlign: 'center',
          transition: 'all .3s ease', position: 'relative',
        }}>
        <div style={{ position: 'absolute', top: 14, right: 14, fontSize: '0.72rem', color: T.muted }}>
          {flipped ? 'Definition' : 'Term'} — click to flip
        </div>

        {!flipped ? (
          <>
            <div style={{ fontSize: '2.5rem', marginBottom: 14 }}>🃏</div>
            <div style={{ fontFamily: T.fontHead, fontWeight: 800, fontSize: '1.5rem', color: T.accent }}>
              {card.term}
            </div>
            <p style={{ color: T.muted, fontSize: '0.82rem', marginTop: 10 }}>Tap to reveal definition</p>
          </>
        ) : (
          <>
            <div style={{ fontSize: '1.8rem', marginBottom: 12 }}>📖</div>
            <p style={{ fontSize: '0.92rem', lineHeight: 1.75, color: T.text, maxWidth: 460 }}>
              {card.definition}
            </p>
          </>
        )}
      </div>

      {/* SM-2 rating buttons (only shown after flip) */}
      {flipped && (
        <div style={{ marginTop: 18 }}>
          <p style={{ fontSize: '0.78rem', color: T.muted, marginBottom: 12, textAlign: 'center' }}>
            How well did you know this? (SM-2 Spaced Repetition)
          </p>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
            {[
              { q: 0, label: "Didn't know",  color: T.red    },
              { q: 2, label: 'Almost',        color: T.yellow },
              { q: 3, label: 'With effort',   color: T.accent },
              { q: 5, label: 'Perfect',        color: T.green  },
            ].map(({ q, label, color }) => (
              <button key={q} onClick={(e) => { e.stopPropagation(); onRate(q); }}
                style={{
                  padding: '10px 18px', borderRadius: 9, border: `1px solid ${color}`,
                  background: `${color}18`, color, cursor: 'pointer', fontSize: '0.85rem',
                  fontFamily: T.fontBody, fontWeight: 600, transition: 'all .15s',
                }}>
                {label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const FlashcardsPage = ({ onNavigate }) => {
  const { flashcards, studyContent } = useStudy();
  const { user, updateQuizHistory }  = useAuth();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped,       setFlipped]      = useState(false);
  const [srItems,       setSrItems]      = useState({});
  const [completed,     setCompleted]    = useState([]);
  const [sessionDone,   setSessionDone]  = useState(false);

  const handleRate = (quality) => {
    const card    = flashcards[currentIndex];
    const key     = `fc_${card.term.toLowerCase().replace(/\s+/g, '_')}`;
    const current = srItems[key] || { easiness: 2.5, interval: 1, repetitions: 0 };
    const updated = sm2Update(current, quality);
    setSrItems((prev) => ({ ...prev, [key]: { ...updated, term: card.term } }));
    setCompleted((prev) => [...prev, { term: card.term, quality }]);

    // Always reset flip to front before moving to next card
    setFlipped(false);

    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex((i) => i + 1);
    } else {
      setSessionDone(true);
    }
  };

  if (!studyContent || !flashcards.length) {
    return (
      <EmptyState icon="🃏" title="No flashcards yet"
        subtitle="Upload study material to auto-generate flashcards from your notes."
        action={<Button onClick={() => onNavigate('upload')}>Upload Material →</Button>} />
    );
  }

  const qualityLabel = (q) => q >= 4 ? '✅ Perfect' : q >= 3 ? '👍 Good' : q >= 2 ? '⚠️ Almost' : '❌ Missed';
  const qualityColor = (q) => q >= 4 ? T.green : q >= 3 ? T.accent : q >= 2 ? T.yellow : T.red;

  if (sessionDone) {
    const perfectCount = completed.filter((c) => c.quality >= 4).length;
    const missedCount  = completed.filter((c) => c.quality < 3).length;

    return (
      <div>
        <PageHeader title="Flashcard Session Complete 🎉" subtitle="Here's how you did" />
        <Card className="fade-up" style={{ textAlign: 'center', marginBottom: 20, padding: '32px 24px' }}>
          <div style={{ fontFamily: T.fontHead, fontSize: '3rem', fontWeight: 800, color: T.accent, marginBottom: 8 }}>
            {flashcards.length}
          </div>
          <p style={{ color: T.muted }}>cards reviewed</p>
          <div style={{ display: 'flex', gap: 20, justifyContent: 'center', marginTop: 20 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontFamily: T.fontHead, fontSize: '1.6rem', fontWeight: 800, color: T.green }}>{perfectCount}</div>
              <div style={{ fontSize: '0.78rem', color: T.muted }}>Remembered</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontFamily: T.fontHead, fontSize: '1.6rem', fontWeight: 800, color: T.red }}>{missedCount}</div>
              <div style={{ fontSize: '0.78rem', color: T.muted }}>To review</div>
            </div>
          </div>
          <div style={{ marginTop: 22, display: 'flex', gap: 10, justifyContent: 'center' }}>
            <Button onClick={() => { setCurrentIndex(0); setCompleted([]); setSessionDone(false); setFlipped(false); }}>
              Restart Session
            </Button>
            <Button variant="ghost" onClick={() => onNavigate('quiz')}>Take Mock Test →</Button>
          </div>
        </Card>

        <h3 style={{ fontFamily: T.fontHead, fontWeight: 700, fontSize: '0.9rem', color: T.muted, marginBottom: 12, letterSpacing: 1 }}>SESSION BREAKDOWN</h3>
        {completed.map((c, i) => (
          <Card key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10, padding: '12px 18px' }}>
            <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{c.term}</span>
            <span style={{ fontSize: '0.82rem', color: qualityColor(c.quality), fontWeight: 600 }}>{qualityLabel(c.quality)}</span>
          </Card>
        ))}

        {missedCount > 0 && (
          <div style={{ marginTop: 16, background: 'rgba(240,96,96,.06)', border: `1px solid rgba(240,96,96,.2)`, borderRadius: 10, padding: '14px 18px' }}>
            <p style={{ fontSize: '0.84rem', color: T.red, marginBottom: 8, fontWeight: 600 }}>⚠️ SM-2 suggests reviewing these soon:</p>
            {completed.filter((c) => c.quality < 3).map((c, i) => (
              <p key={i} style={{ fontSize: '0.82rem', color: T.muted, marginBottom: 4 }}>• {c.term}</p>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div>
      <PageHeader title="Flashcards" subtitle="AI-generated term–definition cards with SM-2 spaced repetition rating" />
      <div className="fade-up-2">
        <FlashCard
          card={flashcards[currentIndex]}
          index={currentIndex}
          total={flashcards.length}
          onRate={handleRate}
          flipped={flipped}
          setFlipped={setFlipped}
        />
      </div>
      <div style={{ marginTop: 20, display: 'flex', gap: 10, justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <Button variant="ghost"
          onClick={() => { setCurrentIndex((i) => Math.max(0, i - 1)); setFlipped(false); }}
          disabled={currentIndex === 0}>
          ← Previous
        </Button>
        <Button variant="ghost"
          onClick={() => { setCurrentIndex((i) => Math.min(flashcards.length - 1, i + 1)); setFlipped(false); }}
          disabled={currentIndex === flashcards.length - 1}>
          Skip →
        </Button>
      </div>
    </div>
  );
};

export default FlashcardsPage;
