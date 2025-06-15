import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { User, Tokens } from './types';

interface AuthState {
  user: User | null;
  tokens: Tokens | null;
  isLoading: boolean;
  error: string | null;
}

const stored = localStorage.getItem('auth');
const initialState: AuthState = stored
  ? JSON.parse(stored)
  : { user: null, tokens: null, isLoading: false, error: null };

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart(state) {
      state.isLoading = true;
      state.error = null;
    },
    loginSuccess(state, action: PayloadAction<{ user: User; tokens: Tokens }>) {
      state.user = action.payload.user;
      state.tokens = action.payload.tokens;
      state.isLoading = false;
      localStorage.setItem(
        'auth',
        JSON.stringify({ user: state.user, tokens: state.tokens })
      );
    },
    loginFailure(state, action: PayloadAction<string>) {
      state.error = action.payload;
      state.isLoading = false;
    },
    logout(state) {
      state.user = null;
      state.tokens = null;
      localStorage.removeItem('auth');
    },
  },
});

export const { loginStart, loginSuccess, loginFailure, logout } = authSlice.actions;

export const authReducer = authSlice.reducer;
