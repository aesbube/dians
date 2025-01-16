import { Typography } from "@mui/material";
import React, { lazy, useEffect, useState } from "react";
import Row from "../components/row";
import Item from "../components/item";
import Column from "../components/column";

const LazyRowContainer = lazy(() => import("../components/row_container"));

interface TechnicalParametersProps {
  selectedStock: string;
  selectedPeriod: string;
}

const TechnicalParameters: React.FC<TechnicalParametersProps> = ({
  selectedStock,
  selectedPeriod,
}) => {
  const [relativeStrengthIndex, setRelativeStrengthIndex] = useState<number>(0);
  const [momentum, setMomentum] = useState<number>(0);
  const [williamsPercentRange, setWilliamsPercentRange] = useState<number>(0);
  const [stochasticK, setStochasticK] = useState<number>(0);
  const [ultimateOscillator, setUltimateOscillator] = useState<number>(0);
  const [simpleMovingAverage, setSimpleMovingAverage] = useState<number>(0);
  const [exponentialMovingAverage, setExponentialMovingAverage] =
    useState<number>(0);
  const [hullMovingAverage, setHullMovingAverage] = useState<number>(0);
  const [volumeWeightedMovingAverage, setVolumeWeightedMovingAverage] =
    useState<number>(0);
  const [ichimokuBaseLine, setIchimokuBaseLine] = useState<number>(0);
  const [overallSignal, setOverallSignal] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null); 

  useEffect(() => {
    if (!selectedStock) return;

    const fetchTechnicalAnalysisData = async () => {
      try {
        const getCookie = (name: string): string | undefined => {
          const value = `; ${document.cookie}`;
          const parts = value.split(`; ${name}=`);
          if (parts.length === 2) {
            return parts.pop()?.split(";").shift();
          }
          return undefined;
        };

        const apiKey = getCookie("API_KEY");
        if (!apiKey) {
          setError("API key not found.");
          return;
        }
        const response = await fetch(
          "https://apidians.azurewebsites.net/fundamental_analysis/${stock}",
          {
            method: "GET",
            headers: {
              "x-api-key": apiKey?.toString(),
            },
          }
        );

        if (!response.ok) {
          if (response.status === 404) {
            setError("Stock data not found.");
          } else {
            setError("An error occurred while fetching data.");
          }
          console.error(error);
          return;
        }

        const rawData = await response.json();
        const data = rawData[selectedPeriod.toLowerCase()];

        setRelativeStrengthIndex(data["rsi"][0]);
        setMomentum(data["momentum"][0]);
        setWilliamsPercentRange(data["williams_percent_range"][0]);
        setStochasticK(data["stochastic_oscillator"][0]);
        setUltimateOscillator(data["ultimate_oscillator"][0]);
        setSimpleMovingAverage(data["sma"]);
        setExponentialMovingAverage(data["ema"]);
        setHullMovingAverage(data["hull_moving_average"]);
        setVolumeWeightedMovingAverage(data["volume_weighted_average_price"]);
        setIchimokuBaseLine(data["ichimoku_base_line"][0]);
        setOverallSignal(data["overall_signal"]);
      } catch (error) {
        setError("An unexpected error occurred.");
        console.error("Error fetching data for technical analysis:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchTechnicalAnalysisData();
  }, [selectedStock, selectedPeriod]);

  if (loading) {
    return <p>Loading...</p>;
  }

  if (error) {
    return (
      <Typography sx={{ color: "red", textAlign: "center", marginTop: "20px" }}>
        {error}
      </Typography>
    );
  }

  return (
    <>
      <LazyRowContainer sx={{ zIndex: 1 }}>
        <Row sx={{ padding: "20px" }}>
          <Item>
            <Typography sx={{ color: "white" }}>
              Relative Strength Index: {relativeStrengthIndex}
              <br />
              Momentum: {momentum}
              <br />
              Williams Percent Range: {williamsPercentRange}
              <br />
              Stochastic %K: {stochasticK}
              <br />
              Ultimate Oscillator: {ultimateOscillator}
            </Typography>
          </Item>
        </Row>

        <Row sx={{ padding: "20px" }}>
          <Item>
            <Typography sx={{ color: "white" }}>
              Simple Moving Average: {simpleMovingAverage}
              <br />
              Exponential Moving Average: {exponentialMovingAverage}
              <br />
              Hull Moving Average: {hullMovingAverage}
              <br />
              Volume Weighted Moving Average: {volumeWeightedMovingAverage}
              <br />
              Ichimoku Base Line: {ichimokuBaseLine}
            </Typography>
          </Item>
        </Row>
        <Column>
          <Item>
            <Typography sx={{ color: "white" }}>
              Overall Signal: {overallSignal}
            </Typography>
          </Item>
        </Column>
      </LazyRowContainer>
    </>
  );
};

export default TechnicalParameters;
