/**
 * Fingerprint del navegador exigido por Wompi para 3D Secure v2 en pagos con tarjeta
 * (ver skill `wompi-gateway`, Paso 6). `browserTz` sigue la convención EMV 3DS: el
 * mismo valor que entrega `Date.prototype.getTimezoneOffset()`, sin invertir el signo.
 */
export const captureWompiBrowserInfo = () => ({
  browserColorDepth: String(window.screen.colorDepth),
  browserScreenHeight: String(window.screen.height),
  browserScreenWidth: String(window.screen.width),
  browserLanguage: navigator.language,
  browserUserAgent: navigator.userAgent,
  browserTz: String(new Date().getTimezoneOffset()),
});
