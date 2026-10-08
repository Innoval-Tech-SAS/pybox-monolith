import Chart from "react-apexcharts";
import type { ApexOptions } from "apexcharts";
import type { DonutChartProps } from "@/types/props/chart-props";
import { CHART_DONUT_COLORS } from "@/ui/constants/chart-colors";

/** Donut con texto central (nombre + valor + total), estilo PieChartTwo.tsx de TailAdmin. */
export const DonutChart: React.FC<DonutChartProps> = ({
  series,
  labels,
  colors = CHART_DONUT_COLORS,
  height = 280,
}) => {
  const options: ApexOptions = {
    chart: { type: "donut" },
    labels,
    colors: colors.slice(0, series.length),
    legend: { position: "bottom" },
    dataLabels: { enabled: false },
    plotOptions: {
      pie: {
        donut: {
          size: "70%",
          labels: {
            show: true,
            name: { show: true },
            value: { show: true, formatter: (val) => String(val) },
            total: {
              show: true,
              label: "Total",
              formatter: (w) => String(w.globals.seriesTotals.reduce((a: number, b: number) => a + b, 0)),
            },
          },
        },
      },
    },
  };

  return <Chart options={options} series={series} type="donut" height={height} />;
};
