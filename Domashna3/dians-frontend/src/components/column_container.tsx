import { Container, styled } from "@mui/material";
import { css } from "@emotion/react";

const fadeInAnimation = css`
  animation: fadeIn 1s ease-in-out;
`;

const ColumnContainer = styled(Container)({
  display: "flex",
  alignItems: "strech",
  justifyContent: "center",
  width: "100%",
  height: "100vh",
  padding: "15px",
  flexDirection: "column",
  animation: `${fadeInAnimation};`,
});

export default ColumnContainer;