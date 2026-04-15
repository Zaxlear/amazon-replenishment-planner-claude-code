export interface SalesPlanCreate {
  plan_name: string;
  sku?: string;
  asin?: string;
  start_date: string;
  end_date: string;
  initial_inventory: number;
  shipment_plan_id?: number | null;
}

export interface SalesPlanUpdate {
  plan_name?: string;
  sku?: string;
  asin?: string;
  start_date?: string;
  end_date?: string;
  initial_inventory?: number;
  shipment_plan_id?: number | null;
}

export interface SalesPlanResponse {
  id: number;
  plan_name: string;
  sku: string | null;
  asin: string | null;
  start_date: string;
  end_date: string;
  initial_inventory: number;
  shipment_plan_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface SalesPlanListItem {
  id: number;
  plan_name: string;
  sku: string | null;
  asin: string | null;
  start_date: string;
  end_date: string;
  initial_inventory: number;
  shipment_plan_id: number | null;
  created_at: string;
}

export interface DailySalesInput {
  entry_date: string;
  planned_sales: number;
}

export interface DailySalesBatchInput {
  start_date: string;
  end_date: string;
  daily_sales: number;
}

export interface OverrideCreate {
  override_date: string;
  override_value: number;
  reason?: string;
}

export interface OverrideResponse {
  id: number;
  override_date: string;
  override_value: number;
  reason: string | null;
  created_at: string;
}

export interface ArrivalDetail {
  unit_label: string;
  quantity: number;
}

export interface DailyCalculationResult {
  date: string;
  opening_stock: number;
  arrivals: number;
  available_stock: number;
  planned_sales: number;
  actual_sales: number;
  closing_stock: number;
  is_stockout: boolean;
  has_override: boolean;
  arrival_details: ArrivalDetail[];
}

export interface CalculationSummary {
  total_days: number;
  total_planned_sales: number;
  total_actual_sales: number;
  stockout_days: number;
  stockout_dates: string[];
  ending_inventory: number;
}

export interface CalculationResponse {
  sales_plan_id: number;
  calculation_date: string;
  summary: CalculationSummary;
  daily_data: DailyCalculationResult[];
}

export interface ShipmentTurnoverResult {
  unit_id: number;
  unit_label: string;
  region: string;
  ship_date: string;
  arrival_date: string;
  quantity: number;
  sold_quantity: number;
  avg_turnover_days: number | null;
  fully_sold: boolean;
  sell_through_date: string | null;
}

export interface TurnoverResponse {
  sales_plan_id: number;
  turnovers: ShipmentTurnoverResult[];
}

export interface StockoutWarning {
  date: string;
  planned_sales: number;
  available_stock: number;
  shortfall: number;
}
