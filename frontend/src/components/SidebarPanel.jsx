import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Activity, Waves, TrendingDown } from 'lucide-react';
import { setSelectedIndicators } from '../features/indicators/indicatorsSlice';

const SidebarPanel = () => {
  const dispatch = useDispatch();
  const { availableIndicators, selectedIndicators } = useSelector(state => state.indicators);

  // Map icon strings to actual components
  const getIcon = (iconName) => {
    switch(iconName) {
      case 'Activity': return Activity;
      case 'Waves': return Waves;
      case 'TrendingDown': return TrendingDown;
      default: return Activity;
    }
  };

  const handleToggleIndicator = (value) => {
    if (selectedIndicators.includes(value)) {
      dispatch(setSelectedIndicators(selectedIndicators.filter(item => item !== value)));
    } else {
      dispatch(setSelectedIndicators([...selectedIndicators, value]));
    }
  };

  return (
    <div className="p-2">
      <h3 className="font-bold text-sm mb-2 text-slate-300">Indicators</h3>
      <div className="space-y-1">
        {availableIndicators.map((item) => {
          const Icon = getIcon(item.icon);
          return (
            <div 
              key={item.value}
              className={`p-2 rounded cursor-pointer ${
                selectedIndicators.includes(item.value) 
                  ? 'bg-blue-900/50 border border-blue-500/50' 
                  : 'bg-slate-800 hover:bg-slate-700'
              }`}
              onClick={() => handleToggleIndicator(item.value)}
            >
              <div className="flex items-center gap-2">
                <Icon className="h-4 w-4 text-blue-400" />
                <span>{item.label}</span>
              </div>
              {selectedIndicators.includes(item.value) && (
                <p className="text-xs text-slate-400 mt-1">{item.description}</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SidebarPanel;
