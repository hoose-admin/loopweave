import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/firebase-auth';
import { getUserFavorites, addFavorite, removeFavorite } from '@/lib/firestore';

export async function GET(request: NextRequest) {
  try {
    const user = await getCurrentUser();

    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const favorites = await getUserFavorites(user.uid);
    return NextResponse.json({ favorites });
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const user = await getCurrentUser();

    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const body = await request.json();
    const { symbol, action } = body;

    if (!symbol || !action) {
      return NextResponse.json(
        { error: 'Symbol and action are required' },
        { status: 400 }
      );
    }

    let success = false;
    if (action === 'add') {
      success = await addFavorite(user.uid, symbol);
    } else if (action === 'remove') {
      success = await removeFavorite(user.uid, symbol);
    } else {
      return NextResponse.json(
        { error: 'Invalid action' },
        { status: 400 }
      );
    }

    if (success) {
      return NextResponse.json({ success: true });
    }

    return NextResponse.json(
      { error: 'Failed to update favorites' },
      { status: 500 }
    );
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    );
  }
}

