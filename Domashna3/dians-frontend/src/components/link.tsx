import { type LinkProps, Link, styled } from "@mui/material";

const Linked = styled(Link)<LinkProps>(() => ({
  "&:hover": {
    color: "#ffffff",
  },
  color: "#000000",
  textDecoration: "underline",
  textDecorationColor: "#000000",
  textDecorationStyle: "dotted",
}));

export default Linked;