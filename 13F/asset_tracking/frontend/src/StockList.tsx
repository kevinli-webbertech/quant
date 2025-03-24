import React, { useEffect, useState } from 'react';

interface Stock {
  id: number;
  stock_symbol: string;
  shares: number;
  purchase_price: number;
  current_price: number | null;
  total_value: number;
  profit_loss: number;
}

const StockList: React.FC = () => {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/stocks')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then((data: Stock[]) => {
        setStocks(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading stock data...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h2>Stock Portfolio</h2>
      <table>
        <thead>
          <tr>
            <th>Stock</th>
            <th>Shares</th>
            <th>Purchase Price</th>
            <th>Current Price</th>
            <th>Total Value</th>
            <th>Profit/Loss</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock) => (
            <tr key={stock.id}>
              <td>{stock.stock_symbol}</td>
              <td>{stock.shares}</td>
              <td>${stock.purchase_price.toFixed(2)}</td>
              <td>{stock.current_price ? `$${stock.current_price.toFixed(2)}` : "N/A"}</td>
              <td>${stock.total_value.toFixed(2)}</td>
              <td style={{ color: stock.profit_loss >= 0 ? 'green' : 'red' }}>
                {stock.profit_loss >= 0 ? `+$${stock.profit_loss.toFixed(2)}` : `-$${Math.abs(stock.profit_loss).toFixed(2)}`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StockList;
