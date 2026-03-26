import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface ChatMessage {
  id: string;
  conversation_id: string;
  sender_id: string;
  recipient_id: string;
  body: string;
  attachment_url?: string | null;
  created_at: string;
}

interface ChatState {
  messages: ChatMessage[];
  activeConversationId: string | null;
}

const initialState: ChatState = {
  messages: [],
  activeConversationId: null,
};

/** Holds active thread messages for the inbox UI. */
const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    setActiveConversation(state, action: PayloadAction<string | null>) {
      state.activeConversationId = action.payload;
      state.messages = [];
    },
    setMessages(state, action: PayloadAction<ChatMessage[]>) {
      state.messages = action.payload;
    },
    appendMessage(state, action: PayloadAction<ChatMessage>) {
      state.messages.push(action.payload);
    },
  },
});

export const { setActiveConversation, setMessages, appendMessage } = chatSlice.actions;
export default chatSlice.reducer;
