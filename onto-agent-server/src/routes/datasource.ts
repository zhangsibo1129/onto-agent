import { Router } from "express"
import { datasourceController } from "../controllers/datasourceController"

const router = Router()

router.get("/", datasourceController.list)
router.get("/:id", datasourceController.get)
router.post("/", datasourceController.create)
router.put("/:id", datasourceController.update)
router.delete("/:id", datasourceController.delete)
router.post("/:id/test", datasourceController.test)
router.get("/:id/tables", datasourceController.getTables)
router.get("/:id/tables/:tableName/columns", datasourceController.getColumns)

export { router as datasourceRouter }
