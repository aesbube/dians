import express, { Request, Response } from "express";
import dotenv from "dotenv";
import cors from "cors";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  throw new Error("API_KEY is not defined in .env");
}

app.post("/api/proxy", async (req: Request, res: Response) => {
  const { url } = req.body;

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "x-api-key": `${API_KEY}`,
      },
    });

    const data = await response.json();

    res.json(data);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to fetch data from API" });
  }
});

process.on("SIGTERM", () => {
  console.log("SIGTERM received - ignoring");
});

const port = 80;
app.listen(port, () => {
  console.log(`Proxy running on http://localhost:${port}`);
});
