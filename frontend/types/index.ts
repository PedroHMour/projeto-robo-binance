// Define a estrutura de um único trade, como recebido da API da Binance
export interface Trade {
    id: number;
    price: string;
    qty: string;
    quoteQty: string;
    commission: string;
    commissionAsset: string;
    time: number;
    isBuyer: boolean;
    isMaker: boolean;
    isBestMatch: boolean;
    symbol: string;
    orderId: number;
}

// Define a estrutura das métricas de performance que calculamos
export interface PerformanceMetrics {
    total_pnl: number;
    ciclos: number;
    gains: number;
    losses: number;
    win_rate: number;
}