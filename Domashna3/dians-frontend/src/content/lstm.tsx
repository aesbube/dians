import { LineChart } from "@mui/x-charts/LineChart";
import { useEffect, useState } from "react";

interface LineChartProps {
  selectedStock: string;
}

const LstmComponent: React.FC<LineChartProps> = ({ selectedStock }) => {
  const [xData, setXData] = useState<string[]>([]);
  const [yData, setYData] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!selectedStock) return;

    const fetchChartData = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:8000/lstm_predict/${selectedStock}`
        );
        const data = await response.json();
        setXData(data[0]);
        setYData(data[1]);
        console.log(xData[0], yData[0]);
      } catch (error) {
        console.error("Error fetching chart data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchChartData();
  }, [selectedStock]);

  return loading ? (
    <p>Loading...</p>
  ) : (
    <LineChart
      series={[{ data: yData, label: "price" }]}
      xAxis={[{ scaleType: "point", data: xData }]}
      width={1000}
      height={600}
      sx={{
        "& .MuiChartsAxis-line ": {
          stroke: "white",
        },
        "&  .MuiChartsAxis-tickLabel": {
          fill: "white",
        },
      }}
    />
  );
};

export default LstmComponent;