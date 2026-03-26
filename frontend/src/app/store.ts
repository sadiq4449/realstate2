import { configureStore } from "@reduxjs/toolkit";
import authReducer from "../slices/authSlice";
import propertiesReducer from "../slices/propertiesSlice";
import chatReducer from "../slices/chatSlice";

/** Redux store with feature slices for auth, listings cache, and chat UI. */
export const store = configureStore({
  reducer: {
    auth: authReducer,
    properties: propertiesReducer,
    chat: chatReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
