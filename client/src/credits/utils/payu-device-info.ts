/**
 * Antifraude exigido por PayU para PSE/NEQUI/BANCOLOMBIA_TRANSFER (deviceSessionId/
 * cookie/userAgent a nivel de `transaction`, ver `DeviceInfo` en el backend). El
 * fingerprint "oficial" de PayU depende de un objeto Flash (`fp.swf`), inexistente en
 * cualquier navegador desde ~2020 -- no hay forma de replicarlo hoy, así que se manda
 * un UUID por intento de pago como mejor esfuerzo (decisión registrada al agregar
 * Nequi/Botón Bancolombia a PayU).
 */
export const capturePayuDeviceInfo = () => {
  const deviceSessionId = crypto.randomUUID();
  return {
    deviceSessionId,
    cookie: deviceSessionId,
    userAgent: navigator.userAgent,
  };
};
