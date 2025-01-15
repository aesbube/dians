import { lazy, Suspense, useState, useEffect } from "react";
import Dropdown from "../content/dropdown";
import Item from "../components/item";
import CircularProgress from "@mui/material/CircularProgress";
import Row from "../components/row";
import LstmComponent from "../content/lstm";


const LazyRowContainer = lazy(
  () => import("../components/row_container")
);

const Prediction = () => {
  const [selectedStock, setSelectedStock] = useState<string>("");
  const [options, setOptions] = useState<string[]>([]);

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const response = await fetch(
          "https://apidians.azurewebsites.net/stocks",
          {
            method: "GET",
            headers: {
              "x-api-key": import.meta.env.VITE_API_KEY,
            },
          }
        );
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
            <LstmComponent selectedStock={selectedStock} />
          )}
        </Item>
        </Row>
      </LazyRowContainer>
    </Suspense>
  );
};

export default Prediction;

