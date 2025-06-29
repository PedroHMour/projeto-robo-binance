'use client';

interface HeaderProps {
    isConnected: boolean;
}

export default function Header({ isConnected }: HeaderProps) {
    return (
        <header className="flex justify-between items-center mb-8 pb-4 border-b border-primary">
            <h1 className="text-3xl font-bold text-white">
                Painel de Performance <span className="text-accent">Robô Trader</span>
            </h1>
            <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full transition-colors duration-300 ${isConnected ? 'bg-accent-green animate-pulse' : 'bg-accent-red'}`}></div>
                <span className="text-text-secondary font-medium">{isConnected ? 'Conectado em Tempo Real' : 'Desconectado'}</span>
            </div>
        </header>
    );
}