import React from 'react';
import { ChevronLeft, ChevronRight, X } from 'lucide-react';

const Filters = ({
    dates,
    selectedDate,
    selectedTag,
    onDateChange,
    onTagChange,
    onPrevDate,
    onNextDate,
    hasPrev,
    hasNext
}) => {
    return (
        <div className="bg-white p-4 rounded-lg shadow-sm mb-6 flex flex-wrap gap-4 items-center border border-gray-100">
            <div className={`flex flex-col ${selectedTag ? 'opacity-50' : ''}`}>
                <label className="text-sm font-medium text-gray-700 mb-1">
                    Date de la newsletter {selectedTag && <span className="text-[10px] text-orange-600 font-normal">(Désactivé en recherche par tag)</span>}
                </label>
                <div className="flex items-center gap-2">
                    <button
                        onClick={onPrevDate}
                        disabled={!hasPrev || !!selectedTag}
                        className={`p-2 rounded-md border ${hasPrev && !selectedTag ? 'hover:bg-gray-50 border-gray-300' : 'opacity-30 border-gray-200 cursor-not-allowed'}`}
                        title={selectedTag ? "Désactivé en recherche par tag" : "Newsletter précédente"}
                    >
                        <ChevronLeft size={18} />
                    </button>

                    <input
                        type="date"
                        value={selectedDate || ''}
                        disabled={!!selectedTag}
                        onChange={(e) => onDateChange(e.target.value || null)}
                        className={`border border-gray-300 rounded-md p-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-pastel ${selectedTag ? 'bg-gray-50 cursor-not-allowed' : ''}`}
                    />

                    <button
                        onClick={onNextDate}
                        disabled={!hasNext || !!selectedTag}
                        className={`p-2 rounded-md border ${hasNext && !selectedTag ? 'hover:bg-gray-50 border-gray-300' : 'opacity-30 border-gray-200 cursor-not-allowed'}`}
                        title={selectedTag ? "Désactivé en recherche par tag" : "Newsletter suivante"}
                    >
                        <ChevronRight size={18} />
                    </button>
                </div>
            </div>

            <div className="flex flex-col flex-1 min-w-[280px]">
                <label className="text-sm font-medium text-gray-700 mb-1">Filtrer par tags (max 3, séparés par des virgules)</label>
                <div className="relative">
                    <input
                        type="text"
                        value={selectedTag || ''}
                        placeholder="Ex: AI, Python, Data"
                        onChange={(e) => {
                            const val = e.target.value;
                            // Basic validation for max 3 tags could be done here or in the search
                            onTagChange(val);
                        }}
                        className="border border-gray-300 rounded-md p-1.5 pl-3 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-pastel w-full"
                    />
                    {selectedTag && (
                        <button
                            onClick={() => onTagChange('')}
                            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                            <X size={16} />
                        </button>
                    )}
                </div>
                <p className="text-[10px] text-gray-500 mt-1">Recherche par expression 'OU' (OR) entre les tags.</p>
            </div>
        </div>
    );
};

export default Filters;
