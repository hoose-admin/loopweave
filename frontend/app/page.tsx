"use client";

import Link from "next/link";
import styled from "styled-components";
import { AccountCircle } from "@mui/icons-material";

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

const Logo = styled.h1`
  font-family: ${({ theme }) => theme.fonts.logo};
  font-size: 2rem;
  color: ${({ theme }) => theme.colors.grayDark};
  font-weight: normal;
`;

const AccountIcon = styled(AccountCircle)`
  color: ${({ theme }) => theme.colors.grayDark};
  cursor: pointer;
  font-size: 2rem !important;
  transition: color 0.2s;

  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const Main = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  text-align: center;
`;

const Title = styled.h2`
  font-family: ${({ theme }) => theme.fonts.logo};
  font-size: 3rem;
  color: ${({ theme }) => theme.colors.grayDark};
  margin-bottom: 2rem;
  font-weight: normal;
`;

const Subtitle = styled.p`
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 1.5rem;
  color: ${({ theme }) => theme.colors.grayMedium};
  margin-bottom: 3rem;
`;

const NavLinks = styled.div`
  display: flex;
  gap: 2rem;
`;

const NavLink = styled(Link)`
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 1.2rem;
  color: ${({ theme }) => theme.colors.primary};
  padding: 0.75rem 2rem;
  border: 1px solid ${({ theme }) => theme.colors.primary};
  border-radius: 4px;
  transition: all 0.2s;

  &:hover {
    background-color: ${({ theme }) => theme.colors.primary};
    color: ${({ theme }) => theme.colors.white};
  }
`;

export default function Home() {
  return (
    <Container>
      <Header>
        <Logo>loopweave</Logo>
        <Link href="/login">
          <AccountIcon />
        </Link>
      </Header>
      <Main>
        <Title>Simplify Stock Trading Metrics</Title>
        <Subtitle>Visualize and analyze stock data with clarity</Subtitle>
        <NavLinks>
          <NavLink href="/micro/default">Explore Micro</NavLink>
          <NavLink href="/login">Get Started</NavLink>
        </NavLinks>
      </Main>
    </Container>
  );
}
