import { NextRequest, NextResponse } from 'next/server';
import { getOrCreateAnonymousUser } from '@/lib/nurture-auth';
import { applyNurtureAction, getNurtureSnapshot } from '@/lib/nurture-server';
import {
  DEFAULT_NURTURE_STATE,
  type NurtureActionType,
  type NurtureChatMessage,
  type NurtureStats,
} from '@/lib/nurture';

function isValidActionType(value: unknown): value is NurtureActionType {
  return (
    value === 'message' ||
    value === 'snack' ||
    value === 'present' ||
    value === 'training' ||
    value === 'champagne'
  );
}

function isNurtureState(value: unknown): value is NurtureStats {
  if (!value || typeof value !== 'object') return false;

  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.level === 'number' &&
    typeof candidate.intimacy === 'number' &&
    typeof candidate.mood === 'number'
  );
}

function isChatMessage(value: unknown): value is NurtureChatMessage {
  if (!value || typeof value !== 'object') return false;

  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.id === 'string' &&
    (candidate.role === 'user' || candidate.role === 'character') &&
    typeof candidate.actionType === 'string' &&
    typeof candidate.content === 'string' &&
    typeof candidate.createdAt === 'string'
  );
}

export async function GET(request: NextRequest) {
  const characterId = request.nextUrl.searchParams.get('characterId');

  if (!characterId) {
    return NextResponse.json(
      { error: 'characterId is required' },
      { status: 400 }
    );
  }

  try {
    const { userId } = await getOrCreateAnonymousUser();
    const snapshot = await getNurtureSnapshot(userId, characterId);
    return NextResponse.json(snapshot);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Failed to load nurture data';

    return NextResponse.json(
      {
        error: message,
        state: DEFAULT_NURTURE_STATE,
        messages: [],
        databaseAvailable: false,
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as {
      characterId?: string;
      actionType?: NurtureActionType;
      message?: string;
      currentState?: NurtureStats;
      recentMessages?: NurtureChatMessage[];
    };

    if (!body.characterId) {
      return NextResponse.json(
        { error: 'characterId is required' },
        { status: 400 }
      );
    }

    if (typeof body.message === 'string' && body.message.length > 500) {
      return NextResponse.json(
        { error: 'Message too long' },
        { status: 400 }
      );
    }

    if (!isValidActionType(body.actionType)) {
      return NextResponse.json(
        { error: 'Invalid actionType' },
        { status: 400 }
      );
    }

    if (
      body.actionType === 'message' &&
      (!body.message || body.message.trim().length === 0)
    ) {
      return NextResponse.json(
        { error: 'message is required for message action' },
        { status: 400 }
      );
    }

    const { userId } = await getOrCreateAnonymousUser();
    const result = await applyNurtureAction({
      userId,
      characterId: body.characterId,
      actionType: body.actionType,
      message: body.message,
      fallbackState: isNurtureState(body.currentState)
        ? body.currentState
        : DEFAULT_NURTURE_STATE,
      fallbackMessages: Array.isArray(body.recentMessages)
        ? body.recentMessages.filter(isChatMessage).slice(-5)
        : [],
    });

    return NextResponse.json(result);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Failed to process nurture action';

    return NextResponse.json({ error: message }, { status: 500 });
  }
}
