export const getFlagEmoji = (countryCode: string): string =>
  String.fromCodePoint(
    ...countryCode
      .toUpperCase()
      .split("")
      .map((char) => 0x1f1a5 + char.charCodeAt(0))
  );
