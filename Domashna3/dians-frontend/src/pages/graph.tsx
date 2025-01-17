import { lazy, Suspense, useState, useEffect } from "react";
import LineChartComponent from "../content/line_graph";
import Dropdown from "../content/dropdown";
import Item from "../components/item";

import CircularProgress from "@mui/material/CircularProgress";
import Row from "../components/row";

const LazyRowContainer = lazy(() => import("../components/row_container"));

const GraphPage = () => {
  const [selectedStock, setSelectedStock] = useState<string>("");
  const [options, setOptions] = useState<string[]>([]);

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const target = `https://apidians.azurewebsites.net/stocks`;
        const apiUrl = `http://localhost:80/api/proxy`;
        const response = await fetch(apiUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: target,
          }),
        });
        const data = await response.json();
        setOptions(data);

        if (data.length > 0) {
          setSelectedStock(data[0]);
        }
      } catch (error) {
        console.error("Error fetching dropdown options:", error);
      }
    };

    fetchOptions();
  }, []);

  return (
    <Suspense fallback={<CircularProgress />}>
      <LazyRowContainer>
        <Row>
          <Item>
            <Dropdown
              options={options}
              selectedStock={selectedStock}
              onSelectionChange={(stock) => setSelectedStock(stock)}
            />
          </Item>
        </Row>
        <Row>
          <Item>
            {selectedStock && (
              <LineChartComponent selectedStock={selectedStock} />
            )}
          </Item>
        </Row>
      </LazyRowContainer>
    </Suspense>
  );
};

export default GraphPage;
