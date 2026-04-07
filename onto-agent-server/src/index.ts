import "reflect-metadata"
import express from "express"
import cors from "cors"
import { DataSource } from "typeorm"
import { datasourceRouter } from "./routes/datasource"
import { Datasource } from "./entities/Datasource"

const app = express()
const PORT = process.env.PORT || 3001

app.use(cors())
app.use(express.json())

export const AppDataSource = new DataSource({
  type: "postgres",
  host: process.env.PG_HOST || "localhost",
  port: parseInt(process.env.PG_PORT || "5432"),
  username: process.env.PG_USER || "postgres",
  password: process.env.PG_PASSWORD || "postgres",
  database: process.env.PG_DATABASE || "ontoagent",
  synchronize: true,
  logging: true,
  entities: [Datasource],
})

AppDataSource.initialize()
  .then(() => {
    console.log("Database connected")
  })
  .catch((err) => {
    console.error("Database connection error:", err)
  })

app.use("/api/datasources", datasourceRouter)

app.get("/api/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() })
})

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`)
})
