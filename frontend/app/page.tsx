'use client';
import Header from "@/components/Header";
import MetricsBar from "@/components/MetricsBar";
import TradesHistory from "@/components/TradesHistory";
import dynamic from 'next/dynamic';
import { useBotData } from '@/hooks/useBotData';

const TradingChart = dynamic(() => import('@/components/TradingChart'), {
    ssr: false,
    loading: () => <div className="h-[450px] flex items-center justify-center"><p className="text-text-secondary">Carregando Gráfico...</p></div>
});

export default function DashboardPage() {
    const { isConnected, trades, performance, lastPrice } = useBotData();

    return (
        <div className="bg-background min-h-screen">
            <main className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
                <Header isConnected={isConnected} />
                {performance && <MetricsBar performance={performance} />}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
                    <div className="lg:col-span-2 bg-primary p-4 rounded-xl shadow-lg">
                        <h2 className="text-xl font-semibold mb-4 text-white">Gráfico de Preço (BTC/USDT - 5m)</h2>
                        <TradingChart lastPrice={lastPrice} />
                    </div>
                    <TradesHistory trades={trades} />
                </div>
            </main>
        </div>
    );
}