import Chart from "react-apexcharts";
import type { ApexOptions } from "apexcharts";
import type { MonthlyBarChartProps } from "@/types/props/chart-props";
import { CHART_BRAND_COLOR } from "@/ui/constants/chart-colors";

/** Bar simple de una serie por mes, estilo BarChartOne.tsx de TailAdmin. */
export const MonthlyBarChart: React.FC<MonthlyBarChartProps> = ({
  categories,
  data,
  seriesName,
  color = CHART_BRAND_COLOR,
  height = 280,
  tooltipFormatter = (val) => `${val} envíos`,
}) => {
  const options: ApexOptions = {
    chart: { type: "bar", toolbar: { show: false }, fontFamily: "Outfit, sans-serif" },
    colors: [color],
    plotOptions: {
      bar: { horizontal: false, columnWidth: "39%", borderRadius: 4, borderRadiusApplication: "end" },
    },
    dataLabels: { enabled: false },
    stroke: { show: true, width: 4, colors: ["transparent"] },
    xaxis: { categories, axisBorder: { show: false }, axisTicks: { show: false } },
    yaxis: { title: { text: undefined } },
    grid: { yaxis: { lines: { show: true } } },
    fill: { opacity: 1 },
    tooltip: { y: { formatter: tooltipFormatter } },
  };

  return (
    <Chart options={options} series={[{ name: seriesName, data }]} type="bar" height={height} />
  );
};
