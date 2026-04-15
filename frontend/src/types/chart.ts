export interface ChartDataPoint {
  date: string;
  openingStock: number;
  plannedSales: number;
  actualSales: number;
  isStockout: boolean;
  arrivals: number;
  hasOverride: boolean;
}
