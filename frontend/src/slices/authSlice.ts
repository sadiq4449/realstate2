import { createSlice, PayloadAction } from "@reduxjs/toolkit";

/** Authenticated user shape returned by `/users/me`. */
export type UserRole = "owner" | "seeker" | "admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string;
}

interface AuthState {
  user: User | null;
  bootstrapped: boolean;
}

const initialState: AuthState = {
  user: null,
  bootstrapped: false,
};

/** Tracks session user for role-based routing and navbar. */
const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setUser(state, action: PayloadAction<User | null>) {
      state.user = action.payload;
      state.bootstrapped = true;
    },
    logout(state) {
      state.user = null;
      state.bootstrapped = true;
    },
  },
});

export const { setUser, logout } = authSlice.actions;
export default authSlice.reducer;
