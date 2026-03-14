import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DB_FILE = path.join(__dirname, 'db.json');

const app = express();
app.use(cors());
app.use(express.json());

// Initialize DB if not exists
if (!fs.existsSync(DB_FILE)) {
  fs.writeFileSync(DB_FILE, JSON.stringify({ users: [], predictions: [] }));
}

// GET Leaders
app.get('/api/leaderboard', (req, res) => {
  const data = JSON.parse(fs.readFileSync(DB_FILE));
  res.json(data);
});

// POST Prediction
app.post('/api/predict', (req, res) => {
  const { username, round, predictions } = req.body;
  if (!username || !round) return res.status(400).json({ error: 'Missing data' });

  const data = JSON.parse(fs.readFileSync(DB_FILE));
  
  // Update or Add user
  let user = data.users.find(u => u.username === username);
  if (!user) {
    user = { username, score: 0, joined: new Date().toISOString() };
    data.users.push(user);
  }

  // Update or Add prediction
  const predIndex = data.predictions.findIndex(p => p.username === username && p.round === round);
  const predictionEntry = { username, round, predictions, timestamp: new Date().toISOString() };
  
  if (predIndex > -1) {
    data.predictions[predIndex] = predictionEntry;
  } else {
    data.predictions.push(predictionEntry);
  }

  fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));
  res.json({ success: true, user });
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`F1 Prediction Server running on http://localhost:${PORT}`);
});
