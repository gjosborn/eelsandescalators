import { useState, useCallback } from "react";
import { GameBoard } from "@/components/GameBoard";
import { DiceRoller } from "@/components/DiceRoller";
import { GameControls } from "@/components/GameControls";
import { WinModal } from "@/components/WinModal";
import { toast } from "sonner";
import RegisterModal from "../components/Register";

export interface GameState {
  playerPosition: number;
  isGameActive: boolean;
  isRolling: boolean;
  hasWon: boolean;
  moveHistory: number[];
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
    playerPosition: 0,
    isGameActive: true,
    isRolling: false,
    hasWon: false,
    moveHistory: []
  });

  // State to control RegisterModal visibility
  const [isRegisterOpen, setRegisterOpen] = useState(false);

  const handleDiceRoll = useCallback((diceValue: number) => {
    if (!gameState.isGameActive || gameState.isRolling) return;

    setGameState(prev => ({ ...prev, isRolling: true }));
    
    setTimeout(() => {
      const newPosition = Math.min(gameState.playerPosition + diceValue, 100);
      const hasWon = newPosition === 100;
      
      setGameState(prev => ({
        ...prev,
        playerPosition: newPosition,
        isRolling: false,
        hasWon,
        isGameActive: !hasWon,
        moveHistory: [...prev.moveHistory, diceValue]
      }));

      if (hasWon) {
        toast.success("🎉 Congratulations! You've reached the top!");
      }
    }, 1500);
  }, [gameState.playerPosition, gameState.isGameActive, gameState.isRolling]);

  const resetGame = useCallback(() => {
    setGameState({
      playerPosition: 0,
      isGameActive: true,
      isRolling: false,
      hasWon: false,
      moveHistory: []
    });
    toast.info("🔄 New game started!");
  }, []);

  const handlePositionUpdate = useCallback((newPosition: number) => {
    setGameState(prev => ({
      ...prev,
      playerPosition: newPosition
    }));
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
          <RegisterModal open={isRegisterOpen} onClose={() => setRegisterOpen(false)} />
        </div>
        <p className="text-xl text-blue-100 drop-shadow text-center mb-8">
          The classic Bikini Bottom board game adventure!
        </p>

        <div className="grid lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
          {/* Game Board */}
          <div className="lg:col-span-3">
            <GameBoard 
              playerPosition={gameState.playerPosition}
              onPositionUpdate={handlePositionUpdate}
            />
          </div>

          {/* Game Controls */}
          <div className="lg:col-span-1 space-y-6">
            <DiceRoller 
              onRoll={handleDiceRoll} 
              disabled={!gameState.isGameActive || gameState.isRolling}
              isRolling={gameState.isRolling}
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
        moveCount={gameState.moveHistory.length}
      />
    </div>
  );
};

export default Index;
