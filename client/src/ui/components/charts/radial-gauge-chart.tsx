import Chart from "react-apexcharts";
import type { ApexOptions } from "apexcharts";
import type { RadialGaugeChartProps } from "@/types/props/chart-props";
import { CHART_BRAND_COLOR, CHART_TRACK_COLOR } from "@/ui/constants/chart-colors";

/**
 * Gauge semicircular con un solo valor central, estilo MonthlyTarget.tsx de TailAdmin.
 * series=[value] (0-100); el "%" se renderiza vía dataLabels.value.formatter, no HTML superpuesto.
 */
export const RadialGaugeChart: React.FC<RadialGaugeChartProps> = ({
  value,
  label,
  color = CHART_BRAND_COLOR,
  height = 280,
}) => {
  const options: ApexOptions = {
    chart: { type: "radialBar", height, sparkline: { enabled: true } },
    plotOptions: {
      radialBar: {
        startAngle: -85,
        endAngle: 85,
        hollow: { size: "75%" },
        track: { background: CHART_TRACK_COLOR, strokeWidth: "100%", margin: 5 },
        dataLabels: {
          name: { show: false },
          value: {
            fontSize: "32px",
            fontWeight: "600",
            offsetY: -10,
            formatter: (val) => `${val}%`,
          },
        },
      },
    },
    fill: { type: "solid", colors: [color] },
    stroke: { lineCap: "round" },
    labels: [label],
  };

  return <Chart options={options} series={[value]} type="radialBar" height={height} />;
};
