// Main.js

import React, { useState, useRef, useEffect } from 'react';
import ChatButton from './ChatButton'
import ChatWindow from './ChatWindow'

const Main = () => {
  const [isChatWindowVisible, setChatWindowVisible] = useState(false);

  const toggleChatWindow = () => {
    setChatWindowVisible(!isChatWindowVisible);
  };
  const handleCloseButtonClick = () => {
    setChatWindowVisible(false);
  };

  return (
    <div>
      <ChatButton onClick={toggleChatWindow} />
      <ChatWindow isVisible={isChatWindowVisible} onCloseButtonClick={handleCloseButtonClick} />
    </div>
  );
};

export default Main;
