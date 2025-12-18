import React from 'react';

const ArticleCard = ({ article, isSelected, onSelect }) => {
    return (
        <div
            onClick={() => onSelect(article.id)}
            className={`
        cursor-pointer 
        bg-white 
        p-4 
        rounded-lg 
        shadow-md 
        transition-all 
        duration-200 
        hover:shadow-2xl 
        hover:-translate-y-2
        hover:scale-[1.02]
        flex flex-col
        h-full
        ${isSelected ? 'border-4 border-blue-dark shadow-inner bg-gray-50' : 'border border-gray-200'}
      `}
            style={{
                boxShadow: isSelected ? 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)' : '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
            }}
        >
            {article.image_url && (
                <img
                    src={article.image_url}
                    alt={article.title}
                    className="w-full h-40 object-cover rounded-md mb-3"
                />
            )}

            <h3 className="text-lg font-bold text-blue-pastel mb-2 line-clamp-2 hover:text-blue-600">
                <a href={article.url} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()}>
                    {article.title}
                </a>
            </h3>

            <div className="text-xs text-gray-500 mb-2 flex justify-between">
                <span>{article.author}</span>
                <span>{article.publication_date}</span>
            </div>

            <p className="text-sm text-gray-700 mb-3 line-clamp-3 flex-grow">
                {article.summary}
            </p>

            <div className="mt-auto">
                <div className="flex flex-wrap gap-1 mb-2">
                    {article.tags && article.tags.map((tag, idx) => (
                        <span key={idx} className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full">
                            {tag}
                        </span>
                    ))}
                </div>
                <div className="text-xs text-gray-400 text-right">
                    {article.reading_time}
                </div>

            </div>
        </div>
    );
};

export default ArticleCard;
