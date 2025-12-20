"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import styled from "styled-components";
import { AccountCircle } from "@mui/icons-material";
import PlotlyChart from "@/components/PlotlyChart";
import { Stock, TimeSeriesData } from "@/types";

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
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
`;

const StockHeader = styled.div`
  margin-bottom: 3rem;
`;

const StockSymbol = styled.h1`
  font-family: ${({ theme }) => theme.fonts.logo};
  font-size: 3rem;
  color: ${({ theme }) => theme.colors.grayDark};
  margin-bottom: 0.5rem;
  font-weight: normal;
`;

const CompanyName = styled.p`
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 1.5rem;
  color: ${({ theme }) => theme.colors.grayMedium};
`;

const ChartSection = styled.div`
  margin-bottom: 4rem;
  border: 1px solid ${({ theme }) => theme.colors.grayLight};
  border-radius: 8px;
  padding: 2rem;
  background-color: ${({ theme }) => theme.colors.white};
`;

const ChartTitle = styled.h2`
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 1.5rem;
  color: ${({ theme }) => theme.colors.grayDark};
  margin-bottom: 1.5rem;
  font-weight: normal;
`;

const ChartContainer = styled.div`
  width: 100%;
  height: 500px;
`;

const FundamentalsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 3rem;
`;

const FundamentalCard = styled.div`
  padding: 1.5rem;
  border: 1px solid ${({ theme }) => theme.colors.grayLight};
  border-radius: 8px;
  background-color: ${({ theme }) => theme.colors.white};
`;

const FundamentalLabel = styled.div`
  font-family: ${({ theme }) => theme.fonts.detail};
  font-size: 0.9rem;
  color: ${({ theme }) => theme.colors.grayMedium};
  margin-bottom: 0.5rem;
`;

const FundamentalValue = styled.div`
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 1.5rem;
  color: ${({ theme }) => theme.colors.grayDark};
`;

const LoadingMessage = styled.p`
  text-align: center;
  font-family: ${({ theme }) => theme.fonts.body};
  color: ${({ theme }) => theme.colors.grayMedium};
  padding: 4rem;
`;

export default function StockDetailPage() {
  const params = useParams();
  const symbol = params.symbol as string;
  const [stock, setStock] = useState<Stock | null>(null);
  const [timeseries, setTimeseries] = useState<TimeSeriesData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stockResponse, timeseriesResponse] = await Promise.all([
          fetch(`/api/micro/stocks?symbol=${symbol}`),
          fetch(`/api/micro/timeseries?symbol=${symbol}`),
        ]);

        const stockData = await stockResponse.json();
        const timeseriesData = await timeseriesResponse.json();

        setStock(stockData);
        setTimeseries(timeseriesData.timeseries || []);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      } finally {
        setLoading(false);
      }
    };

    if (symbol) {
      fetchData();
    }
  }, [symbol]);

  const createInteractiveChart = () => {
    if (timeseries.length === 0) {
      return { data: [], layout: {} };
    }

    const dates = timeseries.map((d) => d.date);
    const prices = timeseries.map((d) => d.close);
    const rsi = timeseries.map((d) => d.rsi || 0);
    const volume = timeseries.map((d) => d.volume);

    const data = [
      {
        x: dates,
        y: prices,
        type: "scatter",
        mode: "lines",
        name: "Price",
        line: { color: "#64a7fa", width: 2 },
        xaxis: "x",
        yaxis: "y",
      },
      {
        x: dates,
        y: rsi,
        type: "scatter",
        mode: "lines",
        name: "RSI",
        line: { color: "#ff7878", width: 2 },
        xaxis: "x2",
        yaxis: "y2",
      },
      {
        x: dates,
        y: volume,
        type: "bar",
        name: "Volume",
        marker: { color: "#AAA" },
        xaxis: "x3",
        yaxis: "y3",
      },
    ];

    const layout = {
      height: 800,
      grid: {
        rows: 3,
        columns: 1,
        pattern: "independent",
      },
      xaxis: { domain: [0, 1], anchor: "y" },
      yaxis: { domain: [0.67, 1], title: "Price" },
      xaxis2: { domain: [0, 1], anchor: "y2" },
      yaxis2: { domain: [0.34, 0.66], title: "RSI" },
      xaxis3: { domain: [0, 1], anchor: "y3" },
      yaxis3: { domain: [0, 0.33], title: "Volume" },
      paper_bgcolor: "transparent",
      plot_bgcolor: "transparent",
      showlegend: true,
    };

    return { data, layout };
  };

  if (loading) {
    return (
      <Container>
        <LoadingMessage>Loading stock data...</LoadingMessage>
      </Container>
    );
  }

  if (!stock) {
    return (
      <Container>
        <LoadingMessage>Stock not found</LoadingMessage>
      </Container>
    );
  }

  const { data, layout } = createInteractiveChart();

  return (
    <Container>
      <Header>
        <Logo href="/">loopweave</Logo>
        <Link href="/account">
          <AccountCircle
            style={{ color: "#333", fontSize: "2rem", cursor: "pointer" }}
          />
        </Link>
      </Header>
      <Main>
        <StockHeader>
          <StockSymbol>{stock.symbol}</StockSymbol>
          <CompanyName>{stock.name}</CompanyName>
        </StockHeader>

        <ChartSection>
          <ChartTitle>Price, RSI & Volume</ChartTitle>
          <ChartContainer>
            <PlotlyChart data={data} layout={layout} staticPlot={false} />
          </ChartContainer>
        </ChartSection>

        <FundamentalsGrid>
          <FundamentalCard>
            <FundamentalLabel>Market Cap</FundamentalLabel>
            <FundamentalValue>
              {stock.market_cap
                ? `$${(stock.market_cap / 1e9).toFixed(2)}B`
                : "N/A"}
            </FundamentalValue>
          </FundamentalCard>
          <FundamentalCard>
            <FundamentalLabel>PE Ratio</FundamentalLabel>
            <FundamentalValue>
              {stock.pe_ratio?.toFixed(2) || "N/A"}
            </FundamentalValue>
          </FundamentalCard>
          <FundamentalCard>
            <FundamentalLabel>Forward PE</FundamentalLabel>
            <FundamentalValue>
              {stock.forward_pe?.toFixed(2) || "N/A"}
            </FundamentalValue>
          </FundamentalCard>
          <FundamentalCard>
            <FundamentalLabel>EBITDA</FundamentalLabel>
            <FundamentalValue>
              {stock.ebitda ? `$${(stock.ebitda / 1e9).toFixed(2)}B` : "N/A"}
            </FundamentalValue>
          </FundamentalCard>
          <FundamentalCard>
            <FundamentalLabel>Sector</FundamentalLabel>
            <FundamentalValue>{stock.sector || "N/A"}</FundamentalValue>
          </FundamentalCard>
          <FundamentalCard>
            <FundamentalLabel>Industry</FundamentalLabel>
            <FundamentalValue>{stock.industry || "N/A"}</FundamentalValue>
          </FundamentalCard>
        </FundamentalsGrid>
      </Main>
    </Container>
  );
}
