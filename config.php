<?php
// --- MySQL connection ---
$mysql = new mysqli("localhost", "root", "", "speech2sql");
if ($mysql->connect_error) {
    die("MySQL Connection failed: " . $mysql->connect_error);
}

// --- SQLite connection (for logs) ---
$sqlite = new SQLite3('logs.db');

// Create a logs table if not exists
$sqlite->exec("CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT,
    email TEXT,
    timestamp TEXT
)");
?>
