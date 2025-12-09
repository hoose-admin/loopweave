import { NextRequest, NextResponse } from 'next/server';
import { logout } from '@/lib/firebase-auth';

export async function POST(request: NextRequest) {
  try {
    const { error } = await logout();

    if (error) {
      return NextResponse.json({ error }, { status: 500 });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    );
  }
}

