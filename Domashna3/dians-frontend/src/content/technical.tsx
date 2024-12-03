import { Typography } from "@mui/material";
import { lazy } from "react";
import Row from "../components/row";
import Item from "../components/item";

const LazyRowContainer = lazy(() => import("../components/row_container"));

const TechnicalParameters = () => {
  return (
    <LazyRowContainer sx={{zIndex:1}}>
      <Row sx={{padding:"20px"}}>
        <Item>
          <Typography sx={{ color: "white" }}>
            Relative Strength Index (RSI): 63.71
            <br />
            Momentum (10): 11.02
            <br />
            Williams Percent Range (14): -23.09
            <br />
            Stochastic %K (14, 3, 3): 78.64
            <br />
            Ultimate Oscillator (7, 14, 28): 47.74
          </Typography>
        </Item>
      </Row>
        
      <Row sx={{padding:"20px"}}>
        <Item>
          <Typography sx={{ color: "white" }}>
            Simple Moving Average (10): 344.20
            <br />
            Exponential Moving Average (10): 341.18
            <br />
            Hull Moving Average (9): 349.43
            <br />
            Volume Weighted Moving Average (20): 326.99
            <br />
            Ichimoku Base Line (9, 26, 52, 26): 300.40
          </Typography>
        </Item>
      </Row>
    </LazyRowContainer>
  );
};

export default TechnicalParameters;
