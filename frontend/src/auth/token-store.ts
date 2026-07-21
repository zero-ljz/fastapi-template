type TokenListener = (accessToken: string | null) => void

let accessToken: string | null = null
const listeners = new Set<TokenListener>()

export function getAccessToken(): string | null {
  return accessToken
}

export function setAccessToken(nextToken: string | null): void {
  accessToken = nextToken
  listeners.forEach((listener) => listener(accessToken))
}

export function subscribeToAccessToken(listener: TokenListener): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}
