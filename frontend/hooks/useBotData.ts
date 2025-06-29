'use client';
import { useState, useEffect, useMemo } from 'react';
import type { Trade, PerformanceMetrics, PriceUpdate } from '@/types';
const API_BASE_URL = 'http://127.0.0.1:8000';

export function useBotData() {
    const [trades, setTrades] = useState<Trade[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [lastPrice, setLastPrice] = useState<PriceUpdate | null>(null);

    const fetchData = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/trades`);
            if (res.ok) setTrades((await res.json()).sort((a: Trade, b: Trade) => a.time - b.time));
        } catch (e) { console.error("Erro ao buscar trades:", e); }
    };

    useEffect(() => {
        fetchData();
        const ws = new WebSocket(`ws://127.0.0.1:8000/ws/updates`);
        ws.onopen = () => setIsConnected(true);
        ws.onclose = () => setIsConnected(false);
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            if (msg.type === 'new_trade') fetchData();
            else if (msg.type === 'price_update') setLastPrice(msg.data);
        };
        return () => ws.close();
    }, []);

    const performance = useMemo<PerformanceMetrics>(() => {
        const compras = trades.filter(t => t.isBuyer);
        const vendas = trades.filter(t => !t.isBuyer);
        const numCiclos = Math.min(compras.length, vendas.length);
        if (numCiclos === 0) return { total_pnl: 0, ciclos: 0, gains: 0, losses: 0, win_rate: 0 };
        let totalPnl = 0, gains = 0;
        for (let i = 0; i < numCiclos; i++) {
            const pnl = (parseFloat(vendas[i].price) * parseFloat(vendas[i].qty)) - (parseFloat(compras[i].price) * parseFloat(compras[i].qty));
            if (pnl > 0) gains++;
            totalPnl += pnl;
        }
        return { total_pnl: totalPnl, ciclos: numCiclos, gains, losses: numCiclos - gains, win_rate: (gains / numCiclos) * 100 };
    }, [trades]);

    return { isConnected, trades, performance, lastPrice };
}