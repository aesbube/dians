import { DataGrid } from "@mui/x-data-grid";
import { useEffect, useState } from "react";

interface DataTableProps {
  selectedStock: string;
}

const DataTable: React.FC<DataTableProps> = ({ selectedStock }) => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!selectedStock) return;

    const fetchData = async () => {
      try {
        //   const getCookie = (name: string): string | undefined => {
        //     const value = `; ${document.cookie}`;
        //     const parts = value.split(`; ${name}=`);
        //     if (parts.length === 2) {
        //       return parts.pop()?.split(";").shift();
        //     }
        //     return undefined;
        //   };

        // const apiKey = getCookie("API_KEY");
        const target = `https://apidians.azurewebsites.net/stocks/${selectedStock}`;
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
        const transformedData = data.map(
          (
            item: {
              date: string;
              last_transaction: string;
              max_value: string;
              min_value: string;
              average: string;
              change: string;
              volume: string;
              best_sales: string;
              all_sales: string;
            },
            index: number
          ) => ({
            id: index + 1,
            date: item.date,
            last_transaction: item.last_transaction,
            max_value: item.max_value,
            min_value: item.min_value,
            average: item.average,
            change: item.change,
            volume: item.volume,
            best_sales: item.best_sales,
            all_sales: item.all_sales,
          })
        );

        setRows(transformedData);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedStock]);

  return (
    <DataGrid
      sx={{
        maxHeight: "80%",
        width: "100%",
        bgcolor: "lightgray",
        "& .MuiDataGrid-root": {
          backgroundColor: "lightgray",
        },
      }}
      columns={[
        { field: "date", headerName: "Date", flex: 1 },
        {
          field: "last_transaction",
          headerName: "Last Transaction",
          flex: 1.2,
        },
        { field: "max_value", headerName: "Max Value", flex: 1.2 },
        { field: "min_value", headerName: "Min Value", flex: 1.2 },
        { field: "average", headerName: "Average", flex: 1.2 },
        { field: "change", headerName: "Change", flex: 1 },
        { field: "volume", headerName: "Volume", flex: 1 },
        { field: "best_sales", headerName: "Best Sales", flex: 1.2 },
        { field: "all_sales", headerName: "All Sales", flex: 1.2 },
      ]}
      rows={rows}
      loading={loading}
    />
  );
};

export default DataTable;
