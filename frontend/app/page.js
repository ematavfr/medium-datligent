'use client';

import React, { useState, useEffect } from 'react';
import ArticleCard from '../components/ArticleCard';
import Filters from '../components/Filters';

const API_URL = 'http://localhost:6051'; // In production, use env var

export default function Home() {
    const [articles, setArticles] = useState([]);
    const [filters, setFilters] = useState({ dates: [], tags: [] });
    const [selectedDate, setSelectedDate] = useState(null);
    const [selectedTag, setSelectedTag] = useState(null);
    const [selectedArticleId, setSelectedArticleId] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchFilters();
        fetchArticles();
    }, []);

    useEffect(() => {
        fetchArticles();
    }, [selectedDate, selectedTag]);

    const fetchFilters = async () => {
        try {
            const res = await fetch(`${API_URL}/filters`);
            const data = await res.json();
            setFilters(data);
        } catch (error) {
            console.error('Error fetching filters:', error);
        }
    };

    const fetchArticles = async () => {
        setLoading(true);
        try {
            let url = `${API_URL}/articles?`;
            if (selectedDate) url += `date=${selectedDate}&`;
            if (selectedTag) url += `tag=${selectedTag}`;

            const res = await fetch(url);
            const data = await res.json();
            setArticles(data);
        } catch (error) {
            console.error('Error fetching articles:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen p-8 max-w-[1600px] mx-auto">
            <header className="mb-8">
                <h1 className="text-4xl font-bold text-blue-dark mb-2">
                    Explorateur articles Medium
                </h1>
                <p className="text-gray-600">
                    Votre veille technologique quotidienne
                </p>
            </header>

            <Filters
                dates={filters.dates}
                tags={filters.tags}
                selectedDate={selectedDate}
                selectedTag={selectedTag}
                onDateChange={setSelectedDate}
                onTagChange={setSelectedTag}
            />

            <div className="mb-4 text-xl font-semibold text-gray-700">
                Articles medium du {selectedDate ? new Date(selectedDate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) : new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })} ({articles.length} articles)
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
                        />
                    ))}
                </div>
            )}

            {!loading && articles.length === 0 && (
                <div className="text-center text-gray-500 mt-12">
                    Aucun article trouvé pour ces critères.
                </div>
            )}
        </main>
    );
}
