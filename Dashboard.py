# dashboard_forex.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import random
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Top 40 Devises - Marché des Changes",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(45deg, #1E88E5, #039BE5, #00ACC1, #00897B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        padding: 1rem;
    }
    .currency-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .currency-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .currency-change {
        font-size: 1.2rem;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .positive { background-color: rgba(40, 167, 69, 0.2); color: #28a745; border: 2px solid #28a745; }
    .negative { background-color: rgba(220, 53, 69, 0.2); color: #dc3545; border: 2px solid #dc3545; }
    .neutral { background-color: rgba(108, 117, 125, 0.2); color: #6c757d; border: 2px solid #6c757d; }
    .section-header {
        color: #0055A4;
        border-bottom: 3px solid #FF6B00;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        font-size: 1.8rem;
    }
    .currency-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    .metric-highlight {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .volatility-indicator {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-weight: bold;
    }
    .low-vol { background-color: #d4edda; color: #155724; }
    .medium-vol { background-color: #fff3cd; color: #856404; }
    .high-vol { background-color: #f8d7da; color: #721c24; }
    .category-major { background: linear-gradient(135deg, #1E88E5, #039BE5); }
    .category-minor { background: linear-gradient(135deg, #43A047, #66BB6A); }
    .category-exotic { background: linear-gradient(135deg, #FB8C00, #FFA726); }
    .category-crypto { background: linear-gradient(135deg, #8E24AA, #AB47BC); }
    .simulator-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .profit-loss-positive {
        background-color: rgba(40, 167, 69, 0.2);
        color: #28a745;
        border: 2px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
    }
    .profit-loss-negative {
        background-color: rgba(220, 53, 69, 0.2);
        color: #dc3545;
        border: 2px solid #dc3545;
        padding: 1rem;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class ForexDashboard:
    def __init__(self):
        self.currencies = self.define_currencies()
        self.historical_data = self.initialize_historical_data()
        self.current_data = self.initialize_current_data()
        self.market_data = self.initialize_market_data()
        
    def define_currencies(self):
        """Définit les 40 principales paires de devises avec leurs caractéristiques"""
        return {
            # Paires Majeures (contre USD)
            'EUR/USD': {
                'nom': 'Euro / Dollar Américain',
                'symbole': 'EUR/USD',
                'icone': '🇪🇺🇺🇸',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 1.0850,
                'volatilite': 1.2,
                'volume_journalier': 750.0,  # milliards USD
                'pays': ['Zone Euro', 'États-Unis'],
                'banque_centrale': ['BCE', 'Fed'],
                'description': 'La paire de devises la plus échangée au monde'
            },
            'GBP/USD': {
                'nom': 'Livre Sterling / Dollar Américain',
                'symbole': 'GBP/USD',
                'icone': '🇬🇧🇺🇸',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 1.2750,
                'volatilite': 1.5,
                'volume_journalier': 350.0,
                'pays': ['Royaume-Uni', 'États-Unis'],
                'banque_centrale': ['BoE', 'Fed'],
                'description': 'Aussi connue sous le nom de "Cable"'
            },
            'USD/JPY': {
                'nom': 'Dollar Américain / Yen Japonais',
                'symbole': 'USD/JPY',
                'icone': '🇺🇸🇯🇵',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 155.50,
                'volatilite': 1.3,
                'volume_journalier': 550.0,
                'pays': ['États-Unis', 'Japon'],
                'banque_centrale': ['Fed', 'BoJ'],
                'description': 'La troisième paire la plus échangée'
            },
            'USD/CHF': {
                'nom': 'Dollar Américain / Franc Suisse',
                'symbole': 'USD/CHF',
                'icone': '🇺🇸🇨🇭',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 0.9050,
                'volatilite': 1.4,
                'volume_journalier': 250.0,
                'pays': ['États-Unis', 'Suisse'],
                'banque_centrale': ['Fed', 'SNB'],
                'description': 'Considérée comme une valeur refuge'
            },
            'AUD/USD': {
                'nom': 'Dollar Australien / Dollar Américain',
                'symbole': 'AUD/USD',
                'icone': '🇦🇺🇺🇸',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 0.6650,
                'volatilite': 1.6,
                'volume_journalier': 200.0,
                'pays': ['Australie', 'États-Unis'],
                'banque_centrale': ['RBA', 'Fed'],
                'description': 'Influencée par les prix des matières premières'
            },
            'USD/CAD': {
                'nom': 'Dollar Américain / Dollar Canadien',
                'symbole': 'USD/CAD',
                'icone': '🇺🇸🇨🇦',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 1.3650,
                'volatilite': 1.4,
                'volume_journalier': 180.0,
                'pays': ['États-Unis', 'Canada'],
                'banque_centrale': ['Fed', 'BoC'],
                'description': 'Influencée par les prix du pétrole'
            },
            'NZD/USD': {
                'nom': 'Dollar Néo-Zélandais / Dollar Américain',
                'symbole': 'NZD/USD',
                'icone': '🇳🇿🇺🇸',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 0.6150,
                'volatilite': 1.7,
                'volume_journalier': 80.0,
                'pays': ['Nouvelle-Zélande', 'États-Unis'],
                'banque_centrale': ['RBNZ', 'Fed'],
                'description': 'Souvent appelée "Kiwi"'
            },
            
            # Paires Croisées Majeures
            'EUR/GBP': {
                'nom': 'Euro / Livre Sterling',
                'symbole': 'EUR/GBP',
                'icone': '🇪🇺🇬🇧',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 0.8520,
                'volatilite': 1.3,
                'volume_journalier': 100.0,
                'pays': ['Zone Euro', 'Royaume-Uni'],
                'banque_centrale': ['BCE', 'BoE'],
                'description': 'Paire croisée importante'
            },
            'EUR/JPY': {
                'nom': 'Euro / Yen Japonais',
                'symbole': 'EUR/JPY',
                'icone': '🇪🇺🇯🇵',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 168.50,
                'volatilite': 1.5,
                'volume_journalier': 120.0,
                'pays': ['Zone Euro', 'Japon'],
                'banque_centrale': ['BCE', 'BoJ'],
                'description': 'Très liquide'
            },
            'GBP/JPY': {
                'nom': 'Livre Sterling / Yen Japonais',
                'symbole': 'GBP/JPY',
                'icone': '🇬🇧🇯🇵',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 197.50,
                'volatilite': 1.8,
                'volume_journalier': 90.0,
                'pays': ['Royaume-Uni', 'Japon'],
                'banque_centrale': ['BoE', 'BoJ'],
                'description': 'Connue pour sa volatilité'
            },
            'EUR/CHF': {
                'nom': 'Euro / Franc Suisse',
                'symbole': 'EUR/CHF',
                'icone': '🇪🇺🇨🇭',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 0.9820,
                'volatilite': 1.2,
                'volume_journalier': 60.0,
                'pays': ['Zone Euro', 'Suisse'],
                'banque_centrale': ['BCE', 'SNB'],
                'description': 'Considérée comme stable'
            },
            'EUR/AUD': {
                'nom': 'Euro / Dollar Australien',
                'symbole': 'EUR/AUD',
                'icone': '🇪🇺🇦🇺',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 1.6320,
                'volatilite': 1.6,
                'volume_journalier': 50.0,
                'pays': ['Zone Euro', 'Australie'],
                'banque_centrale': ['BCE', 'RBA'],
                'description': 'Influencée par les matières premières'
            },
            'EUR/CAD': {
                'nom': 'Euro / Dollar Canadien',
                'symbole': 'EUR/CAD',
                'icone': '🇪🇺🇨🇦',
                'categorie': 'Majeures',
                'unite': 'taux de change',
                'prix_base': 1.4820,
                'volatilite': 1.5,
                'volume_journalier': 45.0,
                'pays': ['Zone Euro', 'Canada'],
                'banque_centrale': ['BCE', 'BoC'],
                'description': 'Paire croisée importante'
            },
            
            # Paires Mineures
            'USD/SEK': {
                'nom': 'Dollar Américain / Couronne Suédoise',
                'symbole': 'USD/SEK',
                'icone': '🇺🇸🇸🇪',
                'categorie': 'Mineures',
                'unite': 'taux de change',
                'prix_base': 10.7500,
                'volatilite': 1.8,
                'volume_journalier': 40.0,
                'pays': ['États-Unis', 'Suède'],
                'banque_centrale': ['Fed', 'Riksbank'],
                'description': 'Paire nordique'
            },
            'USD/NOK': {
                'nom': 'Dollar Américain / Couronne Norvégienne',
                'symbole': 'USD/NOK',
                'icone': '🇺🇸🇳🇴',
                'categorie': 'Mineures',
                'unite': 'taux de change',
                'prix_base': 10.5500,
                'volatilite': 1.9,
                'volume_journalier': 35.0,
                'pays': ['États-Unis', 'Norvège'],
                'banque_centrale': ['Fed', 'Norges Bank'],
                'description': 'Influencée par les prix du pétrole'
            },
            'USD/DKK': {
                'nom': 'Dollar Américain / Couronne Danoise',
                'symbole': 'USD/DKK',
                'icone': '🇺🇸🇩🇰',
                'categorie': 'Mineures',
                'unite': 'taux de change',
                'prix_base': 6.8800,
                'volatilite': 1.4,
                'volume_journalier': 30.0,
                'pays': ['États-Unis', 'Danemark'],
                'banque_centrale': ['Fed', 'Danmarks Nationalbank'],
                'description': 'Liée à l\'EUR via l\'ERM II'
            },
            'USD/PLN': {
                'nom': 'Dollar Américain / Zloty Polonais',
                'symbole': 'USD/PLN',
                'icone': '🇺🇸🇵🇱',
                'categorie': 'Mineures',
                'unite': 'taux de change',
                'prix_base': 3.9500,
                'volatilite': 2.0,
                'volume_journalier': 25.0,
                'pays': ['États-Unis', 'Pologne'],
                'banque_centrale': ['Fed', 'NBP'],
                'description': 'Paire d\'Europe de l\'Est'
            },
            'USD/CZK': {
                'nom': 'Dollar Américain / Couronne Tchèque',
                'symbole': 'USD/CZK',
                'icone': '🇺🇸🇨🇿',
                'categorie': 'Mineures',
                'unite': 'taux de change',
                'prix_base': 23.2500,
                'volatilite': 1.7,
                'volume_journalier': 20.0,
                'pays': ['États-Unis', 'République Tchèque'],
                'banque_centrale': ['Fed', 'ČNB'],
                'description': 'Paire d\'Europe centrale'
            },
            'USD/HUF': {
                'nom': 'Dollar Américain / Forint Hongrois',
                'symbole': 'USD/HUF',
                'icone': '🇺🇸🇭🇺',
                'categorie': 'Mineures',
                'unite': 'taux de change',
                'prix_base': 355.50,
                'volatilite': 2.1,
                'volume_journalier': 18.0,
                'pays': ['États-Unis', 'Hongrie'],
                'banque_centrale': ['Fed', 'MNB'],
                'description': 'Paire d\'Europe de l\'Est'
            },
            'USD/SGD': {
                'nom': 'Dollar Américain / Dollar de Singapour',
                'symbole': 'USD/SGD',
                'icone': '🇺🇸🇸🇬',
                'categorie': 'Mineures',
                'unite': 'taux de change',
                'prix_base': 1.3450,
                'volatilite': 1.3,
                'volume_journalier': 45.0,
                'pays': ['États-Unis', 'Singapour'],
                'banque_centrale': ['Fed', 'MAS'],
                'description': 'Paire asiatique importante'
            },
            'USD/HKD': {
                'nom': 'Dollar Américain / Dollar de Hong Kong',
                'symbole': 'USD/HKD',
                'icone': '🇺🇸🇭🇰',
                'categorie': 'Mineures',
                'unite': 'taux de change',
                'prix_base': 7.8250,
                'volatilite': 0.3,
                'volume_journalier': 60.0,
                'pays': ['États-Unis', 'Hong Kong'],
                'banque_centrale': ['Fed', 'HKMA'],
                'description': 'Paire à taux fixe'
            },
            'USD/ZAR': {
                'nom': 'Dollar Américain / Rand Sud-Africain',
                'symbole': 'USD/ZAR',
                'icone': '🇺🇸🇿🇦',
                'categorie': 'Mineures',
                'unite': 'taux de change',
                'prix_base': 18.8500,
                'volatilite': 2.5,
                'volume_journalier': 25.0,
                'pays': ['États-Unis', 'Afrique du Sud'],
                'banque_centrale': ['Fed', 'SARB'],
                'description': 'Paire de matières premières'
            },
            'USD/MXN': {
                'nom': 'Dollar Américain / Peso Mexicain',
                'symbole': 'USD/MXN',
                'icone': '🇺🇸🇲🇽',
                'categorie': 'Mineures',
                'unite': 'taux de change',
                'prix_base': 16.8500,
                'volatilite': 2.2,
                'volume_journalier': 30.0,
                'pays': ['États-Unis', 'Mexique'],
                'banque_centrale': ['Fed', 'Banxico'],
                'description': 'Paire d\'Amérique latine'
            },
            
            # Paires Exotiques
            'USD/TRY': {
                'nom': 'Dollar Américain / Livre Turque',
                'symbole': 'USD/TRY',
                'icone': '🇺🇸🇹🇷',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 32.2500,
                'volatilite': 3.5,
                'volume_journalier': 15.0,
                'pays': ['États-Unis', 'Turquie'],
                'banque_centrale': ['Fed', 'CBRT'],
                'description': 'Paire très volatile'
            },
            'USD/THB': {
                'nom': 'Dollar Américain / Baht Thaïlandais',
                'symbole': 'USD/THB',
                'icone': '🇺🇸🇹🇭',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 36.5500,
                'volatilite': 1.8,
                'volume_journalier': 12.0,
                'pays': ['États-Unis', 'Thaïlande'],
                'banque_centrale': ['Fed', 'BOT'],
                'description': 'Paire d\'Asie du Sud-Est'
            },
            'USD/IDR': {
                'nom': 'Dollar Américain / Rupiah Indonésien',
                'symbole': 'USD/IDR',
                'icone': '🇺🇸🇮🇩',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 15850.0,
                'volatilite': 2.0,
                'volume_journalier': 10.0,
                'pays': ['États-Unis', 'Indonésie'],
                'banque_centrale': ['Fed', 'BI'],
                'description': 'Paire d\'Asie du Sud-Est'
            },
            'USD/INR': {
                'nom': 'Dollar Américain / Roupie Indienne',
                'symbole': 'USD/INR',
                'icone': '🇺🇸🇮🇳',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 83.2500,
                'volatilite': 1.5,
                'volume_journalier': 20.0,
                'pays': ['États-Unis', 'Inde'],
                'banque_centrale': ['Fed', 'RBI'],
                'description': 'Paire asiatique importante'
            },
            'USD/CNY': {
                'nom': 'Dollar Américain / Yuan Chinois',
                'symbole': 'USD/CNY',
                'icone': '🇺🇸🇨🇳',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 7.2450,
                'volatilite': 1.4,
                'volume_journalier': 40.0,
                'pays': ['États-Unis', 'Chine'],
                'banque_centrale': ['Fed', 'PBoC'],
                'description': 'Paire gérée par la Chine'
            },
            'USD/KRW': {
                'nom': 'Dollar Américain / Won Sud-Coréen',
                'symbole': 'USD/KRW',
                'icone': '🇺🇸🇰🇷',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 1325.50,
                'volatilite': 1.6,
                'volume_journalier': 15.0,
                'pays': ['États-Unis', 'Corée du Sud'],
                'banque_centrale': ['Fed', 'BoK'],
                'description': 'Paire asiatique importante'
            },
            'USD/BRL': {
                'nom': 'Dollar Américain / Real Brésilien',
                'symbole': 'USD/BRL',
                'icone': '🇺🇸🇧🇷',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 5.2500,
                'volatilite': 2.8,
                'volume_journalier': 18.0,
                'pays': ['États-Unis', 'Brésil'],
                'banque_centrale': ['Fed', 'BCB'],
                'description': 'Paire d\'Amérique du Sud'
            },
            'USD/RUB': {
                'nom': 'Dollar Américain / Rouble Russe',
                'symbole': 'USD/RUB',
                'icone': '🇺🇸🇷🇺',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 91.2500,
                'volatilite': 3.2,
                'volume_journalier': 12.0,
                'pays': ['États-Unis', 'Russie'],
                'banque_centrale': ['Fed', 'CBR'],
                'description': 'Paire très volatile'
            },
            'USD/CLP': {
                'nom': 'Dollar Américain / Peso Chilien',
                'symbole': 'USD/CLP',
                'icone': '🇺🇸🇨🇱',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 925.50,
                'volatilite': 2.0,
                'volume_journalier': 8.0,
                'pays': ['États-Unis', 'Chili'],
                'banque_centrale': ['Fed', 'BCCh'],
                'description': 'Paire d\'Amérique du Sud'
            },
            'USD/COP': {
                'nom': 'Dollar Américain / Peso Colombien',
                'symbole': 'USD/COP',
                'icone': '🇺🇸🇨🇴',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 3850.50,
                'volatilite': 2.3,
                'volume_journalier': 6.0,
                'pays': ['États-Unis', 'Colombie'],
                'banque_centrale': ['Fed', 'Banco de la República'],
                'description': 'Paire d\'Amérique du Sud'
            },
            'USD/PHP': {
                'nom': 'Dollar Américain / Peso Philippin',
                'symbole': 'USD/PHP',
                'icone': '🇺🇸🇵🇭',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 56.8500,
                'volatilite': 1.7,
                'volume_journalier': 8.0,
                'pays': ['États-Unis', 'Philippines'],
                'banque_centrale': ['Fed', 'BSP'],
                'description': 'Paire d\'Asie du Sud-Est'
            },
            'USD/MYR': {
                'nom': 'Dollar Américain / Ringgit Malaisien',
                'symbole': 'USD/MYR',
                'icone': '🇺🇸🇲🇾',
                'categorie': 'Exotiques',
                'unite': 'taux de change',
                'prix_base': 4.6250,
                'volatilite': 1.5,
                'volume_journalier': 10.0,
                'pays': ['États-Unis', 'Malaisie'],
                'banque_centrale': ['Fed', 'BNM'],
                'description': 'Paire d\'Asie du Sud-Est'
            },
            
            # Cryptomonnaies
            'BTC/USD': {
                'nom': 'Bitcoin / Dollar Américain',
                'symbole': 'BTC/USD',
                'icone': '₿',
                'categorie': 'Cryptomonnaies',
                'unite': 'taux de change',
                'prix_base': 65250.0,
                'volatilite': 4.5,
                'volume_journalier': 30.0,
                'pays': ['Global', 'États-Unis'],
                'banque_centrale': ['Décentralisé', 'Fed'],
                'description': 'La cryptomonnaie la plus connue'
            },
            'ETH/USD': {
                'nom': 'Ethereum / Dollar Américain',
                'symbole': 'ETH/USD',
                'icone': 'Ξ',
                'categorie': 'Cryptomonnaies',
                'unite': 'taux de change',
                'prix_base': 3250.0,
                'volatilite': 5.0,
                'volume_journalier': 20.0,
                'pays': ['Global', 'États-Unis'],
                'banque_centrale': ['Décentralisé', 'Fed'],
                'description': 'Deuxième cryptomonnaie par capitalisation'
            }
        }
    
    def initialize_historical_data(self):
        """Initialise les données historiques des devises"""
        dates = pd.date_range('2020-01-01', datetime.now(), freq='D')
        data = []
        
        for date in dates:
            for symbole, info in self.currencies.items():
                # Prix de base
                base_price = info['prix_base']
                
                # Impact des événements mondiaux
                global_impact = 1.0
                
                # Crise COVID (2020)
                if date.year == 2020 and date.month <= 6:
                    if 'USD' in symbole and symbole != 'USD/JPY':
                        global_impact *= random.uniform(1.05, 1.15)  # USD renforcé
                    else:
                        global_impact *= random.uniform(0.9, 1.1)
                # Reprise post-COVID (2021)
                elif date.year == 2021:
                    if 'USD' in symbole and symbole != 'USD/JPY':
                        global_impact *= random.uniform(0.95, 1.05)  # USD affaibli
                    else:
                        global_impact *= random.uniform(1.05, 1.15)
                # Guerre Ukraine (2022)
                elif date.year == 2022 and date.month >= 2:
                    if symbole in ['EUR/USD', 'GBP/USD']:
                        global_impact *= random.uniform(0.9, 1.0)  # EUR/GBP affaiblis
                    elif symbole in ['USD/CHF', 'USD/JPY']:
                        global_impact *= random.uniform(1.0, 1.1)  # CHF/JPY renforcés
                # Tensions récentes
                elif date.year >= 2023:
                    global_impact *= random.uniform(0.98, 1.08)
                
                # Volatilité quotidienne basée sur le profil de volatilité
                daily_volatility = random.normalvariate(1, info['volatilite']/100)
                
                # Tendance saisonnière
                seasonal = 1 + 0.003 * np.sin(2 * np.pi * date.dayofyear / 365)
                
                prix_actuel = base_price * global_impact * daily_volatility * seasonal
                
                data.append({
                    'date': date,
                    'symbole': symbole,
                    'nom': info['nom'],
                    'categorie': info['categorie'],
                    'prix': prix_actuel,
                    'volume': random.uniform(100000, 5000000),
                    'volatilite_jour': abs(daily_volatility - 1) * 100
                })
        
        return pd.DataFrame(data)
    
    def initialize_current_data(self):
        """Initialise les données courantes"""
        current_data = []
        for symbole, info in self.currencies.items():
            # Dernières données historiques
            last_data = self.historical_data[self.historical_data['symbole'] == symbole].iloc[-1]
            
            # Variations simulées
            change_pct = random.uniform(-2.0, 2.0)
            
            current_data.append({
                'symbole': symbole,
                'nom': info['nom'],
                'icone': info['icone'],
                'categorie': info['categorie'],
                'unite': info['unite'],
                'prix': last_data['prix'] * (1 + change_pct/100),
                'change_pct': change_pct,
                'volatilite': info['volatilite'],
                'volume_journalier': info['volume_journalier'],
                'pays': info['pays'],
                'banque_centrale': info['banque_centrale'],
                'spread': random.uniform(0.1, 2.0)
            })
        
        return pd.DataFrame(current_data)
    
    def initialize_market_data(self):
        """Initialise les données des marchés mondiaux"""
        indices = {
            'Dollar Index (DXY)': {'valeur': 104.5, 'change': 0.0, 'secteur': 'USD'},
            'Euro Index': {'valeur': 95.2, 'change': 0.0, 'secteur': 'EUR'},
            'Pound Index': {'valeur': 92.8, 'change': 0.0, 'secteur': 'GBP'},
            'Yen Index': {'valeur': 88.5, 'change': 0.0, 'secteur': 'JPY'},
            'Franc Index': {'valeur': 96.3, 'change': 0.0, 'secteur': 'CHF'},
            'Aussie Index': {'valeur': 90.7, 'change': 0.0, 'secteur': 'AUD'},
            'Loonie Index': {'valeur': 91.2, 'change': 0.0, 'secteur': 'CAD'},
            'Kiwi Index': {'valeur': 89.8, 'change': 0.0, 'secteur': 'NZD'}
        }
        
        return {'indices': indices}
    
    def update_live_data(self):
        """Met à jour les données en temps réel"""
        for idx in self.current_data.index:
            symbole = self.current_data.loc[idx, 'symbole']
            
            # Mise à jour des prix
            if random.random() < 0.6:  # 60% de chance de changement
                variation = random.uniform(-1.0, 1.0)
                
                self.current_data.loc[idx, 'prix'] *= (1 + variation/100)
                self.current_data.loc[idx, 'change_pct'] = variation
                
                # Mise à jour du volume
                self.current_data.loc[idx, 'volume_journalier'] *= random.uniform(0.8, 1.2)
    
    def calculate_rsi(self, prices, period=14):
        """Calcule le RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calcule les bandes de Bollinger"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, lower_band
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        st.markdown(
            '<h1 class="main-header">💱 DASHBOARD TOP 40 DEVISES - MARCHÉ DES CHANGES</h1>', 
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                '<div style="text-align: center; background: linear-gradient(45deg, #1E88E5, #039BE5); '
                'color: white; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">'
                '<h3>🔴 SURVEILLANCE EN TEMPS RÉEL DES 40 PRINCIPALES PAIRES DE DEVISES</h3>'
                '</div>', 
                unsafe_allow_html=True
            )
        
        current_time = datetime.now().strftime('%H:%M:%S')
        st.sidebar.markdown(f"**🕐 Dernière mise à jour: {current_time}**")
    
    def display_currency_cards(self):
        """Affiche les cartes de devises principales"""
        st.markdown('<h3 class="section-header">💰 TAUX DE CHANGE EN TEMPS RÉEL</h3>', 
                   unsafe_allow_html=True)
        
        # Grouper par catégorie
        categories = self.current_data['categorie'].unique()
        
        for categorie in categories:
            st.markdown(f'<h4 style="color: #0055A4; margin-top: 1rem;">{categorie}</h4>', 
                       unsafe_allow_html=True)
            
            cat_data = self.current_data[self.current_data['categorie'] == categorie]
            
            # Afficher 4 devises par ligne
            for i in range(0, len(cat_data), 4):
                cols = st.columns(min(4, len(cat_data) - i))
                
                for j, (_, currency) in enumerate(cat_data.iloc[i:i+4].iterrows()):
                    with cols[j]:
                        change_class = "positive" if currency['change_pct'] > 0 else "negative" if currency['change_pct'] < 0 else "neutral"
                        card_class = f"currency-card category-{categorie.lower().replace(' ', '').replace('é', 'e')}"
                        
                        st.markdown(f"""
                        <div class="{card_class}">
                            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                <span class="currency-icon">{currency['icone']}</span>
                                <div>
                                    <h3 style="margin: 0; font-size: 1.2rem;">{currency['symbole']}</h3>
                                    <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">{currency['nom']}</p>
                                </div>
                            </div>
                            <div class="currency-value">{currency['prix']:.4f}</div>
                            <div style="font-size: 0.9rem; opacity: 0.8;">{currency['unite']}</div>
                            <div class="currency-change {change_class}">
                                {currency['change_pct']:+.2f}%
                            </div>
                            <div style="margin-top: 1rem; font-size: 0.8rem;">
                                📊 Vol: {currency['volume_journalier']:.1f}B<br>
                                📈 Volatilité: {currency['volatilite']:.1f}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    
    def display_key_metrics(self):
        """Affiche les métriques clés"""
        st.markdown('<h3 class="section-header">📊 INDICATEURS MARCHÉ</h3>', 
                   unsafe_allow_html=True)
        
        # Calcul des métriques globales
        avg_change = self.current_data['change_pct'].mean()
        total_volume = self.current_data['volume_journalier'].sum()
        strongest_currency = self.current_data.loc[self.current_data['change_pct'].idxmax()]
        weakest_currency = self.current_data.loc[self.current_data['change_pct'].idxmin()]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Performance Moyenne",
                f"{avg_change:+.2f}%",
                "Journalier",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Volume Total Journalier",
                f"${total_volume:,.1f}B",
                f"{random.randint(-8, 12)}% vs hier"
            )
        
        with col3:
            st.metric(
                "Plus Forte Hausse",
                f"{strongest_currency['symbole']}",
                f"{strongest_currency['change_pct']:+.2f}%"
            )
        
        with col4:
            st.metric(
                "Plus Forte Baisse",
                f"{weakest_currency['symbole']}",
                f"{weakest_currency['change_pct']:+.2f}%"
            )
    
    def create_price_overview(self):
        """Crée la vue d'ensemble des prix"""
        st.markdown('<h3 class="section-header">📈 ANALYSE DES TAUX HISTORIQUES</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "Évolution Historique", 
            "Analyse par Catégorie", 
            "Volatilité", 
            "Performances Relatives"
        ])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Sélection des devises à afficher
                selected_currencies = st.multiselect(
                    "Sélectionnez les paires de devises:",
                    list(self.currencies.keys()),
                    default=['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD']
                )
            
            with col2:
                # Période d'analyse
                period = st.selectbox(
                    "Période d'analyse:",
                    ['1 mois', '3 mois', '6 mois', '1 an', '2 ans', 'Toute la période'],
                    index=3
                )
            
            # Filtrage des données
            filtered_data = self.historical_data[
                self.historical_data['symbole'].isin(selected_currencies)
            ]
            
            if period != 'Toute la période':
                if 'mois' in period:
                    months = int(period.split()[0])
                    cutoff_date = datetime.now() - timedelta(days=30 * months)
                else:
                    years = int(period.split()[0])
                    cutoff_date = datetime.now() - timedelta(days=365 * years)
                filtered_data = filtered_data[filtered_data['date'] >= cutoff_date]
            
            fig = px.line(filtered_data, 
                         x='date', 
                         y='prix',
                         color='symbole',
                         title=f'Évolution des Taux de Change ({period})',
                         color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(yaxis_title="Taux de Change")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Analyse par catégorie
            fig = px.box(self.historical_data, 
                        x='categorie', 
                        y='prix',
                        title='Distribution des Taux par Catégorie',
                        color='categorie')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                # Volatilité historique
                volatilite_data = self.historical_data.groupby('symbole')['volatilite_jour'].mean().reset_index()
                fig = px.bar(volatilite_data, 
                            x='symbole', 
                            y='volatilite_jour',
                            title='Volatilité Historique Moyenne (%)',
                            color='symbole',
                            color_discrete_sequence=px.colors.qualitative.Bold)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Volatilité récente (30 derniers jours)
                recent_data = self.historical_data[
                    self.historical_data['date'] > (datetime.now() - timedelta(days=30))
                ]
                recent_vol = recent_data.groupby('symbole')['volatilite_jour'].std().reset_index()
                
                fig = px.scatter(recent_vol, 
                               x='symbole', 
                               y='volatilite_jour',
                               size='volatilite_jour',
                               title='Volatilité Récente (30 jours)',
                               color='symbole',
                               size_max=40)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            # Performance relative
            performance_data = []
            for symbole in self.currencies.keys():
                currency_data = self.historical_data[self.historical_data['symbole'] == symbole]
                if len(currency_data) > 0:
                    start_price = currency_data.iloc[0]['prix']
                    end_price = currency_data.iloc[-1]['prix']
                    performance = ((end_price - start_price) / start_price) * 100
                    performance_data.append({
                        'symbole': symbole,
                        'performance': performance,
                        'categorie': self.currencies[symbole]['categorie']
                    })
            
            performance_df = pd.DataFrame(performance_data)
            fig = px.bar(performance_df, 
                        x='symbole', 
                        y='performance',
                        color='categorie',
                        title='Performance Totale depuis 2020 (%)',
                        color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig, use_container_width=True)
    
    def create_central_bank_analysis(self):
        """Analyse des banques centrales"""
        st.markdown('<h3 class="section-header">🏦 ANALYSE DES BANQUES CENTRALES</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Politiques Monétaires", "Taux Directeurs", "Interventions"])
        
        with tab1:
            st.subheader("Politiques Monétaires des Principales Banques Centrales")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🇺🇸 Réserve Fédérale (Fed)
                
                **Position actuelle:** Hawkish pause
                **Taux directeur:** 5.25%-5.50%
                **Prochaine réunion:** Juin 2024
                **Perspective:** Maintien des taux élevés
                
                **Facteurs d'influence:**
                - Inflation à 3.2%
                - Chômage à 3.8%
                - Croissance PIB à 2.1%
                
                ### 🇪🇺 Banque Centrale Européenne (BCE)
                
                **Position actuelle:** Dovish pivot
                **Taux directeur:** 4.5%
                **Prochaine réunion:** Juin 2024
                **Perspective:** Baisse des taux attendue
                
                **Facteurs d'influence:**
                - Inflation à 2.4%
                - Chômage à 6.5%
                - Croissance PIB à 0.5%
                """)
            
            with col2:
                st.markdown("""
                ### 🇬🇧 Banque d'Angleterre (BoE)
                
                **Position actuelle:** Attentiste
                **Taux directeur:** 5.25%
                **Prochaine réunion:** Juin 2024
                **Perspective:** Maintien ou légère baisse
                
                **Facteurs d'influence:**
                - Inflation à 3.8%
                - Chômage à 4.2%
                - Croissance PIB à 0.3%
                
                ### 🇯🇵 Banque du Japon (BoJ)
                
                **Position actuelle:** Ultra-dovish
                **Taux directeur:** -0.1% à 0.1%
                **Prochaine réunion:** Juin 2024
                **Perspective:** Normalisation progressive
                
                **Facteurs d'influence:**
                - Inflation à 2.7%
                - Chômage à 2.6%
                - Croissance PIB à 1.9%
                """)
        
        with tab2:
            st.subheader("Comparaison des Taux Directeurs")
            
            # Données des taux directeurs
            central_banks = {
                'Fed': 5.375,
                'BCE': 4.5,
                'BoE': 5.25,
                'BoJ': 0.0,
                'SNB': 1.75,
                'RBA': 4.1,
                'BoC': 5.0,
                'RBNZ': 5.5,
                'Riksbank': 4.0,
                'Norges Bank': 4.5,
                'Danmarks Nationalbank': 3.75,
                'NBP': 5.75,
                'ČNB': 5.25,
                'MNB': 7.75,
                'MAS': 3.5,
                'HKMA': 5.75,
                'SARB': 8.25,
                'Banxico': 11.25,
                'CBRT': 50.0,
                'BOT': 2.5,
                'BI': 6.0,
                'RBI': 6.5,
                'PBoC': 3.45,
                'BoK': 3.5,
                'BCB': 10.75,
                'CBR': 16.0,
                'BCCh': 10.25,
                'Banco de la República': 13.25,
                'BSP': 6.5,
                'BNM': 3.0
            }
            
            # Création du graphique
            banks_df = pd.DataFrame(list(central_banks.items()), columns=['Banque Centrale', 'Taux Directeur'])
            banks_df = banks_df.sort_values('Taux Directeur', ascending=False)
            
            fig = px.bar(banks_df, 
                        x='Banque Centrale', 
                        y='Taux Directeur',
                        title='Taux Directeurs des Banques Centrales (%)',
                        color='Taux Directeur',
                        color_continuous_scale='RdYlGn_r')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Interventions Récentes sur le Marché des Changes")
            
            st.markdown("""
            ### 📊 Interventions Planifiées
            
            **🇯🇵 Banque du Japon:**
            - Surveillance accrue du Yen faible
            - Possibilité d'intervention si USD/JPY > 160
            - Coordination avec le Trésor américain
            
            **🇨🇭 Banque Nationale Suisse:**
            - Interventions occasionnelles contre le Franc fort
            - Maintien du plancher implicite à 1.05 CHF/EUR
            
            **🇨🇳 Banque Populaire de Chine:**
            - Fixation quotidienne du taux de référence du Yuan
            - Interventions via les banques d'État
            
            ### 📈 Impact des Interventions
            
            **Intervention BOJ (Mars 2024):**
            - Achat de Yen pour 5 milliards USD
            - Impact: USD/JPY -1.2% en 24h
            - Effet durable: 3-4 jours
            
            **Intervention SNB (Janvier 2024):**
            - Vente de Francs pour 3 milliards CHF
            - Impact: EUR/CHF +0.8% en 24h
            - Effet durable: 2-3 jours
            """)
    
    def create_technical_analysis(self):
        """Analyse technique avancée"""
        st.markdown('<h3 class="section-header">🔬 ANALYSE TECHNIQUE AVANCÉE</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Indicateurs Techniques", "Patterns de Trading", "Signaux"])
        
        with tab1:
            devise_selectionnee = st.selectbox("Sélectionnez une paire de devises:", 
                                             list(self.currencies.keys()))
            
            if devise_selectionnee:
                devise_data = self.historical_data[
                    self.historical_data['symbole'] == devise_selectionnee
                ].copy()
                
                # Calcul des indicateurs techniques
                devise_data['MA20'] = devise_data['prix'].rolling(window=20).mean()
                devise_data['MA50'] = devise_data['prix'].rolling(window=50).mean()
                devise_data['RSI'] = self.calculate_rsi(devise_data['prix'])
                devise_data['Bollinger_High'], devise_data['Bollinger_Low'] = self.calculate_bollinger_bands(devise_data['prix'])
                
                fig = make_subplots(rows=3, cols=1, 
                                  shared_xaxes=True, 
                                  vertical_spacing=0.05,
                                  subplot_titles=('Prix et Moyennes Mobiles', 'Bandes de Bollinger', 'RSI'),
                                  row_heights=[0.5, 0.25, 0.25])
                
                # Prix et moyennes mobiles
                fig.add_trace(go.Scatter(x=devise_data['date'], y=devise_data['prix'],
                                       name='Prix', line=dict(color='#0055A4')), row=1, col=1)
                fig.add_trace(go.Scatter(x=devise_data['date'], y=devise_data['MA20'],
                                       name='MM20', line=dict(color='orange')), row=1, col=1)
                fig.add_trace(go.Scatter(x=devise_data['date'], y=devise_data['MA50'],
                                       name='MM50', line=dict(color='red')), row=1, col=1)
                
                # Bandes de Bollinger
                fig.add_trace(go.Scatter(x=devise_data['date'], y=devise_data['Bollinger_High'],
                                       name='Bollinger High', line=dict(color='gray', dash='dash')), row=2, col=1)
                fig.add_trace(go.Scatter(x=devise_data['date'], y=devise_data['prix'],
                                       name='Prix', line=dict(color='#0055A4'), showlegend=False), row=2, col=1)
                fig.add_trace(go.Scatter(x=devise_data['date'], y=devise_data['Bollinger_Low'],
                                       name='Bollinger Low', line=dict(color='gray', dash='dash'), 
                                       fill='tonexty'), row=2, col=1)
                
                # RSI
                fig.add_trace(go.Scatter(x=devise_data['date'], y=devise_data['RSI'],
                                       name='RSI', line=dict(color='purple')), row=3, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
                
                fig.update_layout(height=800, title_text=f"Analyse Technique - {devise_selectionnee}")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Patterns de Trading Courants")
            
            patterns_data = {
                'Pattern': ['Head & Shoulders', 'Double Top/Bottom', 'Triangle', 'Flag/Pennant', 'Wedge'],
                'Fréquence': [15, 20, 25, 18, 12],
                'Fiabilité': [75, 80, 65, 70, 60],
                'Type': ['Renversement', 'Renversement', 'Continuation', 'Continuation', 'Renversement']
            }
            
            patterns_df = pd.DataFrame(patterns_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(patterns_df, 
                           x='Pattern', 
                           y='Fréquence',
                           title='Fréquence des Patterns (%)',
                           color='Type')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(patterns_df, 
                               x='Pattern', 
                               y='Fiabilité',
                               size='Fréquence',
                               title='Fiabilité des Patterns (%)',
                               color='Type',
                               size_max=40)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Signaux de Trading Actuels")
            
            # Simulation de signaux
            signals = []
            for symbole in self.currencies.keys():
                signal_type = random.choice(['ACHAT', 'VENTE', 'NEUTRE'])
                strength = random.randint(1, 10)
                reason = random.choice([
                    'Surachat RSI', 'Survente RSI', 'Croissance MM20/50', 
                    'Bande Bollinger', 'Support/Résistance', 'Volume élevé'
                ])
                
                signals.append({
                    'Symbole': symbole,
                    'Signal': signal_type,
                    'Force': strength,
                    'Raison': reason
                })
            
            signals_df = pd.DataFrame(signals)
            
            # Filtrer les signaux forts
            strong_signals = signals_df[signals_df['Force'] >= 7].sort_values('Force', ascending=False)
            
            if not strong_signals.empty:
                st.write("### 🚨 Signaux Forts (Force ≥ 7)")
                for _, signal in strong_signals.iterrows():
                    signal_class = "profit-loss-positive" if signal['Signal'] == 'ACHAT' else "profit-loss-negative"
                    st.markdown(f"""
                    <div class="{signal_class}">
                        <strong>{signal['Symbole']}</strong> - {signal['Signal']} (Force: {signal['Force']}/10)<br>
                        Raison: {signal['Raison']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun signal fort détecté actuellement.")
            
            # Tableau complet des signaux
            st.write("### 📋 Tous les Signaux")
            st.dataframe(signals_df, use_container_width=True)
    
    def create_trading_simulator(self):
        """Simulateur de trading"""
        st.markdown('<h3 class="section-header">🎮 SIMULATEUR DE TRADING</h3>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Ouvrir une Position")
            
            # Sélection de la paire
            pair = st.selectbox("Paire de devises:", list(self.currencies.keys()))
            
            # Type de position
            position_type = st.radio("Type de position:", ['ACHAT (Long)', 'VENTE (Short)'])
            
            # Paramètres de la position
            col_amount, col_leverage = st.columns(2)
            with col_amount:
                amount = st.number_input("Montant ($):", min_value=100, max_value=100000, value=1000, step=100)
            with col_leverage:
                leverage = st.selectbox("Effet de levier:", [1, 5, 10, 20, 50, 100], index=2)
            
            # Stop Loss et Take Profit
            col_sl, col_tp = st.columns(2)
            with col_sl:
                stop_loss = st.number_input("Stop Loss (%):", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
            with col_tp:
                take_profit = st.number_input("Take Profit (%):", min_value=0.1, max_value=20.0, value=5.0, step=0.1)
            
            # Bouton pour ouvrir la position
            if st.button("Ouvrir Position", type="primary"):
                current_price = self.current_data[self.current_data['symbole'] == pair]['prix'].iloc[0]
                
                # Simulation du résultat
                price_change = random.uniform(-take_profit, take_profit)
                final_price = current_price * (1 + price_change/100)
                
                if position_type == 'ACHAT (Long)':
                    pnl_pct = price_change
                else:
                    pnl_pct = -price_change
                
                pnl_amount = amount * pnl_pct/100 * leverage
                
                # Affichage du résultat
                st.markdown('<div class="simulator-card">', unsafe_allow_html=True)
                st.write(f"**Position ouverte:** {position_type} {pair}")
                st.write(f"**Prix d'entrée:** ${current_price:.4f}")
                st.write(f"**Prix de sortie:** ${final_price:.4f}")
                st.write(f"**Variation:** {price_change:+.2f}%")
                st.write(f"**P&L:** ${pnl_amount:+.2f}")
                
                if pnl_amount > 0:
                    st.markdown(f'<div class="profit-loss-positive">PROFIT: ${pnl_amount:+.2f}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="profit-loss-negative">PERTE: ${pnl_amount:+.2f}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader("Historique des Trades")
            
            # Simulation d'historique
            trade_history = []
            for i in range(10):
                pair = random.choice(list(self.currencies.keys()))
                position_type = random.choice(['ACHAT', 'VENTE'])
                pnl = random.uniform(-500, 1000)
                
                trade_history.append({
                    'Paire': pair,
                    'Type': position_type,
                    'P&L': f"${pnl:+.2f}",
                    'Résultat': 'Profit' if pnl > 0 else 'Perte'
                })
            
            history_df = pd.DataFrame(trade_history)
            st.dataframe(history_df, use_container_width=True)
            
            # Statistiques
            total_trades = len(trade_history)
            winning_trades = len([t for t in trade_history if t['Résultat'] == 'Profit'])
            win_rate = (winning_trades / total_trades) * 100
            
            st.metric("Total Trades", total_trades)
            st.metric("Taux de réussite", f"{win_rate:.1f}%")
    
    def create_market_sentiment(self):
        """Analyse du sentiment du marché"""
        st.markdown('<h3 class="section-header">💭 SENTIMENT DU MARCHÉ</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Sentiment Global", "Fear & Greed Index", "Actualités"])
        
        with tab1:
            # Sentiment par devise
            sentiment_data = []
            for symbole in self.currencies.keys():
                sentiment_score = random.uniform(-1, 1)
                if sentiment_score > 0.3:
                    sentiment = 'HAUSSIER'
                elif sentiment_score < -0.3:
                    sentiment = 'BAISSIER'
                else:
                    sentiment = 'NEUTRE'
                
                sentiment_data.append({
                    'Symbole': symbole,
                    'Sentiment': sentiment,
                    'Score': sentiment_score
                })
            
            sentiment_df = pd.DataFrame(sentiment_data)
            
            # Graphique du sentiment
            fig = px.bar(sentiment_df.head(20), 
                        x='Symbole', 
                        y='Score',
                        color='Score',
                        title='Sentiment du Marché par Paire de Devises',
                        color_continuous_scale='RdYlGn')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Répartition des sentiments
            sentiment_counts = sentiment_df['Sentiment'].value_counts()
            fig = px.pie(values=sentiment_counts.values, 
                        names=sentiment_counts.index,
                        title='Répartition des Sentiments')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Fear & Greed Index")
            
            # Simulation de l'index
            fear_greed_value = random.randint(0, 100)
            
            if fear_greed_value < 25:
                sentiment = "PEUR EXTREME"
                color = "red"
                advice = "Opportunité d'achat potentielle"
            elif fear_greed_value < 45:
                sentiment = "PEUR"
                color = "orange"
                advice = "Marché prudent"
            elif fear_greed_value < 55:
                sentiment = "NEUTRE"
                color = "gray"
                advice = "Marché équilibré"
            elif fear_greed_value < 75:
                sentiment = "CUPIDITÉ"
                color = "lightgreen"
                advice = "Surveillance requise"
            else:
                sentiment = "CUPIDITÉ EXTREME"
                color = "green"
                advice = "Risque de correction élevé"
            
            # Affichage de l'index
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <h2>Fear & Greed Index</h2>
                <div style="font-size: 4rem; font-weight: bold; color: {color};">
                    {fear_greed_value}
                </div>
                <h3 style="color: {color};">{sentiment}</h3>
                <p><strong>Conseil:</strong> {advice}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Historique de l'index
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            values = [random.randint(0, 100) for _ in range(30)]
            
            fig = px.line(x=dates, y=values, title='Évolution du Fear & Greed Index (30 jours)')
            fig.add_hline(y=50, line_dash="dash", line_color="gray", annotation_text="Neutre")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Actualités du Marché")
            
            # Simulation d'actualités
            news = [
                {
                    'Titre': 'Fed maintient les taux intouchables, signal hawkish',
                    'Heure': 'Il y a 2 heures',
                    'Impact': 'Élevé',
                    'Source': 'Reuters'
                },
                {
                    'Titre': 'L\'Euro rebondit suite aux commentaires de la BCE',
                    'Heure': 'Il y a 4 heures',
                    'Impact': 'Moyen',
                    'Source': 'Bloomberg'
                },
                {
                    'Titre': 'Le Yen japonais atteint son plus bas niveau',
                    'Heure': 'Il y a 6 heures',
                    'Impact': 'Élevé',
                    'Source': 'Financial Times'
                },
                {
                    'Titre': 'La Banque d\'Angleterre adopte une posture attentiste',
                    'Heure': 'Il y a 8 heures',
                    'Impact': 'Moyen',
                    'Source': 'CNBC'
                },
                {
                    'Titre': 'Les devises émergentes sous pression',
                    'Heure': 'Il y a 12 heures',
                    'Impact': 'Faible',
                    'Source': 'WSJ'
                }
            ]
            
            for article in news:
                impact_color = {
                    'Élevé': 'red',
                    'Moyen': 'orange',
                    'Faible': 'green'
                }
                
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 1rem; margin: 0.5rem 0; border-radius: 5px;">
                    <h4>{article['Titre']}</h4>
                    <p style="color: gray; font-size: 0.9rem;">
                        {article['Source']} • {article['Heure']} • 
                        <span style="color: {impact_color[article['Impact']]}; font-weight: bold;">
                            Impact {article['Impact']}
                        </span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    def display_correlation_matrix(self):
        """Affiche la matrice de corrélation"""
        st.markdown('<h3 class="section-header">🔗 MATRICE DE CORRÉLATION</h3>', 
                   unsafe_allow_html=True)
        
        # Préparation des données pour la corrélation
        pivot_data = self.historical_data.pivot(index='date', columns='symbole', values='prix')
        
        # Calcul de la corrélation sur les rendements
        returns_data = pivot_data.pct_change().dropna()
        correlation_matrix = returns_data.corr()
        
        # Sélection des paires principales pour la visualisation
        major_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD']
        available_pairs = [pair for pair in major_pairs if pair in correlation_matrix.columns]
        
        if available_pairs:
            selected_correlation = correlation_matrix[available_pairs].loc[available_pairs]
            
            # Création de la heatmap
            fig = px.imshow(selected_correlation,
                           text_auto=True,
                           aspect="auto",
                           title="Matrice de Corrélation des Paires Majeures",
                           color_continuous_scale='RdBu_r',
                           range_color=[-1, 1])
            st.plotly_chart(fig, use_container_width=True)
        
        # Analyse des corrélations fortes
        st.subheader("Analyse des Corrélations Fortes")
        
        # Trouver les corrélations les plus fortes
        corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                pair1 = correlation_matrix.columns[i]
                pair2 = correlation_matrix.columns[j]
                corr_value = correlation_matrix.iloc[i, j]
                
                if abs(corr_value) > 0.7:  # Corrélation forte
                    corr_pairs.append({
                        'Paire 1': pair1,
                        'Paire 2': pair2,
                        'Corrélation': corr_value
                    })
        
        if corr_pairs:
            corr_df = pd.DataFrame(corr_pairs).sort_values('Corrélation', key=abs, ascending=False)
            st.dataframe(corr_df.head(10), use_container_width=True)
        else:
            st.info("Aucune corrélation forte (> 0.7) détectée actuellement.")
    
    def run(self):
        """Fonction principale pour exécuter le dashboard"""
        # Affichage de l'en-tête
        self.display_header()
        
        # Menu de navigation dans la sidebar
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            "Choisissez une section:",
            [
                "📊 Vue d'ensemble",
                "💰 Taux de change",
                "📈 Analyse historique",
                "🏦 Banques centrales",
                "🔬 Analyse technique",
                "🎮 Simulateur de trading",
                "💭 Sentiment du marché",
                "🔗 Corrélations"
            ]
        )
        
        # Options de rafraîchissement
        st.sidebar.subheader("Options de rafraîchissement")
        auto_refresh = st.sidebar.checkbox("Rafraîchissement automatique", value=True)
        
        if auto_refresh:
            refresh_interval = st.sidebar.slider("Intervalle (secondes):", 5, 60, 10)
        
        # Affichage de la page sélectionnée
        if page == "📊 Vue d'ensemble":
            self.display_key_metrics()
            self.display_currency_cards()
            
        elif page == "💰 Taux de change":
            self.display_currency_cards()
            
        elif page == "📈 Analyse historique":
            self.create_price_overview()
            
        elif page == "🏦 Banques centrales":
            self.create_central_bank_analysis()
            
        elif page == "🔬 Analyse technique":
            self.create_technical_analysis()
            
        elif page == "🎮 Simulateur de trading":
            self.create_trading_simulator()
            
        elif page == "💭 Sentiment du marché":
            self.create_market_sentiment()
            
        elif page == "🔗 Corrélations":
            self.display_correlation_matrix()
        
        # Rafraîchissement automatique
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun() # <--- LIGNE CORRIGÉE

# Point d'entrée principal
if __name__ == "__main__":
    dashboard = ForexDashboard()
    dashboard.run()
