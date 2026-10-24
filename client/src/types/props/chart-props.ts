export interface RadialGaugeChartProps {
  /** Valor 0-100 a mostrar en el gauge. */
  value: number;
  /** Etiqueta interna usada por ApexCharts (no se renderiza visible, solo accesibilidad). */
  label: string;
  color?: string;
  height?: number;
}

export interface DonutChartProps {
  series: number[];
  labels: string[];
  colors?: string[];
  height?: number;
}

export interface MonthlyBarChartProps {
  categories: string[];
  data: number[];
  seriesName: string;
  color?: string;
  height?: number;
  /** Formatea el valor en el tooltip; por defecto `"${val} envíos"`. */
  tooltipFormatter?: (value: number) => string;
}
