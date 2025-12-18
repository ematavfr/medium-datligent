import React from 'react';

const Filters = ({ dates, tags, selectedDate, selectedTag, onDateChange, onTagChange }) => {
    return (
        <div className="bg-white p-4 rounded-lg shadow-sm mb-6 flex flex-wrap gap-4 items-center">
            <div className="flex flex-col">
                <label className="text-sm text-gray-600 mb-1">Date de parution</label>
                <input
                    type="date"
                    value={selectedDate || ''}
                    onChange={(e) => onDateChange(e.target.value || null)}
                    className="border border-gray-300 rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-pastel"
                />
            </div>

            <div className="flex flex-col">
                <label className="text-sm text-gray-600 mb-1">Recherche par tag</label>
                <select
                    value={selectedTag || ''}
                    onChange={(e) => onTagChange(e.target.value || null)}
                    className="border border-gray-300 rounded-md p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-pastel"
                >
                    <option value="">Tous les tags</option>
                    {tags.map(tag => (
                        <option key={tag} value={tag}>{tag}</option>
                    ))}
                </select>
            </div>

            {(selectedDate || selectedTag) && (
                <button
                    onClick={() => { onDateChange(null); onTagChange(null); }}
                    className="mt-auto mb-1 text-sm text-red-500 hover:text-red-700 underline"
                >
                    Réinitialiser
                </button>
            )}
        </div>
    );
};

export default Filters;
