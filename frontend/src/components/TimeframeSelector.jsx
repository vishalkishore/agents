import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setSelectedTimeframe } from '../features/timeframe/timeframeSlice';

const TimeframeSelector = () => {
  const dispatch = useDispatch();
  const { availableTimeframes, selectedTimeframe } = useSelector(state => state.timeframe);

  return (
    <div className="flex items-center gap-0.5">
      {availableTimeframes.map((tf) => (
        <button
          key={tf.value}
          className={`px-2 py-1 rounded text-sm ${
            selectedTimeframe.value === tf.value
              ? 'bg-blue-600 text-white'
              : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
          }`}
          onClick={() => dispatch(setSelectedTimeframe(tf))}
        >
          {tf.label}
        </button>
      ))}
    </div>
  );
};

export default TimeframeSelector;
