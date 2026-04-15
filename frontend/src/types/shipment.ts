export interface WarehouseConfigItem {
  allocation_pct: number;
  transit_days: number;
}

export interface WarehouseConfigInput {
  west: WarehouseConfigItem;
  central: WarehouseConfigItem;
  east: WarehouseConfigItem;
}

export interface WarehouseConfigResponse {
  id: number;
  region: string;
  region_label: string;
  allocation_pct: number;
  transit_days: number;
}

export interface ShipmentUnitResponse {
  id: number;
  batch_id: number;
  region: string;
  quantity: number;
  transit_days: number;
  ship_date: string;
  arrival_date: string;
  status: string;
}

export interface ShipmentBatchInput {
  batch_index: number;
  ship_date: string;
  batch_quantity: number;
}

export interface ShipmentBatchResponse {
  id: number;
  batch_index: number;
  ship_date: string;
  batch_quantity: number;
  units: ShipmentUnitResponse[];
}

export interface ShipmentPlanCreate {
  plan_name: string;
  sku?: string;
  asin?: string;
  total_quantity: number;
  batch_count: number;
  warehouse_config: WarehouseConfigInput;
  batches: ShipmentBatchInput[];
  notes?: string;
}

export interface ShipmentPlanUpdate {
  plan_name?: string;
  sku?: string;
  asin?: string;
  total_quantity?: number;
  status?: string;
  notes?: string;
}

export interface ShipmentPlanResponse {
  id: number;
  plan_name: string;
  sku: string | null;
  asin: string | null;
  total_quantity: number;
  batch_count: number;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  warehouse_configs: WarehouseConfigResponse[];
  batches: ShipmentBatchResponse[];
}

export interface ShipmentPlanListItem {
  id: number;
  plan_name: string;
  sku: string | null;
  asin: string | null;
  total_quantity: number;
  batch_count: number;
  status: string;
  created_at: string;
}
