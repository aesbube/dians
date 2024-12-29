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
        const response = await fetch("http://localhost:8000/stocks");
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
          <Item>
            <Fundamental stock={selectedStock} />
          </Item>
        </Column>
      </LazyColumnContainer>
    </Suspense>
  );
};

export default FundamentalAnalysis;
