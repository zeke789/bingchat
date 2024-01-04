import React from 'react';

// ChatButton.js


const ChatButton = ({ onClick }) => {
  return (
    <div id="chat-button" onClick={onClick}>
      <i className="fas fa-comment-dots" id="chat-icon"></i>
    </div>
  );
};

export default ChatButton;
