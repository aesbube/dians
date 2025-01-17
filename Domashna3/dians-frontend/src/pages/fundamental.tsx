import { lazy, Suspense, useState, useEffect } from "react";
import Dropdown from "../content/dropdown";
import Item from "../components/item";
import CircularProgress from "@mui/material/CircularProgress";
import Column from "../components/column";
import Fundamental from "../content/fundamental";

const LazyColumnContainer = lazy(
  () => import("../components/column_container")
);

const FundamentalAnalysis = () => {
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
      <LazyColumnContainer>
        <Column>
          <Item>
            <Dropdown
              options={options}
              selectedStock={selectedStock}
              onSelectionChange={(stock) => setSelectedStock(stock)}
            />
          </Item>
        </Column>
        <Column>
          <Item>{selectedStock && <Fundamental stock={selectedStock} />}</Item>
        </Column>
      </LazyColumnContainer>
    </Suspense>
  );
};

export default FundamentalAnalysis;
