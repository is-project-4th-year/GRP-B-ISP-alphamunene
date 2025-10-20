// server.js (MySQL version)
import express from "express";
import multer from "multer";
import cors from "cors";
import dotenv from "dotenv";
import fs from "fs";
import OpenAI from "openai";
import mysql from "mysql2/promise";

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(".")); // serve index.html etc.

const upload = multer({ dest: "uploads/" });
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// 🗄️ MySQL connection
const db = await mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "", // your MySQL password if any
  database: "speech2sql"
});

// 🎤 1. Transcribe endpoint
app.post("/api/transcribe", upload.single("audio"), async (req, res) => {
  try {
    const audioPath = req.file.path;
    const transcript = await openai.audio.transcriptions.create({
      file: fs.createReadStream(audioPath),
      model: "whisper-1"
    });
    fs.unlinkSync(audioPath);
    res.json({ text: transcript.text });
  } catch (err) {
    console.error("Transcription error:", err);
    res.status(500).json({ error: "Transcription failed" });
  }
});

// 🧠 2. Query endpoint (convert speech → SQL → run on MySQL)
app.post("/api/query", async (req, res) => {
  const naturalQuery = req.body.query;
  try {
    const sqlPrompt = `
      Convert the following natural language request into a valid MySQL SQL query.
      User request: "${naturalQuery}"
      Do not include explanations — respond with ONLY the SQL query.
    `;

    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: sqlPrompt }]
    });

    const sqlQuery = completion.choices[0].message.content.trim();
    console.log("Generated SQL:", sqlQuery);

    let [result] = [null];
    try {
      [result] = await db.query(sqlQuery);
    } catch (sqlErr) {
      result = [{ error: sqlErr.message }];
    }

    // Save query + result in MySQL
    await db.execute(
      "INSERT INTO history (query, sql_query, result) VALUES (?, ?, ?)",
      [naturalQuery, sqlQuery, JSON.stringify(result)]
    );

    res.json({ success: true, sql: sqlQuery, result });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Query failed" });
  }
});

// 🕒 3. History endpoint
app.get("/api/history", async (req, res) => {
  const [rows] = await db.query("SELECT * FROM history ORDER BY created_at DESC LIMIT 20");
  res.json(rows);
});

// 🚀 Start server
const PORT = 5000;
app.listen(PORT, () => console.log(`✅ MySQL Speech2SQL backend running at http://localhost:${PORT}`));
