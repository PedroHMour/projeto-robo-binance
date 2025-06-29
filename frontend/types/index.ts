export interface Trade {
    id: number; price: string; qty: string; quoteQty: string;
    commission: string; commissionAsset: string; time: number;
    isBuyer: boolean; isMaker: boolean; isBestMatch: boolean;
    symbol?: string; orderId?: number;
}
export interface PerformanceMetrics {
    total_pnl: number; ciclos: number; gains: number;
    losses: number; win_rate: number;
}
export interface PriceUpdate { time: number; price: number; }