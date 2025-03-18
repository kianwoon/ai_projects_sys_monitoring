# Service configurations
SERVICES = {
    'BTSS': {
        'display_name': 'BTSS (Cyber Channel)',
        'patterns': [
            r'BTSS.*(?:Cyber.*Channel|Channel.*Cyber)',
            r'BTSS'
        ]
    },
    'CHSS_EJB': {
        'display_name': 'CHSS_EJB (EBanking)',
        'patterns': [
            r'CHSS.*EJB.*(?:Bank|EBanking)',
            r'CHSS.*EJB'
        ]
    },
    'CHSS_Internet': {
        'display_name': 'CHSS_Internet (EBanking)',
        'patterns': [
            r'CHSS.*(?:Internet|Intranet).*(?:Bank|EBanking)',
            r'CHSS.*Internet'
        ]
    },
    'ECIS': {
        'display_name': 'ECIS (Loans)',
        'patterns': [
            r'ECIS.*(?:Loans?|Loan)',
            r'ECIS'
        ]
    },
    'IVSS': {
        'display_name': 'IVSS_ejb (WMS)',
        'patterns': [
            r'IVSS.*(?:ejb|EJB).*(?:WMS|WM)',
            r'IVSS.*(?:ejb|EJB)'
        ]
    },
    'IWPG': {
        'display_name': 'IWPG_Internet (EBanking)',
        'patterns': [
            r'IWPG.*Internet.*(?:Bank|EBanking)',
            r'IWPG.*Internet'
        ]
    }
}
