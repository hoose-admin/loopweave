import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/firebase-auth';

export async function GET(request: NextRequest) {
  try {
    const user = await getCurrentUser();

    if (user) {
      return NextResponse.json({
        authenticated: true,
        user: {
          uid: user.uid,
          email: user.email,
        },
      });
    }

    return NextResponse.json({ authenticated: false, user: null });
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    );
  }
}

