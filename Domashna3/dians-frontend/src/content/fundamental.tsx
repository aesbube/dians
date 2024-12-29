import { Typography } from "@mui/material";
import React, { useState, useEffect } from "react";

interface FundamentalProps {
  stock: string;
}

const Fundamental: React.FC<FundamentalProps> = ({ stock }) => {
  const [isFundamental, setIsFundamental] = useState<boolean | null>(null);

  useEffect(() => {
    const fetchFundamentalAnalysis = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/fundamental_analysis/${stock}`
        );
        const result = await response.json();
        setIsFundamental(result === 1);
      } catch (error) {
        console.error("Error fetching fundamental analysis:", error);
        setIsFundamental(false);
      }
    };

    fetchFundamentalAnalysis();
  }, [stock]);

  if (isFundamental === null) {
    return <div>Loading...</div>;
  }

  return (
    <Typography variant="h6" sx={{ zIndex: 1, color: "white" }}>
      {isFundamental
        ? "Според анализата на последниот финансиски извештај препорачано е да се купи"
        : "Според анализата на последниот финансиски извештај препорачано е да се продаде"}
    </Typography>
  );
};

export default Fundamental;
