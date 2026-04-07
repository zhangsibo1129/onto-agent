import { Request, Response } from "express"
import { datasourceService } from "../services/datasourceService"
import { DatasourceType } from "../entities/Datasource"

export const datasourceController = {
  async list(req: Request, res: Response) {
    try {
      const datasources = await datasourceService.findAll()
      res.json({
        success: true,
        data: datasources,
      })
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: error.message,
        },
      })
    }
  },

  async get(req: Request, res: Response) {
    try {
      const { id } = req.params
      const datasource = await datasourceService.findById(id)

      if (!datasource) {
        return res.status(404).json({
          success: false,
          error: {
            code: "DATASOURCE_NOT_FOUND",
            message: "数据源不存在",
          },
        })
      }

      res.json({
        success: true,
        data: datasource,
      })
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: error.message,
        },
      })
    }
  },

  async create(req: Request, res: Response) {
    try {
      const { name, type, host, port, database, schema, username, password, sslMode } = req.body

      if (!name || !type) {
        return res.status(400).json({
          success: false,
          error: {
            code: "INVALID_REQUEST",
            message: "名称和类型为必填项",
          },
        })
      }

      if (!Object.values(DatasourceType).includes(type)) {
        return res.status(400).json({
          success: false,
          error: {
            code: "INVALID_REQUEST",
            message: "不支持的数据源类型",
          },
        })
      }

      const datasource = await datasourceService.create({
        name,
        type,
        host,
        port,
        database,
        schema,
        username,
        password,
        sslMode,
      })

      res.status(201).json({
        success: true,
        data: datasource,
      })
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: error.message,
        },
      })
    }
  },

  async update(req: Request, res: Response) {
    try {
      const { id } = req.params
      const { name, type, host, port, database, schema, username, password, sslMode } = req.body

      const datasource = await datasourceService.update(id, {
        name,
        type,
        host,
        port,
        database,
        schema,
        username,
        password,
        sslMode,
      })

      if (!datasource) {
        return res.status(404).json({
          success: false,
          error: {
            code: "DATASOURCE_NOT_FOUND",
            message: "数据源不存在",
          },
        })
      }

      res.json({
        success: true,
        data: datasource,
      })
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: error.message,
        },
      })
    }
  },

  async delete(req: Request, res: Response) {
    try {
      const { id } = req.params
      const deleted = await datasourceService.delete(id)

      if (!deleted) {
        return res.status(404).json({
          success: false,
          error: {
            code: "DATASOURCE_NOT_FOUND",
            message: "数据源不存在",
          },
        })
      }

      res.json({
        success: true,
        data: null,
      })
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: error.message,
        },
      })
    }
  },

  async test(req: Request, res: Response) {
    try {
      const { id } = req.params
      const result = await datasourceService.testConnection(id)

      if (!result.connected) {
        return res.status(200).json({
          success: true,
          data: {
            connected: false,
            error: result.error,
          },
        })
      }

      res.json({
        success: true,
        data: result,
      })
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: error.message,
        },
      })
    }
  },

  async getTables(req: Request, res: Response) {
    try {
      const { id } = req.params
      const datasource = await datasourceService.findById(id)

      if (!datasource) {
        return res.status(404).json({
          success: false,
          error: {
            code: "DATASOURCE_NOT_FOUND",
            message: "数据源不存在",
          },
        })
      }

      const tables = await datasourceService.getTables(datasource)

      res.json({
        success: true,
        data: {
          tables,
          scannedAt: new Date().toISOString(),
        },
      })
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: {
          code: "DATASOURCE_CONNECTION_FAILED",
          message: error.message,
        },
      })
    }
  },

  async getColumns(req: Request, res: Response) {
    try {
      const { id, tableName } = req.params
      const datasource = await datasourceService.findById(id)

      if (!datasource) {
        return res.status(404).json({
          success: false,
          error: {
            code: "DATASOURCE_NOT_FOUND",
            message: "数据源不存在",
          },
        })
      }

      const columns = await datasourceService.getColumns(datasource, tableName)

      res.json({
        success: true,
        data: {
          tableName,
          columns,
        },
      })
    } catch (error: any) {
      res.status(500).json({
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: error.message,
        },
      })
    }
  },
}
