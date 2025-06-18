
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface GameBoardProps {
  playerPosition: number;
  onPositionUpdate: (position: number) => void;
}

// Escalators (go up) - start position: end position
const escalators = {
  1: 38,
  4: 14,
  9: 31,
  16: 6,
  21: 42,
  28: 84,
  36: 44,
  48: 26,
  51: 67,
  71: 91,
  80: 100
};

// Eels (go down) - start position: end position
const eels = {
  98: 78,
  95: 75,
  93: 73,
  87: 24,
  64: 60,
  62: 19,
  56: 53,
  49: 11,
  47: 26,
  16: 6
};

export const GameBoard = ({ playerPosition, onPositionUpdate }: GameBoardProps) => {
  const [displayPosition, setDisplayPosition] = useState(playerPosition);
  const [isMoving, setIsMoving] = useState(false);

  useEffect(() => {
    if (playerPosition !== displayPosition) {
      setIsMoving(true);
      
      // Animate to new position
      setTimeout(() => {
        setDisplayPosition(playerPosition);
        
        // Check for eels or escalators
        const escalatorDestination = escalators[playerPosition as keyof typeof escalators];
        const eelDestination = eels[playerPosition as keyof typeof eels];
        
        if (escalatorDestination) {
          setTimeout(() => {
            setDisplayPosition(escalatorDestination);
            onPositionUpdate(escalatorDestination);
          }, 800);
        } else if (eelDestination) {
          setTimeout(() => {
            setDisplayPosition(eelDestination);
            onPositionUpdate(eelDestination);
          }, 800);
        }
        
        setIsMoving(false);
      }, 300);
    }
  }, [playerPosition, displayPosition, onPositionUpdate]);

  const getSquareNumber = (row: number, col: number) => {
    const rowFromBottom = 9 - row;
    if (rowFromBottom % 2 === 0) {
      return rowFromBottom * 10 + col + 1;
    } else {
      return rowFromBottom * 10 + (10 - col);
    }
  };

  const getSquarePosition = (squareNum: number) => {
    if (squareNum === 0) return { row: 10, col: -1 }; // Start position
    
    const adjustedNum = squareNum - 1;
    const row = Math.floor(adjustedNum / 10);
    const rowFromBottom = 9 - row;
    let col;
    
    if (rowFromBottom % 2 === 0) {
      col = adjustedNum % 10;
    } else {
      col = 9 - (adjustedNum % 10);
    }
    
    return { row, col };
  };

  const hasEel = (squareNum: number) => {
    return eels[squareNum as keyof typeof eels] !== undefined;
  };

  const hasEscalator = (squareNum: number) => {
    return escalators[squareNum as keyof typeof escalators] !== undefined;
  };

  const playerPos = getSquarePosition(displayPosition);

  return (
    <div className="bg-gradient-to-br from-yellow-200 to-yellow-300 p-6 rounded-2xl shadow-2xl border-4 border-yellow-400">
      <div className="grid grid-cols-10 gap-1 bg-yellow-100 p-4 rounded-xl relative">
        {/* Board squares */}
        {Array.from({ length: 10 }, (_, row) =>
          Array.from({ length: 10 }, (_, col) => {
            const squareNum = getSquareNumber(row, col);
            const isEel = hasEel(squareNum);
            const isEscalator = hasEscalator(squareNum);
            const isPlayerHere = displayPosition === squareNum;
            
            return (
              <div
                key={`${row}-${col}`}
                className={cn(
                  "aspect-square rounded-lg border-2 flex items-center justify-center text-sm font-bold relative transition-all duration-300",
                  (row + col) % 2 === 0 ? "bg-blue-100 border-blue-200" : "bg-blue-50 border-blue-100",
                  isEel && "bg-red-200 border-red-300",
                  isEscalator && "bg-green-200 border-green-300",
                  isPlayerHere && "ring-4 ring-yellow-400 ring-opacity-75"
                )}
              >
                <span className="text-blue-800 z-10">{squareNum}</span>
                
                {/* Eel emoji */}
                {isEel && (
                  <span className="absolute inset-0 flex items-center justify-center text-2xl opacity-60">
                    🐍
                  </span>
                )}
                
                {/* Escalator emoji */}
                {isEscalator && (
                  <span className="absolute inset-0 flex items-center justify-center text-2xl opacity-60">
                    🪜
                  </span>
                )}
              </div>
            );
          })
        )}
        
        {/* Player piece */}
        {displayPosition > 0 && (
          <div
            className={cn(
              "absolute w-8 h-8 bg-yellow-400 rounded-full border-4 border-yellow-600 flex items-center justify-center text-lg font-bold transition-all duration-500 z-20 shadow-lg",
              isMoving && "scale-110 animate-bounce"
            )}
            style={{
              left: `${playerPos.col * 10 + 5}%`,
              top: `${playerPos.row * 10 + 5}%`,
              transform: "translate(-50%, -50%)"
            }}
          >
            🟡
          </div>
        )}
        
        {/* Start position indicator */}
        <div className="absolute -bottom-8 left-4 bg-green-400 px-3 py-1 rounded-full text-white font-bold text-sm border-2 border-green-600">
          START
        </div>
        
        {/* Finish position indicator */}
        <div className="absolute -top-8 right-4 bg-gold-400 px-3 py-1 rounded-full text-white font-bold text-sm border-2 border-yellow-600 bg-gradient-to-r from-yellow-400 to-yellow-500">
          FINISH
        </div>
      </div>
      
      {/* Legend */}
      <div className="mt-4 flex justify-center space-x-6 text-sm">
        <div className="flex items-center space-x-1">
          <span>🪜</span>
          <span className="text-green-700 font-semibold">Escalators</span>
        </div>
        <div className="flex items-center space-x-1">
          <span>🐍</span>
          <span className="text-red-700 font-semibold">Eels</span>
        </div>
      </div>
    </div>
  );
};
