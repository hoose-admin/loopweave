'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import styled from 'styled-components';
import { AccountCircle } from '@mui/icons-material';
import MetricDropdown from '@/components/MetricDropdown';
import PlotlyChart from '@/components/PlotlyChart';
import { MetricType, Stock } from '@/types';

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: ${({ theme }) => theme.colors.white};
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 4rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.grayLight};
`;

const Logo = styled(Link)`
  font-family: ${({ theme }) => theme.fonts.logo};
  font-size: 2rem;
  color: ${({ theme }) => theme.colors.grayDark};
  font-weight: normal;
  text-decoration: none;
`;

const Main = styled.main`
  flex: 1;
  padding: 4rem;
`;

const Controls = styled.div`
  display: flex;
  justify-content: center;
  margin-bottom: 3rem;
`;

const StockGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
`;

const StockCard = styled.div`
  border: 1px solid ${({ theme }) => theme.colors.grayLight};
  border-radius: 8px;
  padding: 1.5rem;
  background-color: ${({ theme }) => theme.colors.white};
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
`;

const StockSymbol = styled.h3`
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 1.5rem;
  color: ${({ theme }) => theme.colors.grayDark};
  margin-bottom: 1rem;
  font-weight: normal;
`;

const ChartContainer = styled.div`
  width: 100%;
  height: 200px;
`;

const LoadingMessage = styled.p`
  text-align: center;
  font-family: ${({ theme }) => theme.fonts.body};
  color: ${({ theme }) => theme.colors.grayMedium};
  padding: 4rem;
`;

export default function MicroPage() {
  const params = useParams();
  const router = useRouter();
  const userUuid = params.userUuid as string;
  const [selectedMetric, setSelectedMetric] = useState<MetricType | null>(null);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedMetric) {
      fetchStocksForMetric(selectedMetric);
    }
  }, [selectedMetric]);

  const fetchStocksForMetric = async (metric: MetricType) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/micro/metrics?metric=${metric}`);
      const data = await response.json();
      // Assuming the API returns stocks matching the metric
      setStocks(data.stocks || []);
    } catch (error) {
      console.error('Failed to fetch stocks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStockClick = (symbol: string) => {
    router.push(`/micro/${userUuid}/stock/${symbol}`);
  };

  const createStaticChart = (stock: Stock) => {
    // Placeholder data - will be replaced with actual data from API
    const data = [
      {
        x: ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        y: [100, 105, 103, 108, 110],
        type: 'scatter',
        mode: 'lines',
        line: { color: '#64a7fa', width: 2 },
      },
    ];

    const layout = {
      autosize: true,
      margin: { l: 0, r: 0, t: 0, b: 0 },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      xaxis: { showgrid: false, showticklabels: false },
      yaxis: { showgrid: false, showticklabels: false },
    };

    return { data, layout };
  };

  return (
    <Container>
      <Header>
        <Logo href="/">loopweave</Logo>
        <Link href="/account">
          <AccountCircle style={{ color: '#333', fontSize: '2rem', cursor: 'pointer' }} />
        </Link>
      </Header>
      <Main>
        <Controls>
          <MetricDropdown
            selectedMetric={selectedMetric}
            onSelectMetric={setSelectedMetric}
          />
        </Controls>
        {loading ? (
          <LoadingMessage>Loading stocks...</LoadingMessage>
        ) : stocks.length > 0 ? (
          <StockGrid>
            {stocks.slice(0, 10).map((stock) => {
              const { data, layout } = createStaticChart(stock);
              return (
                <StockCard
                  key={stock.symbol}
                  onClick={() => handleStockClick(stock.symbol)}
                >
                  <StockSymbol>{stock.symbol}</StockSymbol>
                  <ChartContainer>
                    <PlotlyChart data={data} layout={layout} staticPlot={true} />
                  </ChartContainer>
                </StockCard>
              );
            })}
          </StockGrid>
        ) : (
          <LoadingMessage>
            {selectedMetric
              ? 'No stocks found for this metric'
              : 'Select a metric to view stocks'}
          </LoadingMessage>
        )}
      </Main>
    </Container>
  );
}

