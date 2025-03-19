import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  chatOpen: true,
  messages: [],
  newMessage: ''
};

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    toggleChat: (state) => {
      state.chatOpen = !state.chatOpen;
    },
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    setNewMessage: (state, action) => {
      state.newMessage = action.payload;
    }
  }
});

export const { toggleChat, addMessage, setNewMessage } = chatSlice.actions;

export default chatSlice.reducer;
