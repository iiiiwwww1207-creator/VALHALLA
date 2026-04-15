import { cookies } from 'next/headers';
import { db } from '@/db';
import { users } from '@/db/schema';

const USER_COOKIE_NAME = 'yggdra_uid';
const COOKIE_MAX_AGE = 60 * 60 * 24 * 365;
const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export async function getOrCreateAnonymousUser() {
  const cookieStore = await cookies();
  const existing = cookieStore.get(USER_COOKIE_NAME)?.value;
  const userId =
    existing && UUID_PATTERN.test(existing) ? existing : crypto.randomUUID();

  if (!existing || existing !== userId) {
    cookieStore.set(USER_COOKIE_NAME, userId, {
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      path: '/',
      maxAge: COOKIE_MAX_AGE,
    });
  }

  if (db) {
    await db
      .insert(users)
      .values({
        id: userId,
        updatedAt: new Date(),
      })
      .onConflictDoNothing();
  }

  return { userId };
}
