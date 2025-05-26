import React from 'react';

interface PriceData {
  price: number;
  change: number;
}

interface PriceCardProps {
  pair: string;
  priceData: PriceData;
  onClick?: () => void;
  isSelected?: boolean;
}

const PriceCard: React.FC<PriceCardProps> = ({
  pair,
  priceData,
  onClick,
  isSelected = false
}) => {
  const isPositiveChange = priceData.change >= 0;

  return (
    <div 
      className={`
        bg-gray-800 rounded-lg p-4 
        hover:bg-gray-700 transition-colors cursor-pointer
        ${isSelected ? 'ring-2 ring-blue-500' : ''}
      `}
      onClick={onClick}
    >
      <div className="space-y-2">
        <span className="text-lg font-bold">{pair}</span>
        <div className="text-2xl">
          ${priceData.price.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          })}
        </div>
        <div className={isPositiveChange ? 'text-green-500' : 'text-red-500'}>
          {isPositiveChange ? '+' : ''}{priceData.change.toFixed(2)}%
        </div>
      </div>
    </div>
  );
};

export default PriceCard;