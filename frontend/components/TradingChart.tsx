'use client';

// A importação na v3 é direta
import { createChart, IChartApi, ISeriesApi, CandlestickData, UTCTimestamp } from 'lightweight-charts';
import React, { useEffect, useRef, useState } from 'react';

const API_BASE_URL = 'http://127.0.0.1:8000';

async function fetchKlines(): Promise<CandlestickData[]> {
    // ... (esta função continua igual à anterior) ...
    try {
        const response = await fetch(`${API_BASE_URL}/api/klines`);
        if (!response.ok) return [];
        const klines = await response.json();
        if (!Array.isArray(klines)) return [];
        return klines.map((k: any) => ({
            time: (k[0] / 1000) as UTCTimestamp,
            open: parseFloat(k[1]), high: parseFloat(k[2]),
            low: parseFloat(k[3]), close: parseFloat(k[4]),
        }));
    } catch (error) {
        console.error("Erro ao buscar klines:", error);
        return [];
    }
}

const TradingChart = () => {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        const chart: IChartApi = createChart(chartContainerRef.current, {
            width: chartContainerRef.current.clientWidth,
            height: 450,
            layout: { backgroundColor: '#131722', textColor: '#e2e8f0' },
            grid: { vertLines: { color: '#2a2f3b' }, horzLines: { color: '#2a2f3b' } },
            timeScale: { timeVisible: true, secondsVisible: false }
        });

        const candleSeries: ISeriesApi<"Candlestick"> = chart.addCandlestickSeries({
            upColor: 'rgba(74, 222, 128, 0.8)',
            downColor: 'rgba(248, 113, 113, 0.8)',
            borderVisible: false,
            wickUpColor: '#4ade80', wickDownColor: '#f87171',
        });

        fetchKlines().then(data => {
            if (data.length > 0) {
                candleSeries.setData(data);
                chart.timeScale().fitContent();
            }
            setIsLoading(false);
        });

        const handleResize = () => chart.resize(chartContainerRef.current!.clientWidth, 450);
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, []);

    return (
        <div className="relative w-full h-[450px]">
            {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-primary bg-opacity-50 z-10">
                    <p className="text-text-secondary">Carregando dados do gráfico...</p>
                </div>
            )}
            <div ref={chartContainerRef} className="w-full h-full" />
        </div>
    );
};

export default TradingChart;