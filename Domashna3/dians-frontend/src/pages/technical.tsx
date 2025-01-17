import { lazy, Suspense, useState, useEffect } from "react";
import Dropdown from "../content/dropdown";
import Item from "../components/item";
import Column from "../components/column";
import CircularProgress from "@mui/material/CircularProgress";
import TechnicalParameters from "../content/technical";
import Row from "../components/row";

const LazyColumnContainer = lazy(
  () => import("../components/column_container")
);

const LazyRowContainer = lazy(() => import("../components/row_container"));

const TechnicalAnalysis = () => {
  const [selectedStock, setSelectedStock] = useState<string>("");
  const [options, setOptions] = useState<string[]>([]);
  const [period, setPeriod] = useState<string[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState<string>("");

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

        const periods = ["Day", "Week", "Month"];
        setPeriod(periods);

        setSelectedPeriod(periods[0]);
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
                <Dropdown
                  options={period}
                  selectedStock={selectedPeriod}
                  onSelectionChange={(period) => setSelectedPeriod(period)}
                />
              </Item>
            </Row>
          </LazyRowContainer>
        </Column>
        <Column>
          <Item>
            <TechnicalParameters
              selectedStock={selectedStock}
              selectedPeriod={selectedPeriod}
            />
          </Item>
        </Column>
      </LazyColumnContainer>
    </Suspense>
  );
};

export default TechnicalAnalysis;
