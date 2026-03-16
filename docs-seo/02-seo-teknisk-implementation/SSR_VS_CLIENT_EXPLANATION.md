# Why `dashboard` Works But `sverigeshemtjanst` Had Issues

## The Key Difference: SSR vs Client-Only

### `dashboard` - Client-Only App (No SSR)

**Architecture:**

- ✅ Pure client-side React app
- ✅ No server-side rendering
- ✅ Uses `nginx` to serve static files
- ✅ ClerkProvider only runs in the browser

**How it works:**

```
User Request → nginx → Static HTML/JS → Browser → React Hydrates → ClerkProvider Initializes
```

**Entry Point:**

- `src/main.tsx` - Only runs in the browser
- Uses `ReactDOM.createRoot()` - client-side only
- ClerkProvider is safely wrapped because it only executes in the browser

```tsx
// dashboard/src/main.tsx
ReactDOM.createRoot(document.getElementById("root")!).render(
  <ClerkProvider publishableKey={env.VITE_CLERK_PUBLISHABLE_KEY}>
    <App />
  </ClerkProvider>,
);
```

**Why it works:**

- ClerkProvider never runs on the server
- No SSR means no server-side React rendering
- All Clerk hooks (`useUser()`, `useAuth()`, etc.) only execute in the browser where ClerkProvider is available

---

### `sverigeshemtjanst` - SSR App (Server-Side Rendering)

**Architecture:**

- ⚠️ Server-Side Rendering (SSR)
- ⚠️ Uses Node.js server (`server.ts`) to render React on the server
- ⚠️ Has TWO entry points: `entry-server.tsx` (server) + `entry-client.tsx` (browser)
- ⚠️ ClerkProvider was being called during SSR (the problem!)

**How it works:**

```
User Request → Node.js Server → renderToString() → HTML → Browser → React Hydrates → ClerkProvider Initializes
```

**Entry Points:**

1. `src/entry-server.tsx` - Runs on the server (SSR)
2. `src/entry-client.tsx` - Runs in the browser (hydration)

**The Problem (Before Fix):**

```tsx
// ❌ BEFORE: This was the issue
// entry-server.tsx (runs on server)
export async function render(url: string) {
  const html = renderToString(
    <ClerkProvider publishableKey={key}>
      {" "}
      // ❌ ClerkProvider uses hooks that don't work in SSR!
      <App />
    </ClerkProvider>,
  );
}
```

**Why it failed:**

- `ClerkProvider` uses React hooks internally (`useEffect`, `useState`, etc.)
- React hooks require a browser environment with DOM APIs
- During SSR, there's no browser, no DOM, no `window` object
- When `ClerkProvider` tried to use hooks during SSR, it failed with:
  ```
  TypeError: Cannot read properties of null (reading 'useContext')
  ```

---

## The Fix: React Best Practices for SSR + Clerk

### ✅ Solution: Separate Server and Client Rendering

**React Best Practice:** Components that use browser-only APIs (like Clerk) should only render on the client side.

**The Fix:**

1. **Server-Side (`entry-server.tsx`):**

   ```tsx
   // ✅ No ClerkProvider during SSR
   export async function render(url: string) {
     const html = renderToString(
       <HelmetProvider>
         <ClerkProviderSSR>
           {" "}
           {/* Pass-through component, no ClerkProvider */}
           <App />
         </ClerkProviderSSR>
       </HelmetProvider>,
     );
   }
   ```

2. **Client-Side (`entry-client.tsx`):**

   ```tsx
   // ✅ ClerkProvider only on client side
   hydrateRoot(
     root,
     <ClerkProvider publishableKey={clerkPubKey}>
       <App />
     </ClerkProvider>,
   );
   ```

3. **Safe Hook Usage:**
   ```tsx
   // ✅ Don't call useUser() during SSR
   const useNavItems = () => {
     // Return base items during SSR (no user-specific items)
     // User-specific items added client-side only
     return BASE_NAV_ITEMS;
   };
   ```

---

## React Best Practices for SSR + Third-Party Libraries

### Rule of Thumb:

1. **Browser-only libraries** (Clerk, analytics, etc.) → Client-side only
2. **SSR-safe libraries** (React Router, Apollo, etc.) → Can be used in SSR
3. **Conditional rendering** → Use `typeof window !== "undefined"` checks
4. **Hooks that require context** → Only call when provider is available

### Pattern to Follow:

```tsx
// ✅ Good: Check for SSR before using browser-only APIs
function MyComponent() {
  if (typeof window === "undefined") {
    // SSR: Return safe defaults
    return <div>Loading...</div>;
  }

  // Client-side: Use browser-only APIs
  const { user } = useUser(); // Safe because ClerkProvider is available
  return <div>Hello {user?.name}</div>;
}
```

---

## Summary

| Aspect            | `dashboard`          | `sverigeshemtjanst`                         |
| ----------------- | -------------------- | ------------------------------------------- |
| **Rendering**     | Client-only          | SSR + Client                                |
| **Server**        | nginx (static files) | Node.js (React SSR)                         |
| **Entry Points**  | 1 (`main.tsx`)       | 2 (`entry-server.tsx` + `entry-client.tsx`) |
| **ClerkProvider** | Only in browser ✅   | Was in SSR ❌ → Fixed ✅                    |
| **Why it works**  | Never runs on server | Fixed to only run on client                 |

**Key Takeaway:** SSR apps need to be careful about browser-only libraries. Always separate server and client rendering, and only use browser-only APIs (like Clerk) on the client side.
