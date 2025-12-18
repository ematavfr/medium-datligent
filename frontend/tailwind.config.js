/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                beige: {
                    100: '#f5f5dc', // Light beige
                    200: '#e8e8c8',
                },
                blue: {
                    pastel: '#aec6cf', // Pastel blue
                    dark: '#00008b',   // Dark blue
                }
            },
        },
    },
    plugins: [],
}
