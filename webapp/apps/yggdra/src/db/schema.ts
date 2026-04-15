import {
  index,
  integer,
  jsonb,
  pgTable,
  primaryKey,
  text,
  timestamp,
  uuid,
  varchar,
} from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: uuid('id').primaryKey(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
});

export const nurtureState = pgTable(
  'nurture_state',
  {
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    characterId: varchar('character_id', { length: 64 }).notNull(),
    level: integer('level').notNull().default(1),
    intimacy: integer('intimacy').notNull().default(0),
    mood: integer('mood').notNull().default(60),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => [
    primaryKey({ columns: [table.userId, table.characterId] }),
    index('nurture_state_character_idx').on(table.characterId),
  ]
);

export const chatHistory = pgTable(
  'chat_history',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    characterId: varchar('character_id', { length: 64 }).notNull(),
    role: varchar('role', { length: 16 }).notNull(),
    actionType: varchar('action_type', { length: 32 }).notNull(),
    content: text('content').notNull(),
    metadata: jsonb('metadata').$type<Record<string, unknown> | null>(),
    createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  },
  (table) => [
    index('chat_history_lookup_idx').on(
      table.userId,
      table.characterId,
      table.createdAt
    ),
  ]
);
