'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import styled from 'styled-components';
import { AccountCircle } from '@mui/icons-material';
import { User } from '@/types';

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

const AccountCard = styled.div`
  width: 100%;
  max-width: 600px;
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
  font-weight: normal;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const Label = styled.label`
  font-family: ${({ theme }) => theme.fonts.detail};
  font-size: 0.9rem;
  color: ${({ theme }) => theme.colors.grayMedium};
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
  margin-top: 1rem;

  &:hover {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const SuccessMessage = styled.p`
  color: ${({ theme }) => theme.colors.primary};
  font-family: ${({ theme }) => theme.fonts.detail};
  font-size: 0.9rem;
  text-align: center;
`;

export default function AccountPage() {
  const [profile, setProfile] = useState<Partial<User>>({
    displayName: '',
    email: '',
    username: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch('/api/user/profile');
        const data = await response.json();
        if (data.profile) {
          setProfile(data.profile);
        }
      } catch (err) {
        console.error('Failed to fetch profile:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccess('');

    try {
      const response = await fetch('/api/user/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile),
      });

      if (response.ok) {
        setSuccess('Profile updated successfully');
      }
    } catch (err) {
      console.error('Failed to update profile:', err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <Container>Loading...</Container>;
  }

  return (
    <Container>
      <Header>
        <Logo href="/">loopweave</Logo>
        <Link href="/account">
          <AccountCircle style={{ color: '#333', fontSize: '2rem', cursor: 'pointer' }} />
        </Link>
      </Header>
      <Main>
        <AccountCard>
          <Title>Account Settings</Title>
          <Form onSubmit={handleSubmit}>
            <div>
              <Label>Display Name</Label>
              <Input
                type="text"
                value={profile.displayName || ''}
                onChange={(e) => setProfile({ ...profile, displayName: e.target.value })}
              />
            </div>
            <div>
              <Label>Email</Label>
              <Input
                type="email"
                value={profile.email || ''}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
              />
            </div>
            <div>
              <Label>Username</Label>
              <Input
                type="text"
                value={profile.username || ''}
                onChange={(e) => setProfile({ ...profile, username: e.target.value })}
              />
            </div>
            {success && <SuccessMessage>{success}</SuccessMessage>}
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </Form>
        </AccountCard>
      </Main>
    </Container>
  );
}

