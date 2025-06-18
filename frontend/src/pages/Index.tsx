import { useState, useCallback } from "react";
import { GameBoard } from "@/components/GameBoard";
import { DiceRoller } from "@/components/DiceRoller";
import { GameControls } from "@/components/GameControls";
import { WinModal } from "@/components/WinModal";
import { toast } from "sonner";
import RegisterModal from "../components/Register";

export interface GameState {
  playerPositions: number[];
  isGameActive: boolean;
  isRolling: boolean;
  hasWon: boolean;
  moveHistory: number[][];
  currentPlayer: number;
  winners: number[];
  playerNames: string[];
}

const closeButtonStyle: React.CSSProperties = {
    position: "absolute",
    top: 12,
    right: 12,
    background: "none",
    border: "none",
    fontSize: 20,
    cursor: "pointer",
    color: "#888",
};

const Index = () => {
  const [gameState, setGameState] = useState<GameState>({
    playerPositions: [0, 0],
    isGameActive: false,
    isRolling: false,
    hasWon: false,
    moveHistory: [[], []],
    currentPlayer: 0,
    winners: [],
    playerNames: ["Player 1", "Player 2"]
  });

  const [isRegisterOpen, setRegisterOpen] = useState(true);

  const handleRegister = (names: string[]) => {
    setGameState({
      playerPositions: Array(names.length).fill(0),
      isGameActive: true,
      isRolling: false,
      hasWon: false,
      moveHistory: Array(names.length).fill([]),
      currentPlayer: 0,
      winners: [],
      playerNames: names
    });
    setRegisterOpen(false);
  };

  const handleDiceRoll = useCallback((diceValue: number) => {
    if (!gameState.isGameActive || gameState.isRolling) return;
    const { currentPlayer, playerPositions, winners, playerNames, moveHistory } = gameState;
    if (winners.includes(currentPlayer)) return;
    setGameState(prev => ({ ...prev, isRolling: true }));
    setTimeout(() => {
      const newPositions = [...playerPositions];
      const newMoveHistory = moveHistory.map(arr => [...arr]);
      const newWinners = [...winners];
      const pos = Math.min(newPositions[currentPlayer] + diceValue, 100);
      newPositions[currentPlayer] = pos;
      newMoveHistory[currentPlayer].push(diceValue);
      let hasWon = false;
      if (pos === 100) {
        newWinners.push(currentPlayer);
        toast.success(`🎉 ${playerNames[currentPlayer]} wins!`);
        hasWon = true;
      }
      // Next player (skip winners)
      let next = currentPlayer;
      for (let i = 1; i <= playerNames.length; i++) {
        const candidate = (currentPlayer + i) % playerNames.length;
        if (!newWinners.includes(candidate)) {
          next = candidate;
          break;
        }
      }
      setGameState(prev => ({
        ...prev,
        playerPositions: newPositions,
        moveHistory: newMoveHistory,
        isRolling: false,
        hasWon: newWinners.length === playerNames.length,
        isGameActive: newWinners.length < playerNames.length,
        currentPlayer: next,
        winners: newWinners
      }));
    }, 1500);
  }, [gameState]);

  const resetGame = useCallback(() => {
    setRegisterOpen(true);
  }, []);

  const handlePositionUpdate = useCallback((newPosition: number) => {
    // Not used in multi-player mode
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-400 via-blue-500 to-blue-800 relative overflow-hidden">
      {/* Underwater Background Effects */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-10 w-4 h-4 bg-white rounded-full animate-pulse"></div>
        <div className="absolute top-40 right-20 w-3 h-3 bg-blue-200 rounded-full animate-bounce"></div>
        <div className="absolute bottom-40 left-1/4 w-2 h-2 bg-white rounded-full animate-ping"></div>
        <div className="absolute top-60 right-1/3 w-5 h-5 bg-blue-100 rounded-full animate-pulse"></div>
      </div>

      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="text-center mb-8 flex items-center justify-center relative">
          <h1 className="text-5xl font-bold text-yellow-300 mb-2 drop-shadow-lg">
            🪜 Eels and Escalators 🐍
          </h1>
          <button
            className="ml-4 px-4 py-2 bg-yellow-400 text-blue-900 font-semibold rounded shadow hover:bg-yellow-300 transition"
            onClick={() => setRegisterOpen(true)}
            type="button"
          >
            Register
          </button>
          {/* RegisterModal controlled by local state */}
          <RegisterModal open={isRegisterOpen} onClose={() => setRegisterOpen(false)} onRegister={handleRegister} />
        </div>
        <p className="text-xl text-blue-100 drop-shadow text-center mb-8">
          The classic Bikini Bottom board game adventure!
        </p>

        <div className="grid lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
          {/* Game Board */}
          <div className="lg:col-span-3">
            <GameBoard 
              playerPositions={gameState.playerPositions}
              currentPlayer={gameState.currentPlayer}
              playerNames={gameState.playerNames}
              winners={gameState.winners}
            />
          </div>

          {/* Game Controls */}
          <div className="lg:col-span-1 space-y-6">
            <DiceRoller 
              onRoll={handleDiceRoll} 
              disabled={!gameState.isGameActive || gameState.isRolling}
              isRolling={gameState.isRolling}
              currentPlayer={gameState.currentPlayer}
              playerNames={gameState.playerNames}
            />
            
            <GameControls 
              gameState={gameState}
              onReset={resetGame}
            />
          </div>
        </div>
      </div>

      {/* Win Modal */}
      <WinModal 
        isOpen={gameState.hasWon} 
        onNewGame={resetGame}
        moveCount={gameState.moveHistory.reduce((a, b) => a + b.length, 0)}
        winners={gameState.winners.map(i => gameState.playerNames[i])}
      />
    </div>
  );
};

export default Index;
