import { sql as vercelSql } from '@vercel/postgres';
import { drizzle } from 'drizzle-orm/vercel-postgres';
import * as schema from './schema';

const hasDatabaseUrl = Boolean(process.env.POSTGRES_URL);

export const db = hasDatabaseUrl ? drizzle(vercelSql, { schema }) : null;

export function isDatabaseAvailable() {
  return hasDatabaseUrl;
}
