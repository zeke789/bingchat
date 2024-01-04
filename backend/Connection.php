<?php
class Connection
{
    private $host;
    private $dbname;
    private $username;
    private $password;
    private $charset;

    private $pdo;


    public function __construct($charset = 'utf8')
    {
        $this->charset = $charset;
        $this->host = 'localhost';
        $this->dbname = 'bing_chats';
        $this->username = 'root';
        $this->password = '';
        $this->connect();
    }

    private function connect()
    {
        $dsn = "mysql:host={$this->host};dbname={$this->dbname};charset={$this->charset}";

        try {
            $this->pdo = new PDO($dsn, $this->username, $this->password);
            $this->pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        } catch (PDOException $e) {
            die("Error de conexión: " . $e->getMessage());
        }
        return $this->pdo;
    }


    public function getPDO() { return $this->pdo; }

}
