import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Dashboard Robô de Trade",
  description: "Dashboard de performance para robô de trade da Binance",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      {/* Adicionamos as classes do Tailwind aqui */}
      <body className={`${inter.className} bg-background text-text-main antialiased`}>
        {children}
      </body>
    </html>
  );
}