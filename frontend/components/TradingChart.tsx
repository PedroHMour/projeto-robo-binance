'use client';

// Usamos a sintaxe de importação direta, compatível com a v3.8.0
import { createChart, IChartApi, ISeriesApi, CandlestickData, UTCTimestamp } from 'lightweight-charts';
import React, { useEffect, useRef, useState } from 'react';
import type { PriceUpdate } from '@/types';

const API_BASE_URL = 'http://127.0.0.1:8000';

interface TradingChartProps {
    lastPrice: PriceUpdate | null;
}

async function fetchKlines(): Promise<CandlestickData[]> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/klines`);
        if (!response.ok) {
            console.error("API de Klines retornou status não-OK:", response.status);
            return [];
        }
        const klines = await response.json();
        if (!Array.isArray(klines)) {
            console.error("Dados de klines inválidos:", klines);
            return [];
        }
        return klines.map((k: any) => ({
            time: (k[0] / 1000) as UTCTimestamp,
            open: parseFloat(k[1]),
            high: parseFloat(k[2]),
            low: parseFloat(k[3]),
            close: parseFloat(k[4]),
        }));
    } catch (error) {
        console.error("Erro ao buscar klines:", error);
        return [];
    }
}

export default function TradingChart({ lastPrice }: TradingChartProps) {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<{ chart?: IChartApi; candleSeries?: ISeriesApi<"Candlestick"> }>({});
    const [isLoading, setIsLoading] = useState(true);

    // Efeito para criar o gráfico (roda apenas uma vez)
    useEffect(() => {
        if (!chartContainerRef.current || chartRef.current.chart) return;

        const chart = createChart(chartContainerRef.current, {
            width: chartContainerRef.current.clientWidth,
            height: 450,
            layout: { backgroundColor: '#131722', textColor: '#e2e8f0' },
            grid: { vertLines: { color: '#2a2f3b' }, horzLines: { color: '#2a2f3b' } },
            timeScale: { timeVisible: true, secondsVisible: false }
        });

        const candleSeries = chart.addCandlestickSeries({
            upColor: 'rgba(74, 222, 128, 0.8)',
            downColor: 'rgba(248, 113, 113, 0.8)',
            borderVisible: false,
            wickUpColor: '#4ade80',
            wickDownColor: '#f87171',
        });
        
        chartRef.current = { chart, candleSeries };

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

    // Efeito para atualizar o gráfico com o preço em tempo real
    useEffect(() => {
        if (chartRef.current.candleSeries && lastPrice) {
            chartRef.current.candleSeries.update({
                time: lastPrice.time as UTCTimestamp,
                close: lastPrice.price,
            });
        }
    }, [lastPrice]);

    return (
        <div className="relative w-full h-[450px]">
            {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-primary bg-opacity-50 z-10">
                    <p className="text-text-secondary">Carregando Gráfico...</p>
                </div>
            )}
            <div ref={chartContainerRef} className="w-full h-full" />
        </div>
    );
}