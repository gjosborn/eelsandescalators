import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface WinModalProps {
  isOpen: boolean;
  onNewGame: () => void;
  moveCount: number;
  winners: string[];
}

export const WinModal = ({ isOpen, onNewGame, moveCount, winners }: WinModalProps) => {
  const getPerformanceMessage = (moves: number) => {
    if (moves <= 10) return "🌟 Incredible! You're a true Bikini Bottom champion!";
    if (moves <= 20) return "🎉 Excellent! SpongeBob would be proud!";
    if (moves <= 30) return "😊 Great job! You've mastered the art of escalators!";
    if (moves <= 50) return "👍 Well done! You made it through the underwater adventure!";
    return "🎈 Congratulations! Persistence pays off in Bikini Bottom!";
  };

  return (
    <Dialog open={isOpen}>
      <DialogContent className="sm:max-w-md bg-gradient-to-br from-yellow-200 to-yellow-300 border-4 border-yellow-400">
        <DialogHeader className="text-center">
          <DialogTitle className="text-3xl font-bold text-blue-800 mb-2">
            🏆 Victory! 🏆
          </DialogTitle>
          <DialogDescription className="text-lg text-blue-700">
            {winners.length > 1
              ? `Winners: ${winners.join(", ")}`
              : `Winner: ${winners[0]}`}
          </DialogDescription>
        </DialogHeader>
        
        <div className="text-center py-6">
          <div className="text-6xl mb-4 animate-bounce">🎉</div>
          <p className="text-xl font-bold text-blue-800 mb-2">
            Completed in {moveCount} moves!
          </p>
          <p className="text-blue-700 mb-6">
            {getPerformanceMessage(moveCount)}
          </p>
          
          {/* Animated celebration elements */}
          <div className="relative overflow-hidden h-16 mb-4">
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl animate-pulse">🌊</span>
              <span className="text-2xl animate-bounce mx-2">🐠</span>
              <span className="text-2xl animate-pulse">🌊</span>
            </div>
          </div>
          
          <Button
            onClick={onNewGame}
            className="w-full py-6 text-lg font-bold bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105"
          >
            🎮 Play Again
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
