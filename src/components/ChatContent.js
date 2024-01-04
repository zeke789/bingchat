// ChatContent.js
import React, { useRef } from 'react';

const ChatContent = ({ content, handleResendClick, onChangeSelectMode, isStreamChecked }) => {
  
  const radioRef = useRef(null);
  
  return (
    <div id="chat-window-content">

      <label class="toggle-label" for="toggleMode">
        
        <b> Stream <small>({isStreamChecked ? 'ON' : 'OFF'})</small> </b>
        <input type="radio" id="toggleMode" class="toggle-input" name="mode"
            ref={radioRef} 
            onClick={onChangeSelectMode} 
            checked={isStreamChecked}
          />
        <div class="toggle-slider"></div>
      </label>

      {content.map((message, index) => {
        // console.log(`Debugging CONTENT ${index}:`, message);
        //console.log(`Debugging Content ${index}:`, message.error);
        return (
          <div key={index} className={`message ${message.sender} ${message.error !== null && message.error !== undefined ? 'msjError' : ''}`} >
            
            <p id="chatContent_msj">
              { message.msj ? message.msj.trim() : ''}
            </p>

            {message.error && 
                <div>
                    <hr className="hr1"/>
                    {message.error}
                    <a href="#" onClick={() => {handleResendClick(message.msj)}} >
                        <img src="/resend.png" height="45" alt="Error icon"/>
                    </a>
                </div>
            }
          </div>
        );
      })}
    </div>
  );
};

export default ChatContent;
