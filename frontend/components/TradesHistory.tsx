'use client';
import type { Trade } from '@/types'; // Importa do nosso novo arquivo!

export default function TradesHistory({ trades }: { trades: Trade[] }) {
    if (trades.length === 0) {
        return (
            <div className="bg-primary p-6 rounded-xl shadow-lg h-full flex items-center justify-center text-center">
                <div>
                    <p className="text-2xl mb-2">📊</p>
                    <p className="text-text-secondary">Nenhum trade executado ainda.</p>
                    <p className="text-xs text-gray-600 mt-2">Deixe o robô rodando para gerar dados.</p>
                </div>
            </div>
        );
    }
    
    return (
        <div className="bg-primary p-4 rounded-xl shadow-lg h-full">
            <h2 className="text-xl font-semibold mb-4 text-white">Histórico de Trades</h2>
            <div className="overflow-y-auto max-h-[450px]">
                <table className="w-full text-sm text-left text-text-secondary">
                    <thead className="text-xs text-gray-400 uppercase bg-secondary sticky top-0">
                        <tr>
                            <th scope="col" className="px-4 py-3">Data/Hora</th>
                            <th scope="col" className="px-4 py-3">Lado</th>
                            <th scope="col" className="px-4 py-3">Preço</th>
                            <th scope="col" className="px-4 py-3">Quantidade</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-secondary">
                        {[...trades].reverse().map((trade) => (
                            <tr key={trade.id} className="hover:bg-secondary">
                                <td className="px-4 py-3">{new Date(trade.time).toLocaleString('pt-BR')}</td>
                                <td className={`px-4 py-3 font-bold ${trade.isBuyer ? 'text-accent-green' : 'text-accent-red'}`}>
                                    {trade.isBuyer ? 'COMPRA' : 'VENDA'}
                                </td>
                                <td className="px-4 py-3">${parseFloat(trade.price).toFixed(2)}</td>
                                <td className="px-4 py-3">{parseFloat(trade.qty).toFixed(6)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}