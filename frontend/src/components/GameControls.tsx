import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { GameState } from "@/pages/Index";

interface GameControlsProps {
  gameState: GameState;
  onReset: () => void;
}

export const GameControls = ({ gameState, onReset }: GameControlsProps) => {
  return (
    <div className="space-y-4">
      {/* Game Status */}
      <Card className="bg-white/90 backdrop-blur-sm p-4 border-2 border-blue-200">
        <h3 className="text-lg font-bold text-blue-800 mb-3">Game Status</h3>
        <div className="space-y-2 text-sm">
          {gameState.playerNames.map((name, idx) => (
            <div className="flex justify-between" key={idx}>
              <span className={
                `font-bold ${gameState.currentPlayer === idx ? 'text-yellow-600' : gameState.winners.includes(idx) ? 'text-green-600' : 'text-blue-800'}`
              }>
                {name} {gameState.currentPlayer === idx ? '(Your turn)' : gameState.winners.includes(idx) ? '🏆' : ''}
              </span>
              <span>{gameState.playerPositions[idx]}/100</span>
              <span>Moves: {gameState.moveHistory[idx].length}</span>
            </div>
          ))}
          <div className="flex justify-between">
            <span className="text-blue-600">Status:</span>
            <span className={`font-bold ${gameState.hasWon ? 'text-green-600' : gameState.isGameActive ? 'text-blue-600' : 'text-gray-600'}`}>
              {gameState.hasWon ? '🏆 Game Over!' : gameState.isGameActive ? '🎮 Playing' : '⏸️ Paused'}
            </span>
          </div>
        </div>
        {/* Progress Bar for all players */}
        <div className="mt-4">
          {gameState.playerNames.map((name, idx) => (
            <div key={idx} className="mb-1">
              <div className="w-full bg-blue-100 rounded-full h-3 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-full rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${gameState.playerPositions[idx]}%` }}
                ></div>
              </div>
              <p className="text-xs text-blue-600 mt-1 text-center">
                {name}: {gameState.playerPositions[idx]}% Complete
              </p>
            </div>
          ))}
        </div>
      </Card>
      {/* Controls */}
      <Card className="bg-white/90 backdrop-blur-sm p-4 border-2 border-blue-200">
        <h3 className="text-lg font-bold text-blue-800 mb-3">Controls</h3>
        <Button
          onClick={onReset}
          variant="outline"
          className="w-full py-6 text-lg font-bold border-2 border-red-300 text-red-600 hover:bg-red-50 hover:border-red-400 transition-all duration-300"
        >
          🔄 New Game
        </Button>
      </Card>
      {/* Move History */}
      {gameState.moveHistory.some(arr => arr.length > 0) && (
        <Card className="bg-white/90 backdrop-blur-sm p-4 border-2 border-blue-200">
          <h3 className="text-lg font-bold text-blue-800 mb-3">Recent Moves</h3>
          <div className="max-h-32 overflow-y-auto">
            {gameState.playerNames.map((name, idx) => (
              <div key={idx} className="mb-2">
                <span className="font-bold text-blue-700">{name}:</span>
                <div className="grid grid-cols-6 gap-1">
                  {gameState.moveHistory[idx].slice(-12).map((move, index) => (
                    <div
                      key={index}
                      className="bg-blue-100 rounded text-center py-1 text-sm font-bold text-blue-800"
                    >
                      {move}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
      {/* Game Tips */}
      <Card className="bg-white/90 backdrop-blur-sm p-4 border-2 border-blue-200">
        <h3 className="text-lg font-bold text-blue-800 mb-3">🐠 Game Tips</h3>
        <div className="text-sm text-blue-700 space-y-2">
          <p>🪜 <strong>Escalators</strong> help you climb up!</p>
          <p>🐍 <strong>Eels</strong> make you slide down!</p>
          <p>🎯 Reach square 100 to win!</p>
        </div>
      </Card>
    </div>
  );
};
