#!/bin/bash
# Script de vérification de la configuration Antigravity

ENV_FILE="/Users/adminmac/medium-datligent/.env"

echo "╔════════════════════════════════════════════════════════╗"
echo "║   VÉRIFICATION CONFIGURATION ANTIGRAVITY               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Fichier .env non trouvé"
    echo "   Exécuter: /Users/adminmac/vault-datligent/scripts/setup-antigravity-env.sh"
    exit 1
fi

echo "📍 Fichier : $ENV_FILE"
echo ""

# Charger le .env
source "$ENV_FILE"

echo "📊 Vérification des variables :"
echo ""

# Gmail User
if [ "$GMAIL_USER" = "your-email@gmail.com" ] || [ -z "$GMAIL_USER" ]; then
    echo "  ❌ GMAIL_USER : Non configuré"
    echo "     Action: Éditer .env avec votre adresse Gmail"
else
    echo "  ✅ GMAIL_USER : $GMAIL_USER"
fi

# Gmail Password
if [[ "$GMAIL_PASS" =~ "xxxx" ]] || [ -z "$GMAIL_PASS" ]; then
    echo "  ❌ GMAIL_PASS : Non configuré"
    echo "     Action: Générer un App Password et le mettre dans .env"
    echo "     URL: https://myaccount.google.com/apppasswords"
else
    echo "  ✅ GMAIL_PASS : **************** (configuré)"
fi

# DeepL
if [ -z "$DEEPL_API_KEY" ] || [ "$DEEPL_API_KEY" = "YOUR_DEEPL_API_KEY_HERE" ]; then
    echo "  ❌ DEEPL_API_KEY : Non configuré"
else
    echo "  ✅ DEEPL_API_KEY : ${DEEPL_API_KEY:0:20}..."
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"

# Résumé
GMAIL_OK=false
DEEPL_OK=false

if [ "$GMAIL_USER" != "your-email@gmail.com" ] && [ -n "$GMAIL_USER" ] && [[ ! "$GMAIL_PASS" =~ "xxxx" ]] && [ -n "$GMAIL_PASS" ]; then
    GMAIL_OK=true
fi

if [ -n "$DEEPL_API_KEY" ] && [ "$DEEPL_API_KEY" != "YOUR_DEEPL_API_KEY_HERE" ]; then
    DEEPL_OK=true
fi

if $GMAIL_OK && $DEEPL_OK; then
    echo "║   ✅ CONFIGURATION COMPLÈTE                            ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "🚀 Antigravity est prêt à être utilisé !"
    echo ""
    echo "💡 Tester avec:"
    echo "   cd /Users/adminmac/medium-datligent/ingestion"
    echo "   python3 ingest_medium.py"
else
    echo "║   ⚠️  CONFIGURATION INCOMPLÈTE                         ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "📝 Actions requises:"
    echo ""
    if ! $GMAIL_OK; then
        echo "   1. Configurer Gmail:"
        echo "      nano /Users/adminmac/medium-datligent/.env"
        echo "      - Mettre votre adresse Gmail dans GMAIL_USER"
        echo "      - Générer un App Password: https://myaccount.google.com/apppasswords"
        echo "      - Mettre le App Password dans GMAIL_PASS"
        echo ""
    fi
    if ! $DEEPL_OK; then
        echo "   2. Configurer DeepL (optionnel):"
        echo "      - Obtenir une clé API: https://www.deepl.com/pro-api"
        echo "      - Mettre à jour .env avec la clé"
        echo ""
    fi
    echo "📚 Guide complet:"
    echo "   cat /Users/adminmac/medium-datligent/.env.README"
fi
echo ""
