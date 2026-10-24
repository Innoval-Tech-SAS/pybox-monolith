const capitalize = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

export const formatTodayLong = (now: Date = new Date()): string =>
  capitalize(now.toLocaleDateString("es-CO", { weekday: "long", day: "numeric", month: "long" }));

export const formatOperationSubtitle = (orgNames: string[]): string => {
  if (orgNames.length === 0) return "Cuando administres una empresa, aquí verás su operación al día.";
  if (orgNames.length === 1) {
    return `Así va ${orgNames[0]} hoy: cédulas cargadas, portafolios y envíos.`;
  }
  return `Así van tus ${orgNames.length} empresas hoy: cédulas cargadas, portafolios y envíos.`;
};

export const PORTFOLIO_DASHBOARD_SUBTITLE =
  "Así va cada portafolio al que tienes acceso: titulares, codeudores y envíos.";
