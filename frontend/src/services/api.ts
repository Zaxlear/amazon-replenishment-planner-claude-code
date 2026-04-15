import axios from 'axios';
import type {
  ShipmentPlanCreate,
  ShipmentPlanUpdate,
  ShipmentPlanResponse,
  ShipmentPlanListItem,
  ShipmentBatchInput,
  ShipmentBatchResponse,
  WarehouseConfigInput,
} from '../types/shipment';
import type {
  SalesPlanCreate,
  SalesPlanUpdate,
  SalesPlanResponse,
  SalesPlanListItem,
  DailySalesInput,
  DailySalesBatchInput,
  OverrideCreate,
  OverrideResponse,
  CalculationResponse,
  TurnoverResponse,
  StockoutWarning,
} from '../types/sales';

const api = axios.create({
  baseURL: '/api/v1',
});

// --- Shipment Plans ---

export const shipmentApi = {
  list: () =>
    api.get<ShipmentPlanListItem[]>('/shipment-plans').then((r) => r.data),

  get: (id: number) =>
    api.get<ShipmentPlanResponse>(`/shipment-plans/${id}`).then((r) => r.data),

  create: (data: ShipmentPlanCreate) =>
    api.post<ShipmentPlanResponse>('/shipment-plans', data).then((r) => r.data),

  update: (id: number, data: ShipmentPlanUpdate) =>
    api.put<ShipmentPlanResponse>(`/shipment-plans/${id}`, data).then((r) => r.data),

  delete: (id: number) =>
    api.delete(`/shipment-plans/${id}`).then((r) => r.data),

  addBatch: (planId: number, data: ShipmentBatchInput) =>
    api.post<ShipmentPlanResponse>(`/shipment-plans/${planId}/batches`, data).then((r) => r.data),

  updateBatch: (planId: number, batchId: number, data: { ship_date?: string; batch_quantity?: number }) =>
    api.put<ShipmentPlanResponse>(`/shipment-plans/${planId}/batches/${batchId}`, data).then((r) => r.data),

  deleteBatch: (planId: number, batchId: number) =>
    api.delete(`/shipment-plans/${planId}/batches/${batchId}`).then((r) => r.data),

  updateWarehouseConfig: (planId: number, data: WarehouseConfigInput) =>
    api.put<ShipmentPlanResponse>(`/shipment-plans/${planId}/warehouse-config`, data).then((r) => r.data),
};

// --- Sales Plans ---

export const salesApi = {
  list: () =>
    api.get<SalesPlanListItem[]>('/sales-plans').then((r) => r.data),

  get: (id: number) =>
    api.get<SalesPlanResponse>(`/sales-plans/${id}`).then((r) => r.data),

  create: (data: SalesPlanCreate) =>
    api.post<SalesPlanResponse>('/sales-plans', data).then((r) => r.data),

  update: (id: number, data: SalesPlanUpdate) =>
    api.put<SalesPlanResponse>(`/sales-plans/${id}`, data).then((r) => r.data),

  delete: (id: number) =>
    api.delete(`/sales-plans/${id}`).then((r) => r.data),

  addEntries: (planId: number, entries: DailySalesInput[]) =>
    api.post(`/sales-plans/${planId}/entries`, entries).then((r) => r.data),

  updateEntry: (planId: number, date: string, planned_sales: number) =>
    api.put(`/sales-plans/${planId}/entries/${date}`, { planned_sales }).then((r) => r.data),

  batchSetSales: (planId: number, data: DailySalesBatchInput) =>
    api.post(`/sales-plans/${planId}/entries/batch`, data).then((r) => r.data),

  addOverride: (planId: number, data: OverrideCreate) =>
    api.post<OverrideResponse>(`/sales-plans/${planId}/overrides`, data).then((r) => r.data),

  deleteOverride: (planId: number, date: string) =>
    api.delete(`/sales-plans/${planId}/overrides/${date}`).then((r) => r.data),

  calculate: (planId: number) =>
    api.get<CalculationResponse>(`/sales-plans/${planId}/calculate`).then((r) => r.data),

  chartData: (planId: number) =>
    api.get(`/sales-plans/${planId}/chart-data`).then((r) => r.data),

  turnover: (planId: number) =>
    api.get<TurnoverResponse>(`/sales-plans/${planId}/turnover`).then((r) => r.data),

  stockoutWarnings: (planId: number) =>
    api.get<{ sales_plan_id: number; warnings: StockoutWarning[] }>(`/sales-plans/${planId}/stockout-warnings`).then((r) => r.data),
};

export default api;
