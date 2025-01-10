import { Typography } from "@mui/material";
import React, { useState, useEffect } from "react";

interface FundamentalProps {
  stock: string;
}

const Fundamental: React.FC<FundamentalProps> = ({ stock }) => {
  const [isFundamental, setIsFundamental] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const fetchFundamentalAnalysis = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/fundamental_analysis/${stock}`
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

        setError(null);

        const result = await response.json();
        setIsFundamental(result === 1);
      } catch (error) {
        setError("An unexpected error occurred.");
        console.error("Error fetching data for technical analysis:", error);
        setIsFundamental(false);
      } finally {
        setLoading(false);
      }
    };

    fetchFundamentalAnalysis();
  }, [stock]);

  if (error) {
    return (
      <Typography sx={{ color: "red", textAlign: "center", marginTop: "20px" }}>
        {error}
      </Typography>
    );
  }

  if (loading) {
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
