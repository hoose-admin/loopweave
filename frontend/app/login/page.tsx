'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import styled from 'styled-components';
import { AccountCircle } from '@mui/icons-material';
import { login } from '@/lib/firebase-auth';

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

const LoginCard = styled.div`
  width: 100%;
  max-width: 400px;
  padding: 3rem;
  border: 1px solid ${({ theme }) => theme.colors.grayLight};
  border-radius: 8px;
  background-color: ${({ theme }) => theme.colors.white};
`;

const Title = styled.h1`
  font-family: ${({ theme }) => theme.fonts.logo};
  font-size: 2rem;
  color: ${({ theme }) => theme.colors.grayDark};
  margin-bottom: 2rem;
  text-align: center;
  font-weight: normal;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 1px solid ${({ theme }) => theme.colors.grayLight};
  border-radius: 4px;
  font-family: ${({ theme }) => theme.fonts.detail};
  font-size: 1rem;
  color: ${({ theme }) => theme.colors.grayDark};
  background-color: ${({ theme }) => theme.colors.white};

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary};
  }
`;

const Button = styled.button`
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-family: ${({ theme }) => theme.fonts.body};
  font-size: 1.1rem;
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

const ErrorMessage = styled.p`
  color: ${({ theme }) => theme.colors.secondary};
  font-family: ${({ theme }) => theme.fonts.detail};
  font-size: 0.9rem;
  text-align: center;
`;

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // For Firebase, we use email instead of username
      // In a real implementation, you might want to support both
      const email = username.includes('@') ? username : `${username}@loopweave.local`;
      
      const { user, error } = await login(email, password);

      if (error) {
        setError(error);
      } else if (user) {
        router.push('/account');
      } else {
        setError('Login failed');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Header>
        <Logo href="/">loopweave</Logo>
        <Link href="/">
          <AccountCircle style={{ color: '#333', fontSize: '2rem', cursor: 'pointer' }} />
        </Link>
      </Header>
      <Main>
        <LoginCard>
          <Title>Login</Title>
          <Form onSubmit={handleSubmit}>
            <Input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {error && <ErrorMessage>{error}</ErrorMessage>}
            <Button type="submit" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </Form>
        </LoginCard>
      </Main>
    </Container>
  );
}

