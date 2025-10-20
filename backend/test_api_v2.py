"""
Script de test pour l'API V2
Teste l'authentification, l'analyse, et les profils utilisateurs
"""
import requests
import json
from pprint import pprint

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "email": "demo@yogacoach.com",
    "username": "demo_user",
    "password": "Demo1234",
    "skill_level": "intermediate"
}

# Landmarks d'exemple (pose de planche)
EXAMPLE_LANDMARKS = [
    {"x": 0.5, "y": 0.3, "z": 0.0, "visibility": 0.9} for _ in range(33)
]

class Colors:
    """Couleurs pour l'affichage dans le terminal"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_section(title):
    """Affiche un titre de section"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(message):
    """Affiche un message de succès"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    """Affiche une information"""
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")

def test_health():
    """Test du health check"""
    print_section("1. TEST HEALTH CHECK")

    response = requests.get(f"{BASE_URL}/health")

    if response.status_code == 200:
        print_success("Health check réussi")
        pprint(response.json())
        return True
    else:
        print_error("Health check échoué")
        return False

def test_register():
    """Test de l'inscription"""
    print_section("2. TEST INSCRIPTION")

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=TEST_USER
    )

    if response.status_code in [200, 201]:
        print_success("Inscription réussie")
        pprint(response.json())
        return True
    elif response.status_code == 400 and "déjà utilisé" in response.json().get('error', ''):
        print_info("Utilisateur existe déjà (normal si test déjà exécuté)")
        return True
    else:
        print_error(f"Inscription échouée: {response.json()}")
        return False

def test_login():
    """Test de la connexion"""
    print_section("3. TEST CONNEXION")

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Connexion réussie")
        token = data['tokens']['access_token']
        print_info(f"Token: {token[:50]}...")
        return token
    else:
        print_error(f"Connexion échouée: {response.json()}")
        return None

def test_analyze_complete(token):
    """Test de l'analyse complète"""
    print_section("4. TEST ANALYSE COMPLÈTE")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{BASE_URL}/analyze-complete",
        headers=headers,
        json={
            "landmarks": EXAMPLE_LANDMARKS,
            "save_session": True
        }
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Analyse complète réussie")

        if data.get('quality_analysis'):
            qa = data['quality_analysis']
            print(f"\n📊 Score Global: {qa.get('global_score', 'N/A')}/100")
            print(f"🎯 Niveau: {qa.get('skill_level', 'N/A')}")

            priority = qa.get('priority_indicator', {})
            print(f"\n⚠️  Indicateur Prioritaire: {priority.get('name', 'N/A')}")
            print(f"   Score: {priority.get('score', 'N/A')}")
            print(f"   Amélioration: {priority.get('improvement_needed', 'N/A')}")

            exercise = qa.get('recommended_exercise')
            if exercise:
                print(f"\n💪 Exercice Recommandé: {exercise.get('title', 'N/A')}")
                print(f"   Durée: {exercise.get('duration', 'N/A')}")
                print(f"   Motivation: {exercise.get('motivation', 'N/A')}")

        return True
    else:
        print_error(f"Analyse échouée: {response.json()}")
        return False

def test_profile(token):
    """Test de récupération du profil"""
    print_section("5. TEST PROFIL UTILISATEUR")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{BASE_URL}/profile",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Profil récupéré avec succès")

        profile = data.get('profile')
        if profile:
            print(f"\n📈 Sessions Totales: {profile.get('total_sessions', 0)}")
            print(f"⭐ Score Moyen: {profile.get('average_global_score', 0):.1f}/100")
            print(f"🏆 Meilleure Pose: {profile.get('best_pose', 'N/A')} ({profile.get('best_pose_score', 0):.1f})")
            print(f"📉 Pose à Améliorer: {profile.get('worst_pose', 'N/A')} ({profile.get('worst_pose_score', 0):.1f})")

        return True
    else:
        print_error(f"Récupération du profil échouée: {response.json()}")
        return False

def test_history(token):
    """Test de l'historique"""
    print_section("6. TEST HISTORIQUE DES SESSIONS")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{BASE_URL}/profile/history?limit=5",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Historique récupéré avec succès")

        sessions = data.get('sessions', [])
        print(f"\n📋 Nombre de sessions: {len(sessions)}")

        for i, session in enumerate(sessions[:3], 1):
            print(f"\nSession {i}:")
            print(f"  Pose: {session.get('pose_name')}")
            print(f"  Score: {session.get('global_score')}/100")
            print(f"  Date: {session.get('created_at')}")

        return True
    else:
        print_error(f"Récupération de l'historique échouée: {response.json()}")
        return False

def test_statistics(token):
    """Test des statistiques"""
    print_section("7. TEST STATISTIQUES")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{BASE_URL}/profile/statistics?days=30",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_success("Statistiques récupérées avec succès")

        stats = data.get('statistics', {})
        print(f"\n📊 Période: {stats.get('period_days', 0)} jours")
        print(f"🎯 Sessions: {stats.get('total_sessions', 0)}")
        print(f"⭐ Score Moyen: {stats.get('average_score', 0):.1f}/100")
        print(f"📈 Tendance: {stats.get('improvement_trend', 'N/A')}")

        poses = stats.get('poses_practiced', {})
        if poses:
            print(f"\n🧘 Poses Pratiquées:")
            for pose, count in poses.items():
                print(f"  • {pose}: {count} fois")

        return True
    else:
        print_error(f"Récupération des statistiques échouée: {response.json()}")
        return False

def run_all_tests():
    """Exécute tous les tests"""
    print(f"\n{Colors.BOLD}🧪 DÉMARRAGE DES TESTS DE L'API V2{Colors.END}")
    print(f"{Colors.BOLD}URL: {BASE_URL}{Colors.END}\n")

    results = []

    # Test 1: Health Check
    results.append(("Health Check", test_health()))

    # Test 2: Inscription
    results.append(("Inscription", test_register()))

    # Test 3: Connexion
    token = test_login()
    results.append(("Connexion", token is not None))

    if token:
        # Test 4: Analyse complète
        results.append(("Analyse Complète", test_analyze_complete(token)))

        # Test 5: Profil
        results.append(("Profil", test_profile(token)))

        # Test 6: Historique
        results.append(("Historique", test_history(token)))

        # Test 7: Statistiques
        results.append(("Statistiques", test_statistics(token)))

    # Résumé
    print_section("RÉSUMÉ DES TESTS")

    success_count = sum(1 for _, result in results if result)
    total_count = len(results)

    for name, result in results:
        status = f"{Colors.GREEN}✅ PASSÉ{Colors.END}" if result else f"{Colors.RED}❌ ÉCHOUÉ{Colors.END}"
        print(f"{name}: {status}")

    print(f"\n{Colors.BOLD}Résultat Global: {success_count}/{total_count} tests réussis{Colors.END}")

    if success_count == total_count:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 TOUS LES TESTS ONT RÉUSSI !{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  Certains tests ont échoué. Vérifiez que l'API est démarrée.{Colors.END}")

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print_error("❌ Impossible de se connecter à l'API")
        print_info("Assurez-vous que l'API est démarrée avec : python api_v2.py")
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
