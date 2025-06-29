'use client';

// ... (interface e a função MetricCard não mudam) ...
interface PerformanceMetrics {
    total_pnl: number;
    win_rate: number;
    gains: number;
    losses: number;
    ciclos: number;
}

interface MetricCardProps {
    title: string;
    value: string;
    colorClass?: string;
}

function MetricCard({ title, value, colorClass = 'text-white' }: MetricCardProps) {
    return (
        <div className="bg-primary p-5 rounded-xl shadow-lg border border-transparent hover:border-accent transition-all duration-300">
            <h3 className="text-sm text-text-secondary mb-1">{title}</h3>
            <p className={`text-3xl font-bold ${colorClass}`}>{value}</p>
        </div>
    );
}

export default function MetricsBar({ performance }: { performance: PerformanceMetrics }) {
    const pnlColor = performance.total_pnl >= 0 ? 'text-accent-green' : 'text-accent-red';
    
    return (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-6 mb-8">
            <MetricCard 
                title="Lucro/Prejuízo Total" 
                value={`$${performance.total_pnl.toFixed(2)}`}
                colorClass={pnlColor}
            />
            <MetricCard 
                title="Taxa de Acerto" 
                value={`${performance.win_rate.toFixed(1)}%`}
                colorClass="text-accent"
            />
            <MetricCard 
                title="Trades com Lucro" 
                value={performance.gains.toString()}
                colorClass="text-accent-green"
            />
            <MetricCard 
                title="Trades com Prejuízo" 
                value={performance.losses.toString()}
                colorClass="text-accent-red"
            />
            <MetricCard
                title="Ciclos Completos"
                value={performance.ciclos.toString()}
            />
        </div>
    );
}