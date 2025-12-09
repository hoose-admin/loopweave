'use client';

import { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { ArrowDropDown } from '@mui/icons-material';
import { MetricType } from '@/types';

const DropdownContainer = styled.div`
  position: relative;
  width: 100%;
  max-width: 400px;
`;

const DropdownButton = styled.button`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 1rem;
  border: 1px solid ${({ theme }) => theme.colors.grayLight};
  border-radius: 4px;
  background-color: ${({ theme }) => theme.colors.white};
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.grayDark};
  cursor: pointer;
  transition: border-color 0.2s;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
  }
`;

const DropdownMenu = styled.div<{ isOpen: boolean }>`
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.5rem;
  background-color: ${({ theme }) => theme.colors.white};
  border: 1px solid ${({ theme }) => theme.colors.grayLight};
  border-radius: 4px;
  max-height: 500px;
  overflow-y: auto;
  z-index: 1000;
  display: ${({ isOpen }) => (isOpen ? 'block' : 'none')};
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const MetricGroup = styled.div`
  padding: 1rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.grayLight};

  &:last-child {
    border-bottom: none;
  }
`;

const GroupTitle = styled.h3`
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 0.9rem;
  color: ${({ theme }) => theme.colors.grayMedium};
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
`;

const MetricCard = styled.div<{ group: string }>`
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background-color: ${({ theme, group }) => {
    if (group === 'bullish') return 'rgba(100, 167, 250, 0.1)';
    if (group === 'bearish') return 'rgba(255, 120, 120, 0.1)';
    return theme.colors.white;
  }};
  border: 1px solid
    ${({ theme, group }) => {
      if (group === 'bullish') return 'rgba(100, 167, 250, 0.3)';
      if (group === 'bearish') return 'rgba(255, 120, 120, 0.3)';
      return theme.colors.grayLight;
    }};

  &:hover {
    background-color: ${({ theme, group }) => {
      if (group === 'bullish') return 'rgba(100, 167, 250, 0.2)';
      if (group === 'bearish') return 'rgba(255, 120, 120, 0.2)';
      return theme.colors.grayLight;
    }};
  }

  &:last-child {
    margin-bottom: 0;
  }
`;

const MetricName = styled.div`
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 1rem;
  color: ${({ theme }) => theme.colors.grayDark};
`;

const metrics = {
  general: [
    { id: 'macd_crossover', name: 'MACD Crossover' },
    { id: 'golden_cross', name: 'Golden Cross' },
    { id: 'death_cross', name: 'Death Cross' },
    { id: 'rsi_extremes', name: 'RSI Extremes' },
    { id: 'volume_spikes', name: 'Volume Spikes' },
    { id: 'breakout_above', name: 'Breakout Above Resistance' },
    { id: 'breakout_below', name: 'Breakout Below Resistance' },
  ],
  bullish: [
    { id: 'inverted_hammer', name: 'Inverted Hammer' },
    { id: 'bullish_engulfing', name: 'Bullish Engulfing' },
    { id: 'morning_star', name: 'Morning Star' },
    { id: 'three_white_soldiers', name: 'Three White Soldiers' },
  ],
  bearish: [
    { id: 'three_black_crows', name: 'Three Black Crows' },
    { id: 'bearish_engulfing', name: 'Bearish Engulfing' },
    { id: 'shooting_star', name: 'Shooting Star' },
    { id: 'evening_star', name: 'Evening Star' },
  ],
};

interface MetricDropdownProps {
  selectedMetric: MetricType | null;
  onSelectMetric: (metric: MetricType) => void;
}

export default function MetricDropdown({
  selectedMetric,
  onSelectMetric,
}: MetricDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedMetricName =
    metrics.general
      .concat(metrics.bullish, metrics.bearish)
      .find((m) => m.id === selectedMetric)?.name || 'Select Metric';

  return (
    <DropdownContainer ref={dropdownRef}>
      <DropdownButton onClick={() => setIsOpen(!isOpen)}>
        <span>{selectedMetricName}</span>
        <ArrowDropDown />
      </DropdownButton>
      <DropdownMenu isOpen={isOpen}>
        <MetricGroup>
          <GroupTitle>General</GroupTitle>
          {metrics.general.map((metric) => (
            <MetricCard
              key={metric.id}
              group="general"
              onClick={() => {
                onSelectMetric(metric.id as MetricType);
                setIsOpen(false);
              }}
            >
              <MetricName>{metric.name}</MetricName>
            </MetricCard>
          ))}
        </MetricGroup>
        <MetricGroup>
          <GroupTitle>Bullish Patterns</GroupTitle>
          {metrics.bullish.map((metric) => (
            <MetricCard
              key={metric.id}
              group="bullish"
              onClick={() => {
                onSelectMetric(metric.id as MetricType);
                setIsOpen(false);
              }}
            >
              <MetricName>{metric.name}</MetricName>
            </MetricCard>
          ))}
        </MetricGroup>
        <MetricGroup>
          <GroupTitle>Bearish Patterns</GroupTitle>
          {metrics.bearish.map((metric) => (
            <MetricCard
              key={metric.id}
              group="bearish"
              onClick={() => {
                onSelectMetric(metric.id as MetricType);
                setIsOpen(false);
              }}
            >
              <MetricName>{metric.name}</MetricName>
            </MetricCard>
          ))}
        </MetricGroup>
      </DropdownMenu>
    </DropdownContainer>
  );
}

