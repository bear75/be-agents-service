/**
 * Type declaration for better-sqlite3 when @types are not resolved (e.g. hoisted workspace).
 * Ensures the server builds; for full types install @types/better-sqlite3 in the workspace.
 */
declare module 'better-sqlite3' {
  interface Statement {
    run(...params: unknown[]): { changes: number; lastInsertRowid: number };
    get(...params: unknown[]): unknown;
    all(...params: unknown[]): unknown[];
  }

  interface Database {
    prepare(sql: string): Statement;
    exec(sql: string): this;
    pragma(sql: string, options?: unknown): unknown;
    close(): this;
  }

  const Database: new (path: string) => Database;
  export default Database;
  export type { Database };
}
