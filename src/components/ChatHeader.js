import React from 'react';

const ChatHeader = ({onCloseButtonClick}) => {

  return (
    <div id="chat-window-header">
      <h3 id="chat-window-title">Asistente Virtual</h3>
      <button id="close-button" onClick={onCloseButtonClick} >&times;</button>
    </div>
  );
};

export default ChatHeader;
