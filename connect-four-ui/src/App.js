import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [board, setBoard] = useState([]);
  const [turn, setTurn] = useState(0);
  const [winner, setWinner] = useState(null);
  const [rows, setRows] = useState(6);
  const [cols, setCols] = useState(5);
  const [gameID, setGameID] = useState(null); // Assuming you have a game ID to track the game

  const newGame = async (rows, cols) => {
    const response = await axios.post('http://127.0.0.1:5000/new_game',
        { rows, cols },
        { withCredentials: true }
    );
    setBoard(response.data.board);
    setTurn(0);
    setWinner(null);
    setGameID(response.data.game_id); // Assuming the response contains a gameID
  };

  const playMove = async (col) => {
    if (winner !== null) return;

        // Debugging: Check the value of gameID
    console.log("Game ID: ${gameID}");
    let url = "http://127.0.0.1:5000/play/" + gameID
    console.log(url);
    try {
      const response = await axios.post(url, {
        col: col
      },
          {
        withCredentials: true  // Ensure credentials are included
      });
      if (response.data.error) {
        alert(response.data.error);
      } else {
        setBoard(response.data.board);
        setTurn(response.data.turn);
        if (response.data.winner !== "2") {
          setWinner(response.data.winner);
          if (response.data.winner === "1"){
            alert("Game Over! Winner: Computer");
          }
          else {
            alert("Game Over! Winner: Human Player");
          }
        }
      }
    } catch (error) {
      console.error('Error playing move:', error);
    }
  };

  const renderCell = (cell, rowIndex, colIndex) => {
    let color = 'white';
    if (cell === 0) color = 'yellow';
    if (cell === 1) color = 'red';
    return (
      <div
        key={`${rowIndex}-${colIndex}`}
        className="cell"
        style={{ backgroundColor: color }}
        data-col={colIndex}
        onClick={() => playMove(colIndex)}
      />
    );
  };

  const renderRow = (row, rowIndex) => {
    return (
      <div key={rowIndex} className="row">
        {row.map((cell, colIndex) => renderCell(cell, rowIndex, colIndex))}
      </div>
    );
  };

  return (
    <div className="App">
      <h1>Connect 4</h1>
      <div className="board">
        {board.map((row, rowIndex) => renderRow(row, rowIndex))}
      </div>
      <div>
        <label>
          Rows:
          <input
            type="number"
            value={rows}
            onChange={(e) => setRows(Number(e.target.value))}
          />
        </label>
        <label>
          Columns:
          <input
            type="number"
            value={cols}
            onChange={(e) => setCols(Number(e.target.value))}
          />
        </label>
        <button onClick={() => newGame(rows, cols)}>New Game</button>
      </div>
      {winner !== null && <h2>Winner: Player {winner}</h2>}
    </div>
  );
}

export default App;