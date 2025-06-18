import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface GameBoardProps {
  playerPositions: number[];
  currentPlayer: number;
  playerNames: string[];
  winners: number[];
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

export const GameBoard = ({ playerPositions, currentPlayer, playerNames, winners }: GameBoardProps) => {
  // State to track the visual position of the player (for animations)
  const [displayPositions, setDisplayPositions] = useState(playerPositions);
  // State to indicate if the player piece is currently moving/animating
  const [isMoving, setIsMoving] = useState(false);

  // Effect hook to handle player movement and eel/escalator interactions
  useEffect(() => {
    // Only trigger movement if the player position has actually changed
    if (playerPositions[currentPlayer] !== displayPositions[currentPlayer]) {
      setIsMoving(true);
      
      // First animation: move to the dice roll position
      setTimeout(() => {
        const newPositions = [...displayPositions];
        newPositions[currentPlayer] = playerPositions[currentPlayer];
        setDisplayPositions(newPositions);
        
        // Check if the new position has an escalator or eel
        const escalatorDestination = escalators[playerPositions[currentPlayer] as keyof typeof escalators];
        const eelDestination = eels[playerPositions[currentPlayer] as keyof typeof eels];
        
        // If there's an escalator at this position, move up after a delay
        if (escalatorDestination) {
          setTimeout(() => {
            const updatedPositions = [...newPositions];
            updatedPositions[currentPlayer] = escalatorDestination;
            setDisplayPositions(updatedPositions);
          }, 800); // 800ms delay before escalator activation
        } 
        // If there's an eel at this position, slide down after a delay
        else if (eelDestination) {
          setTimeout(() => {
            const updatedPositions = [...newPositions];
            updatedPositions[currentPlayer] = eelDestination;
            setDisplayPositions(updatedPositions);
          }, 800); // 800ms delay before eel slide
        }
        
        setIsMoving(false);
      }, 300); // 300ms for initial movement animation
    }
  }, [playerPositions, displayPositions, currentPlayer]);

  /**
   * Calculate the square number for a given row and column position
   * The board follows a snake pattern: even rows go left-to-right, odd rows go right-to-left
   * Row 0 (bottom) = squares 1-10, Row 1 = squares 11-20, etc.
   */
  const getSquareNumber = (row: number, col: number) => {
    const rowFromBottom = 9 - row; // Convert from top-down to bottom-up indexing
    if (rowFromBottom % 2 === 0) {
      // Even rows (0, 2, 4, etc.): left to right numbering
      return rowFromBottom * 10 + col + 1;
    } else {
      // Odd rows (1, 3, 5, etc.): right to left numbering
      return rowFromBottom * 10 + (10 - col);
    }
  };

  /**
   * Calculate the grid row and column position for a given square number
   * This is used for CSS positioning of the player piece
   */
  const getSquarePosition = (squareNum: number) => {
    // Handle starting position (before square 1)
    if (squareNum === 0) return { row: 10, col: 0 };
    
    // Convert square number to 0-based index
    const adjustedNum = squareNum - 1;
    
    // Calculate which row from the bottom (0-9)
    const rowFromBottom = Math.floor(adjustedNum / 10);
    
    // Convert to grid row (top-down, 0-9)
    const row = 9 - rowFromBottom;
    
    let col;
    // Determine column based on row direction (snake pattern)
    if (rowFromBottom % 2 === 0) {
      // Even rows: left to right
      col = adjustedNum % 10;
    } else {
      // Odd rows: right to left
      col = 9 - (adjustedNum % 10);
    }
    
    return { row, col };
  };

  /**
   * Check if a square has an eel (slide down)
   */
  const hasEel = (squareNum: number) => {
    return eels[squareNum as keyof typeof eels] !== undefined;
  };

  /**
   * Check if a square has an escalator (climb up)
   */
  const hasEscalator = (squareNum: number) => {
    return escalators[squareNum as keyof typeof escalators] !== undefined;
  };

  // Get the current visual positions of all players for CSS positioning
  const playerPieces = playerPositions.map((pos, idx) => {
    const playerPos = getSquarePosition(pos);
    const isCurrent = idx === currentPlayer;
    const isWinner = winners.includes(idx);
    return pos > 0 ? (
      <div
        key={idx}
        className={cn(
          "absolute w-8 h-8 rounded-full border-4 flex items-center justify-center text-lg font-bold transition-all duration-500 z-20 shadow-lg",
          isCurrent ? "bg-yellow-400 border-yellow-600 animate-bounce scale-110" : isWinner ? "bg-green-400 border-green-600" : "bg-blue-400 border-blue-600"
        )}
        style={{
          left: `${(playerPos.col + 0.5) * (100 / 10)}%`,
          top: `${(playerPos.row + 0.5) * (100 / 10)}%`,
          transform: "translate(-50%, -50%)"
        }}
        title={playerNames[idx]}
      >
        {String.fromCodePoint(0x1F7E1 + idx)}
      </div>
    ) : null;
  });

  return (
    <div className="bg-gradient-to-br from-yellow-200 to-yellow-300 p-6 rounded-2xl shadow-2xl border-4 border-yellow-400">
      <div className="grid grid-cols-10 gap-1 bg-yellow-100 p-4 rounded-xl relative">
        {/* Generate the 10x10 grid of board squares */}
        {Array.from({ length: 10 }, (_, row) =>
          Array.from({ length: 10 }, (_, col) => {
            const squareNum = getSquareNumber(row, col);
            const isEel = hasEel(squareNum);
            const isEscalator = hasEscalator(squareNum);
            const isPlayerHere = displayPositions.includes(squareNum);
            
            return (
              <div
                key={`${row}-${col}`}
                className={cn(
                  // Base square styling
                  "aspect-square rounded-lg border-2 flex items-center justify-center text-sm font-bold relative transition-all duration-300",
                  // Alternating colors for checkerboard pattern
                  (row + col) % 2 === 0 ? "bg-blue-100 border-blue-200" : "bg-blue-50 border-blue-100",
                  // Special colors for eels and escalators
                  isEel && "bg-red-200 border-red-300",
                  isEscalator && "bg-green-200 border-green-300",
                  // Highlight when player is on this square
                  isPlayerHere && "ring-4 ring-yellow-400 ring-opacity-75"
                )}
              >
                {/* Square number */}
                <span className="text-blue-800 z-10">{squareNum}</span>
                
                {/* Eel emoji for squares with eels */}
                {isEel && (
                  <span className="absolute inset-0 flex items-center justify-center text-2xl opacity-60">
                    🐍
                  </span>
                )}
                
                {/* Escalator emoji for squares with escalators */}
                {isEscalator && (
                  <span className="absolute inset-0 flex items-center justify-center text-2xl opacity-60">
                    🪜
                  </span>
                )}
              </div>
            );
          })
        )}
        
        {/* Player pieces - dynamically generated for each player */}
        {playerPieces}
        
        {/* Start position indicator */}
        <div className="absolute -bottom-8 left-4 bg-green-400 px-3 py-1 rounded-full text-white font-bold text-sm border-2 border-green-600">
          START
        </div>
        
        {/* Finish position indicator */}
        <div className="absolute -top-8 right-4 bg-gold-400 px-3 py-1 rounded-full text-white font-bold text-sm border-2 border-yellow-600 bg-gradient-to-r from-yellow-400 to-yellow-500">
          FINISH
        </div>
      </div>
      
      {/* Legend explaining the game elements */}
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