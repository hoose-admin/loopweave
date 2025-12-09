'use client';

import { useState } from 'react';
import Link from 'next/link';
import styled from 'styled-components';
import { AccountCircle } from '@mui/icons-material';

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
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem;
`;

const SubscribeCard = styled.div`
  width: 100%;
  max-width: 500px;
  padding: 3rem;
  border: 1px solid ${({ theme }) => theme.colors.grayLight};
  border-radius: 8px;
  background-color: ${({ theme }) => theme.colors.white};
  text-align: center;
`;

const Title = styled.h1`
  font-family: ${({ theme }) => theme.fonts.logo};
  font-size: 2.5rem;
  color: ${({ theme }) => theme.colors.grayDark};
  margin-bottom: 1rem;
  font-weight: normal;
`;

const Price = styled.div`
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 3rem;
  color: ${({ theme }) => theme.colors.primary};
  margin: 2rem 0;
`;

const Description = styled.p`
  font-family: ${({ theme }) => theme.fonts.detail};
  font-size: 1rem;
  color: ${({ theme }) => theme.colors.grayMedium};
  margin-bottom: 2rem;
  line-height: 1.6;
`;

const Button = styled.button`
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 4px;
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 1.2rem;
  color: ${({ theme }) => theme.colors.white};
  background-color: ${({ theme }) => theme.colors.primary};
  cursor: pointer;
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

export default function SubscribePage() {
  const [loading, setLoading] = useState(false);

  const handleSubscribe = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/stripe/create-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      const data = await response.json();
      if (data.sessionId) {
        // Redirect to Stripe checkout
        // This will be implemented with Stripe
        console.log('Redirecting to Stripe checkout...');
      }
    } catch (error) {
      console.error('Failed to create checkout session:', error);
    } finally {
      setLoading(false);
    }
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
        <SubscribeCard>
          <Title>Subscribe</Title>
          <Price>$1/month</Price>
          <Description>
            Unlock custom metrics and advanced features. Create your own trading
            indicators and get access to exclusive tools.
          </Description>
          <Button onClick={handleSubscribe} disabled={loading}>
            {loading ? 'Processing...' : 'Subscribe Now'}
          </Button>
        </SubscribeCard>
      </Main>
    </Container>
  );
}

