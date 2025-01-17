import { lazy, Suspense, useState, useEffect } from "react";
import Dropdown from "../content/dropdown";
import Item from "../components/item";
import CircularProgress from "@mui/material/CircularProgress";
import Row from "../components/row";
import LstmComponent from "../content/lstm";

const LazyRowContainer = lazy(() => import("../components/row_container"));

const Prediction = () => {
  const [selectedStock, setSelectedStock] = useState<string>("");
  const [options, setOptions] = useState<string[]>([]);

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const target = `https://apidians.azurewebsites.net/stocks`;
        const apiUrl = `https://proxydians.azurewebsites.net/api/proxy`;
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
            {selectedStock && <LstmComponent selectedStock={selectedStock} />}
          </Item>
        </Row>
      </LazyRowContainer>
    </Suspense>
  );
};

export default Prediction;
