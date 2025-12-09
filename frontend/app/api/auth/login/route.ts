import { NextRequest, NextResponse } from 'next/server';
import { login } from '@/lib/firebase-auth';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email and password are required' },
        { status: 400 }
      );
    }

    const { user, error } = await login(email, password);

    if (error) {
      return NextResponse.json({ error }, { status: 401 });
    }

    return NextResponse.json({
      success: true,
      user: {
        uid: user?.uid,
        email: user?.email,
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    );
  }
}

