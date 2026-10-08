export const playNotificationSound = (): void => {
  try {
    const ctx = new AudioContext();

    const playTone = (freq: number, start: number, duration: number, volume: number) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, ctx.currentTime + start);

      gain.gain.setValueAtTime(0, ctx.currentTime + start);
      gain.gain.linearRampToValueAtTime(volume, ctx.currentTime + start + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + start + duration);

      osc.start(ctx.currentTime + start);
      osc.stop(ctx.currentTime + start + duration);
    };

    // Dos tonos descendentes — chime suave
    playTone(880, 0, 0.18, 0.25);
    playTone(660, 0.12, 0.22, 0.18);

    setTimeout(() => ctx.close(), 600);
  } catch {
    // Browsers sin AudioContext o sin permiso de audio: silencio
  }
};
