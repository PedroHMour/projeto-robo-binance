'use client';
import { useState, useEffect, useMemo } from 'react';
import type { Trade, PerformanceMetrics } from '@/types';

const API_BASE_URL = 'http://127.0.0.1:8000';

interface PriceUpdate {
    time: number;
    price: number;
}

export function useBotData() {
    const [trades, setTrades] = useState<Trade[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [lastPrice, setLastPrice] = useState<PriceUpdate | null>(null);

    const fetchData = async () => {
        try {
            const tradesRes = await fetch(`${API_BASE_URL}/api/trades`);
            if (tradesRes.ok) {
                const tradesData = await tradesRes.json();
                const sortedTrades = (tradesData as Trade[]).sort((a, b) => a.time - b.time);
                setTrades(sortedTrades);
            }
        } catch (error) {
            console.error("Erro ao buscar dados da API de trades:", error);
        }
    };

    useEffect(() => {
        fetchData();
        const ws = new WebSocket(`ws://127.0.0.1:8000/ws/updates`);
        ws.onopen = () => setIsConnected(true);
        ws.onclose = () => setIsConnected(false);
        ws.onerror = (error) => console.error("Erro no WebSocket:", error);
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            switch(message.type) {
                case 'new_trade':
                    fetchData();
                    break;
                case 'price_update':
                    setLastPrice(message.data);
                    break;
            }
        };
        return () => ws.close();
    }, []);

    const performance = useMemo<PerformanceMetrics>(() => {
        const compras = trades.filter(t => t.isBuyer);
        const vendas = trades.filter(t => !t.isBuyer);
        const numCiclos = Math.min(compras.length, vendas.length);

        if (numCiclos === 0) {
            return { total_pnl: 0, ciclos: 0, gains: 0, losses: 0, win_rate: 0 };
        }

        let totalPnl = 0;
        let gains = 0;
        for (let i = 0; i < numCiclos; i++) {
            const custoCompra = parseFloat(compras[i].price) * parseFloat(compras[i].qty);
            const receitaVenda = parseFloat(vendas[i].price) * parseFloat(vendas[i].qty);
            const pnlCiclo = receitaVenda - custoCompra;
            if (pnlCiclo > 0) gains++;
            totalPnl += pnlCiclo;
        }

        return {
            total_pnl: totalPnl,
            ciclos: numCiclos,
            gains: gains,
            losses: numCiclos - gains,
            win_rate: (gains / numCiclos) * 100,
        };
    }, [trades]);

    return { isConnected, trades, performance, lastPrice };
}