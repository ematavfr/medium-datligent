'use client';

import React, { useState, useEffect, useCallback } from 'react';
import ArticleCard from '../components/ArticleCard';
import Filters from '../components/Filters';

const API_URL = 'http://localhost:6051'; // In production, use env var

export default function Home() {
    const [articles, setArticles] = useState([]);
    const [filters, setFilters] = useState({ dates: [], tags: [] });
    const [selectedDate, setSelectedDate] = useState(null);
    const [selectedTag, setSelectedTag] = useState('');
    const [selectedAuthor, setSelectedAuthor] = useState(null);
    const [selectedArticleId, setSelectedArticleId] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchFilters = async () => {
        try {
            const res = await fetch(`${API_URL}/filters`);
            const data = await res.json();
            setFilters(data);

            // Set default date to the latest one if not already set
            if (data.dates && data.dates.length > 0 && !selectedDate && !selectedAuthor) {
                setSelectedDate(data.dates[0]);
            }
        } catch (error) {
            console.error('Error fetching filters:', error);
        }
    };

    const fetchArticles = useCallback(async () => {
        if (!selectedDate && !selectedAuthor && filters.dates.length === 0) return;

        setLoading(true);
        try {
            let url = `${API_URL}/articles?`;
            // If tag is selected, we perform a global search (ignore date)
            if (selectedTag) {
                url += `tag=${encodeURIComponent(selectedTag)}&`;
            } else {
                if (selectedDate && !selectedAuthor) url += `date=${selectedDate}&`;
            }
            if (selectedAuthor) url += `author=${encodeURIComponent(selectedAuthor)}&`;

            const res = await fetch(url);
            const data = await res.json();
            setArticles(data);
        } catch (error) {
            console.error('Error fetching articles:', error);
        } finally {
            setLoading(false);
        }
    }, [selectedDate, selectedTag, selectedAuthor, filters.dates]);

    useEffect(() => {
        fetchFilters();
    }, []);

    useEffect(() => {
        if (selectedDate || selectedAuthor) {
            fetchArticles();
        }
    }, [selectedDate, selectedTag, selectedAuthor, fetchArticles]);

    const handlePrevDate = () => {
        const currentIndex = filters.dates.indexOf(selectedDate);
        if (currentIndex < filters.dates.length - 1) {
            setSelectedDate(filters.dates[currentIndex + 1]);
        }
    };

    const handleNextDate = () => {
        const currentIndex = filters.dates.indexOf(selectedDate);
        if (currentIndex > 0) {
            setSelectedDate(filters.dates[currentIndex - 1]);
        }
    };

    const hasPrev = selectedDate && filters.dates.indexOf(selectedDate) < filters.dates.length - 1;
    const hasNext = selectedDate && filters.dates.indexOf(selectedDate) > 0;

    return (
        <main className="min-h-screen p-8 max-w-[1600px] mx-auto">
            <header className="mb-8">
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-4xl font-bold text-blue-dark mb-2">
                            Medium Explorer
                        </h1>
                        <p className="text-gray-600">
                            Votre veille technologique quotidienne
                        </p>
                    </div>
                </div>
            </header>

            <Filters
                dates={filters.dates}
                selectedDate={selectedDate}
                selectedTag={selectedTag}
                onDateChange={setSelectedDate}
                onTagChange={setSelectedTag}
                onPrevDate={handlePrevDate}
                onNextDate={handleNextDate}
                hasPrev={hasPrev}
                hasNext={hasNext}
            />

            <div className="mb-6 flex justify-between items-end border-b border-gray-100 pb-4">
                <h2 className="text-xl font-semibold text-gray-800">
                    {selectedTag ? (
                        <>Articles avec les tags : <span className="text-blue-dark">{selectedTag}</span></>
                    ) : selectedAuthor ? (
                        <>Newsletters de : <span className="text-blue-dark">{selectedAuthor}</span></>
                    ) : (
                        `Newsletter du ${selectedDate ? new Date(selectedDate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) : '...'}`
                    )}
                    <span className="ml-3 text-sm font-normal text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                        {articles.length} articles
                    </span>
                </h2>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-dark"></div>
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {articles.map(article => (
                        <ArticleCard
                            key={article.id}
                            article={article}
                            isSelected={selectedArticleId === article.id}
                            onSelect={setSelectedArticleId}
                            onAuthorClick={(author) => {
                                setSelectedAuthor(author);
                                setSelectedArticleId(null);
                            }}
                        />
                    ))}
                </div>
            )}

            {!loading && articles.length === 0 && (
                <div className="text-center py-20 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200 mt-8">
                    <p className="text-gray-500 text-lg">Aucun article trouvé pour ces critères.</p>
                    {(selectedTag || selectedAuthor) && (
                        <button
                            onClick={() => {
                                setSelectedTag('');
                                setSelectedAuthor(null);
                            }}
                            className="mt-4 text-blue-600 hover:underline font-medium"
                        >
                            Effacer les filtres de recherche
                        </button>
                    )}
                </div>
            )}
            {!loading && selectedAuthor && articles.length > 0 && (
                <div className="mt-8 text-center">
                    <button
                        onClick={() => setSelectedAuthor(null)}
                        className="text-blue-600 hover:underline font-medium"
                    >
                        Retour à la vue par date
                    </button>
                </div>
            )}
        </main>
    );
}
