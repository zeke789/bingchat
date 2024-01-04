<?php
header('Access-Control-Allow-Credentials: true');
header('Access-Control-Max-Age: 86400');    // cache for 1 day
if (isset($_SERVER['HTTP_ACCESS_CONTROL_REQUEST_HEADERS'])){
  header("Access-Control-Allow-Headers: {$_SERVER['HTTP_ACCESS_CONTROL_REQUEST_HEADERS']}");
}
header("Access-Control-Allow-Headers: x-requested-with ");
header("Access-Control-Allow-Headers: *");
header("Access-Control-Allow-Origin: *");


require_once("Connection.php");

/*
* !! ------>> CAMBIAR API_URL <<------ !!
*/
define("API_URL", "URL_PYTHON_API");



function requestWithStream( $msg, $msgHistory )
{
    // ===================== STREAM MODE ===================== \\
    $userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36";
    $data = [ 'msj' => $msg, "tone"=>"Creative", "return_transfer"=>"stream" ];
    $data['hist'] = $msgHistory;

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, API_URL);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            "User-Agent: $userAgent"
    ]);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_WRITEFUNCTION, function ($ch, $chunk) {
        global $accumulatedResponse;
        $accumulatedResponse .= $chunk;
        echo $chunk;
        ob_flush();
        flush();
        return strlen($chunk);
    });
    $response = curl_exec($ch);
    curl_close($ch);
}



function requestWithNormalResponse($msg,$msgHistory)
{
    $userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36";
    $data = [ 'msj' => $msg, "return_transfer"=>"normal" ];
    $data['hist'] = $msgHistory;    
    $jsonData = json_encode($data);
    // Configurar la solicitud cURL
    $ch = curl_init(API_URL);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
    curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        "User-Agent: $userAgent"
    ]);
    $response = curl_exec($ch);
    if (!$response) {
        saveLog( 'Error de cURL: ' . curl_error($ch) );
        die(json_encode(["error" => "error1"]));
    }
    curl_close($ch);
    try {
        $resp = json_decode($response);    
    } catch (Exception $e) {
        saveLog( "ERR TRYCATCH = " .$e->getMessage() );
        die(json_encode(["error" => "error2"]));
    }
    return $resp;
}


function insertNewChat($history)
{
    $conn = new Connection();
    $pdo = $conn->getPDO();
    $dateNow = new DateTime();
    $date = $dateNow->format("Y-m-d H:i:s");
    $q = "INSERT INTO chats SET messages = ?, fecha = ?";
    $stmt = $pdo->prepare($q);
    if( $stmt->execute([$history,$date]) ) 
        return [ true,$pdo->lastInsertId() ];
    return [ false, $stmt->errorInfo() ];
}

function updateChat($id, $history)
{
    $conn = new Connection();
    $pdo = $conn->getPDO();
    $dateNow = new DateTime();
    $date = $dateNow->format("Y-m-d H:i:s");
    $q = "UPDATE chats SET messages = ?, fecha = ? WHERE id = ?";
    $stmt = $pdo->prepare($q);
    if( $stmt->execute([$history,$date, $id]) ) 
        return [true];
    return [false,$stmt->errorInfo()];
}


function getMessageHistory($chatID)
{
    $conn = new Connection();
    $pdo = $conn->getPDO();
    $q = "SELECT id, fecha, messages FROM chats WHERE id = ?";
    $stmt = $pdo->prepare($q);
    if( $stmt->execute([$chatID]) ){
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}



function saveLog($text)
{
    try{
        file_put_contents("debug.txt", json_encode( $text) . "\r\n==========================================================\r\n\r\n", FILE_APPEND);    
    }catch(Exception $e){
        file_put_contents("debug.txt", $text . "\r\n==========================================================\r\n\r\n", FILE_APPEND);
    }
    
}



$postData = file_get_contents("php://input");
$data = json_decode($postData, true);

$histID = !empty($data["hid"]) ? $data["hid"] : null;
$msg = !empty($data["msg"]) ? $data["msg"] : null;
$tone = !empty($data["tone"]) ? $data["tone"] : null;
$mode = !empty($data["mode"]) ? $data["mode"] : null;

#$histID = 3;

/*
$return = [
    "result" => "test from backend 2",
    'new_chat_id' => isset($newChatID) ? $newChatID : null,
    "error" => 123
];
die(json_encode($return));
*/


#$msgHistory = '[{"content": "Hola, estoy aquí para servirte", "role": "system"}, {"content": "hola, sabes hacer cálculos matemáticos?", "role": "user"}, {"role": "system", "content": "si, puedo hacer cálculos matemáticos"}]';    
#$hist = 1;

if( $histID != null ){
    $msgHistory = getMessageHistory($histID);
    $msgHistory = $msgHistory[0]['messages'];
}else{
    $msgHistory = null;
}



if( $mode === "s"){
    $accumulatedResponse = '';
    requestWithStream($msg, $msgHistory); # THIS ALSO WILL UPDATE $accumulatedResponse

    if( $msgHistory != null){
        $history = json_decode($msgHistory);
        $history[] = ["role"=>"user", "content"=>$msg];
        $history[] = ["role"=>"system", "content"=>$accumulatedResponse];
        $history = json_encode($history, JSON_UNESCAPED_UNICODE);
        $update = updateChat($histID, $history);
        if( !$update[0] ){
            saveLog("Error UPDATE => " . $update[1] );
        }#else{}
    }else{
        // IF IS FIRST MESSAGE THEN CREATE NEW "MESSAGES HISTORY" WITH FIRST USER PROMPT
        $messages = [
            ["role"=>"system", "content"=>"Hola, estoy aquí para servirte de la manera mas creativa y precisa posible"],
            ["role"=>"user", "content"=>$msg],
            ["role"=>"system", "content"=>$accumulatedResponse]
        ];
        $newChatID = insertNewChat( json_encode( $messages, JSON_UNESCAPED_UNICODE ) );
        
        if( $newChatID[0] )
            $newChatID = $newChatID[1];
        else
            saveLog( "Error al agregar new chat => " . $newChatID[1] );
        echo json_encode(["chatid"=>$newChatID]);die;
    }

}else{

    $resp = requestWithNormalResponse($msg, $msgHistory);
    $result = isset($resp->resultado) ? $resp->resultado : null;
    
    #var_dump($resp); echo '<hr>'; var_dump($result);die;
    if($result === null){
        saveLog($resp);
        die(json_encode(["error" => "error3"]));
    }

    
    if( $msgHistory != null ){
        $history = json_decode($msgHistory);
        $history[] = ["role"=>"user", "content"=>$msg];
        $history[] = ["role"=>"system", "content"=>$result];
        $history = json_encode($history, JSON_UNESCAPED_UNICODE);
        $update = updateChat($histID, $history);
        if( !$update[0] ){
            saveLog("Error UPDATE => " . $update[1] );
        }else{
            
        }

    }else{
        // IF IS FIRST MESSAGE THEN CREATE NEW "MESSAGES HISTORY" WITH FIRST USER PROMPT
        $messages = [
            ["role"=>"system", "content"=>"Hola, estoy aquí para servirte de la manera mas creativa y precisa posible"],
            ["role"=>"user", "content"=>$msg],
            ["role"=>"system", "content"=>$result]
        ];
        $newChatID = insertNewChat( json_encode( $messages, JSON_UNESCAPED_UNICODE ) );
        if( $newChatID[0] )
            $newChatID = $newChatID[1];
        else
            saveLog( "Error al agregar new chat => " . $newChatID[1] );
    }


    $return = [
        "result" => $result,
        'new_chat_id' => isset($newChatID) ? $newChatID : $histID,
        "error" => null
    ];

    die( json_encode( $return, JSON_UNESCAPED_UNICODE ) );

}


?>
