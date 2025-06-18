
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface DiceRollerProps {
  onRoll: (value: number) => void;
  disabled: boolean;
  isRolling: boolean;
}

export const DiceRoller = ({ onRoll, disabled, isRolling }: DiceRollerProps) => {
  const [diceValue, setDiceValue] = useState(1);
  const [isAnimating, setIsAnimating] = useState(false);

  const rollDice = () => {
    if (disabled) return;
    
    setIsAnimating(true);
    
    // Show rolling animation
    const animationInterval = setInterval(() => {
      setDiceValue(Math.floor(Math.random() * 6) + 1);
    }, 100);
    
    // Stop animation and set final value
    setTimeout(() => {
      clearInterval(animationInterval);
      const finalValue = Math.floor(Math.random() * 6) + 1;
      setDiceValue(finalValue);
      setIsAnimating(false);
      onRoll(finalValue);
    }, 1000);
  };

  const getDiceEmoji = (value: number) => {
    const diceEmojis = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"];
    return diceEmojis[value - 1];
  };

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-xl border-2 border-blue-200">
      <h3 className="text-xl font-bold text-blue-800 mb-4 text-center">Roll the Dice!</h3>
      
      <div className="flex flex-col items-center space-y-4">
        <div
          className={cn(
            "w-20 h-20 bg-gradient-to-br from-white to-gray-100 rounded-xl border-4 border-gray-300 flex items-center justify-center text-4xl transition-all duration-200 shadow-lg",
            isAnimating && "animate-bounce scale-110",
            isRolling && "opacity-50"
          )}
        >
          {getDiceEmoji(diceValue)}
        </div>
        
        <Button
          onClick={rollDice}
          disabled={disabled}
          className={cn(
            "w-full py-6 text-lg font-bold rounded-xl transition-all duration-300",
            "bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700",
            "disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed",
            "shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95"
          )}
        >
          {isRolling ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
              Rolling...
            </>
          ) : (
            "🎲 Roll Dice"
          )}
        </Button>
        
        {diceValue && !isAnimating && (
          <p className="text-center text-blue-700 font-semibold">
            You rolled a {diceValue}!
          </p>
        )}
      </div>
    </div>
  );
};
