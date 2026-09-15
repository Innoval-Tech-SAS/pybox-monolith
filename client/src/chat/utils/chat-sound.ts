let _ctx: AudioContext | null = null;

function getCtx(): AudioContext {
  if (!_ctx) _ctx = new AudioContext();
  return _ctx;
}

function playBeeps(ctx: AudioContext): void {
  const now = ctx.currentTime;

  const beep = (start: number, freq: number) => {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.25, start);
    gain.gain.exponentialRampToValueAtTime(0.001, start + 0.18);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(start);
    osc.stop(start + 0.18);
  };

  beep(now, 880);
  beep(now + 0.15, 1100);
}

export function playMessageSound(): void {
  try {
    const ctx = getCtx();
    if (ctx.state === "suspended") {
      ctx.resume().then(() => playBeeps(ctx)).catch(() => {});
    } else {
      playBeeps(ctx);
    }
  } catch {
    // ignore — browser policy may block audio
  }
}
