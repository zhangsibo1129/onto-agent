import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from "typeorm"

export enum DatasourceType {
  POSTGRESQL = "postgresql",
  MYSQL = "mysql",
  SQLSERVER = "sqlserver",
  ORACLE = "oracle",
}

export enum DatasourceStatus {
  CONNECTED = "connected",
  DISCONNECTED = "disconnected",
  ERROR = "error",
}

@Entity("datasources")
export class Datasource {
  @PrimaryGeneratedColumn("uuid")
  id!: string

  @Column()
  name!: string

  @Column({ type: "varchar", length: 50 })
  type!: DatasourceType

  @Column({ type: "varchar", length: 255, nullable: true })
  host!: string | null

  @Column({ type: "int", nullable: true })
  port!: number | null

  @Column({ type: "varchar", length: 100, nullable: true })
  database!: string | null

  @Column({ type: "varchar", length: 100, nullable: true })
  schema!: string | null

  @Column({ type: "varchar", length: 100, nullable: true })
  username!: string | null

  @Column({ type: "text", nullable: true })
  password!: string | null

  @Column({ type: "varchar", length: 50, nullable: true })
  sslMode!: string | null

  @Column({
    type: "varchar",
    length: 50,
    default: DatasourceStatus.DISCONNECTED,
  })
  status!: DatasourceStatus

  @Column({ type: "int", default: 0 })
  tableCount!: number

  @Column({ type: "timestamp", nullable: true })
  lastSyncAt!: Date | null

  @CreateDateColumn()
  createdAt!: Date

  @UpdateDateColumn()
  updatedAt!: Date
}
