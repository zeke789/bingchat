// ChatInput.js
import React, { useState } from 'react';

//como parametro  recibe onSendMessage (funcion a ejecutar cuando se clickea enviar)
const ChatInput = ({ onSendMessage }) => {
  const [inputText, setInputText] = useState(''); // Nuevo estado para gestionar el texto de entrada

  const handleInputChange = (event) => {
    setInputText(event.target.value);
  };

  const handleSendButtonClick = () => {
    if (inputText.trim() !== '') {
      onSendMessage(inputText); // Llama a la función con el nuevo mensaje
      setInputText(''); // Limpia el texto de entrada después de enviar el mensaje
    }
  };

  return (
    <div id="chat-input-container">
      <textarea
        id="chat-input"
        placeholder="Escribí acá..."
        rows="1"
        autoComplete="off"
        value={inputText}
        onChange={handleInputChange}
      ></textarea>
      <button id="send-button" onClick={handleSendButtonClick}>
        Enviar
      </button>
    </div>
  );
};

export default ChatInput;
