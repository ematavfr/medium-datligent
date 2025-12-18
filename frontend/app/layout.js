import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
    title: 'Explorateur Articles Medium',
    description: 'Visualisez vos articles Medium',
}

export default function RootLayout({ children }) {
    return (
        <html lang="fr">
            <body className={inter.className}>{children}</body>
        </html>
    )
}
