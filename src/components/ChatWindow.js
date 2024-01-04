// ChatWindow.js
import React, { useState } from 'react';

import ChatHeader from './ChatHeader';
import ChatContent from './ChatContent';
import ChatInput from './ChatInput';

const ChatWindow = ({ isVisible, onCloseButtonClick  }) => {

  const [chatContent, setChatContent] = useState([]);  // Nuevo estado para gestionar el contenido del chat (historial de mensajes)
  const [chatID, setChatID] = useState(null);  // id del chat
  
  const [isStreamChecked, setStreamChecked] = useState(false);
 
  const appendMessage = (userMsg) => {
    const userMessage = {
      msj: userMsg,
      sender: 'user'
    }; 
    setChatContent((prevContent) => [...prevContent, userMessage]);
    getAndAppendAIResponse(userMsg);
  };


  const getAndAppendAIResponse = (userMsg, resend=false) => {
    
    //SEND USER MESSAGE TO AI API
    sendMessage(userMsg).then((data) => {
      
      if(data !== "error"){
        if( data !== 'donestream' && data !== 'chatidsaved' && data !== 'errorconnectsaved' ){ 
          // CREAR MSJ CON LA RESPUESTA DE AI
          const appendMsgAI = {
            msj: data,
            sender: 'ai',
            additionalInfo: "Información adicional"
          };
          //ACTUALIZAR ESTADO CON MSJ DE LA IA
          setChatContent((prevContent) => {
            const newContent = [...prevContent, appendMsgAI];            
            if (resend) {
              // SI ES UN MENSAJE REENVIADO SE LE BORRA EL ERROR AL MSJ DEL USUARIO
              const elementoAnterior = newContent[newContent.length - 2];
              if (elementoAnterior && elementoAnterior.error) {
                const prevElementUpdated = { ...elementoAnterior };
                delete prevElementUpdated.error;
                newContent[newContent.length - 2] = prevElementUpdated;
              }
            }
            return newContent;
          });
        }
      }else{ 
        //SETEAR ESTADO ERROR PARA EL ULTIMO MENSAJE DE USER
        let lastMessageIndex = chatContent.length - 1;
        if (lastMessageIndex >= 0) {
          // si hay mensajes agregar propiedad error al ultimo mensaje agregado a ChatContent
          setChatContent((prevContent) => {
            const ultimoElemento = prevContent[prevContent.length - 1];
            const nuevoContent = [...prevContent];
            nuevoContent[nuevoContent.length - 1] = {...ultimoElemento, error: "No se pudo enviar el mensaje" };
            return nuevoContent;
          });
        }else{
          // si no hay mensajes anteriores, crea un nuevo mensaje y establece el estado con error
          const newMessage = {
            msj: userMsg,
            sender: 'user',
            error: "No se pudo enviar el mensaje"
          };
          setChatContent([newMessage]);
        }
      }

    }).catch((error) => {
      console.error('Error al enviar el mensaje:', error);
    });
  };
  

  const resendMessage = async(msg) => {
    getAndAppendAIResponse(msg,true);
  };  


  const sendMessage = async (msg) => {
    let mode = isStreamChecked ? "s" : "n";
    
    let sendData = { msg: msg, mode:mode };
    if(chatID !== null){
      sendData["hid"] = chatID;
    }
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(sendData)
    };

    if(isStreamChecked){
            ////// ****** ----- STREAM RESPONSE ----- ****** \\\\\\
      try {
        const response = await fetch('/backend/1.php', requestOptions);
        const reader = response.body.getReader();
        let accumulatedMessage = '';  
        while (true) {
          // LEER STREAM RESPONSE Y ACUMULAR RESPUESTA EN accumulatedMessage
          const { value, done } = await reader.read();
          if (done) { break; }
          const chunk = new TextDecoder().decode(value);
          
          // HANDLE ERROR, ( IF ISN'T JSON THEN IS NOT ERROR SO CONTINUE )
          let jsonData;
          try {
            jsonData = JSON.parse(chunk);
            if( jsonData.chatid ){
              setChatID(jsonData.chatid);
              return "chatidsaved"
            }else{
              if( jsonData.savedError ){
                return "errorconnectsaved"
              }
              return "error";/* SAVE_ERROR */
            }            
          }catch (jsonError){}
          

          accumulatedMessage += chunk;  
          await new Promise(resolve => setTimeout(resolve, 100));


          // SI ES REENVIO DE MENSAJE, ELIMINAR ERROR DEL MENSAJE ENVIADO X USUARIO
          setChatContent((prevContent) => {
            const newContent = prevContent;
            const elementoAnterior = newContent[newContent.length - 2];
            if (elementoAnterior && elementoAnterior.error) {
              const prevElementUpdated = { ...elementoAnterior };
              delete prevElementUpdated.error;
              newContent[newContent.length - 2] = prevElementUpdated;
            } 
            return newContent;
          });

          // ACTUALIZAR ESTADO DE chatContent A MEDIDA QUE accumulatedMessage SE ACTUALIZA
          setChatContent(prevContent => {
            const lastMessage = prevContent[prevContent.length - 1];
            if (lastMessage && lastMessage.sender === 'ai') {
              // Ya hay un mensaje de la IA en el ultimo estado, actualizarlo
              // remover mensaje y agregarle mensaje actualizado
              return [
                ...prevContent.slice(0, -1),
                {
                  ...lastMessage,
                  msj: accumulatedMessage,
                },
              ];
            } else {
              // No hay mensajes de la IA se crea un nuevo objeto (mensaje)
              return [
                ...prevContent,
                {
                  msj: accumulatedMessage,
                  sender: 'ai',
                  additionalInfo: 'Información adicional',
                },
              ];
            }
          });
        }  
        reader.releaseLock(); 

        //retornar donestream para que no siga agregando mensajes
        return "donestream";
      } catch (error) {
        console.error('Error al realizar la solicitud:', error);
        throw error;
      }
     
    }else{

            ////// ****** ----- NORMAL RESPONSE ----- ****** \\\\\\
      try {
        const response = await fetch('/backend/1.php', requestOptions);
        const data = await response.json();
        
        if( data.error !== null){ return "error"; }
        
        if( data.new_chat_id != null ){
          setChatID(data.new_chat_id)
        }
        return data.result;
      } catch (error) {
        console.error('Error al realizar la solicitud:', error);
        throw error; // Puedes lanzar el error para manejarlo en el código que llama a esta función
      }
    }


  };

  const visibilityStyle = {
    display: isVisible ? 'block' : 'none',
  };

  const handleSelectChange = () => {
    setStreamChecked(!isStreamChecked);
    // Otras acciones que desees ejecutar cuando cambie el estado del toggleMode
  }

  return (
    <div id="chat-window" style={visibilityStyle}>
      <>
        <ChatHeader onCloseButtonClick={onCloseButtonClick} />
        <ChatContent 
          content={chatContent}
          handleResendClick={resendMessage}
          onChangeSelectMode={handleSelectChange}
          isStreamChecked={isStreamChecked} 
          />
        <ChatInput onSendMessage={appendMessage} />
      </>
    </div>
  );
};

export default ChatWindow;
