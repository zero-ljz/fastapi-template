import { useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState } from 'react'

import { AuthContext } from './auth-context.ts'
import {
  getAccessToken,
  setAccessToken,
  subscribeToAccessToken,
} from './token-store.ts'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient()
  const [token, setToken] = useState(getAccessToken)

  useEffect(
    () =>
      subscribeToAccessToken((nextToken) => {
        setToken(nextToken)
        if (!nextToken) {
          queryClient.clear()
        }
      }),
    [queryClient],
  )

  const signIn = useCallback((nextToken: string) => {
    setAccessToken(nextToken)
  }, [])
  const signOut = useCallback(() => {
    setAccessToken(null)
  }, [])

  const value = useMemo(
    () => ({
      accessToken: token,
      isAuthenticated: Boolean(token),
      signIn,
      signOut,
    }),
    [signIn, signOut, token],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
