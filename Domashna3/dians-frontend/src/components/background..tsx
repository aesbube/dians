import { styled } from "@mui/system";
import Paper from "@mui/material/Paper";

const BackgroundContainer = styled(Paper)({
    borderRadius: 0,
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    overflow: "hidden",
    backgroundColor: "#191a1c",
  });

export default BackgroundContainer;