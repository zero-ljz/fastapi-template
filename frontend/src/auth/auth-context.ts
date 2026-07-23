import { createContext } from 'react'

export type AuthContextValue = {
  isAuthenticated: boolean
  signIn: (accessToken: string) => void
  signOut: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
)
