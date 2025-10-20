"""
Moteur de Recommandation d'Exercices
Suggère des exercices ciblés basés sur l'indicateur prioritaire à améliorer
"""
from typing import Dict, List, Optional


class ExerciseRecommender:
    """Génère des recommandations d'exercices personnalisées"""

    def __init__(self):
        # Base de données d'exercices par pose et par indicateur faible
        self.exercise_database = self._build_exercise_database()

    def _build_exercise_database(self) -> Dict:
        """
        Construit la base de données d'exercices

        Structure:
        {
            "pose_name": {
                "indicator_name": {
                    "title": "Nom de l'exercice",
                    "description": "Description détaillée",
                    "duration": "2-3 minutes",
                    "difficulty": "beginner/intermediate/advanced",
                    "steps": ["étape 1", "étape 2", ...]
                }
            }
        }
        """
        return {
            "downdog": {
                "alignment": {
                    "title": "Mobilité des Épaules au Mur",
                    "description": "Améliorez l'alignement en travaillant la mobilité des épaules",
                    "duration": "3 minutes",
                    "difficulty": "beginner",
                    "steps": [
                        "Placez-vous face à un mur, bras tendus au-dessus de la tête",
                        "Avancez les mains sur le mur et penchez-vous en avant",
                        "Gardez le dos droit et poussez la poitrine vers le sol",
                        "Maintenez 30 secondes, répétez 5 fois"
                    ],
                    "benefit": "Améliore la flexibilité des épaules et l'alignement du dos"
                },
                "shoulder_opening": {
                    "title": "Chien Tête en Bas avec Genoux Pliés",
                    "description": "Variante pour développer l'ouverture des épaules",
                    "duration": "2 minutes",
                    "difficulty": "beginner",
                    "steps": [
                        "Entrez dans la posture du chien tête en bas",
                        "Pliez généreusement les genoux",
                        "Concentrez-vous sur la poussée des mains dans le sol",
                        "Élevez les hanches vers le plafond",
                        "Maintenez 10 respirations"
                    ],
                    "benefit": "Permet de se concentrer sur l'ouverture des épaules sans la contrainte des ischio-jambiers"
                },
                "leg_extension": {
                    "title": "Étirement des Ischio-jambiers Assis",
                    "description": "Préparez vos jambes pour une meilleure extension",
                    "duration": "4 minutes",
                    "difficulty": "beginner",
                    "steps": [
                        "Asseyez-vous jambes tendues devant vous",
                        "Inspirez en allongeant la colonne",
                        "Expirez en vous penchant doucement vers l'avant",
                        "Attrapez vos pieds ou vos tibias",
                        "Maintenez 1 minute par côté"
                    ],
                    "benefit": "Augmente la flexibilité des ischio-jambiers pour mieux tendre les jambes"
                },
                "symmetry": {
                    "title": "Chien Tête en Bas avec Repères Visuels",
                    "description": "Travaillez la symétrie avec des points de repère",
                    "duration": "2 minutes",
                    "difficulty": "intermediate",
                    "steps": [
                        "Placez un tapis de yoga avec des lignes parallèles",
                        "Positionnez vos mains à égale distance des bords",
                        "Vérifiez que vos pieds sont également symétriques",
                        "Maintenez en respirant profondément",
                        "Ajustez si nécessaire"
                    ],
                    "benefit": "Développe la conscience corporelle et l'équilibre gauche-droite"
                }
            },
            "plank": {
                "alignment": {
                    "title": "Planche avec Bâton sur le Dos",
                    "description": "Utilisez un accessoire pour sentir l'alignement parfait",
                    "duration": "3 séries de 30 secondes",
                    "difficulty": "intermediate",
                    "steps": [
                        "Placez un bâton de yoga ou une règle le long de votre dos",
                        "Le bâton doit toucher : tête, haut du dos, et bassin",
                        "Entrez en position planche",
                        "Maintenez le contact avec les 3 points",
                        "Si le bâton se décolle, ajustez votre position"
                    ],
                    "benefit": "Feedback tactile immédiat pour un alignement optimal"
                },
                "core_strength": {
                    "title": "Progression Planche Modifiée",
                    "description": "Renforcez progressivement votre core",
                    "duration": "5 minutes",
                    "difficulty": "beginner",
                    "steps": [
                        "Semaine 1: Planche sur genoux - 3×30 secondes",
                        "Semaine 2: Planche sur genoux - 3×45 secondes",
                        "Semaine 3: Planche complète - 3×20 secondes",
                        "Semaine 4: Planche complète - 3×30 secondes",
                        "Augmentez progressivement"
                    ],
                    "benefit": "Développe la force du core de manière progressive et sûre"
                },
                "shoulder_position": {
                    "title": "Renforcement des Épaules en Position Haute",
                    "description": "Stabilisez vos épaules pour une meilleure planche",
                    "duration": "4 minutes",
                    "difficulty": "intermediate",
                    "steps": [
                        "Position de planche, mains sous les épaules",
                        "Poussez le sol pour arrondir le haut du dos",
                        "Revenez à la position neutre",
                        "Répétez 10 fois",
                        "Faites 3 séries"
                    ],
                    "benefit": "Active les muscles stabilisateurs des épaules"
                }
            },
            "tree": {
                "balance": {
                    "title": "Équilibre Progressif sur Une Jambe",
                    "description": "Développez votre équilibre étape par étape",
                    "duration": "5 minutes",
                    "difficulty": "beginner",
                    "steps": [
                        "Niveau 1: Debout, soulevez un talon (orteils au sol) - 30s",
                        "Niveau 2: Pied sur la cheville - 30s",
                        "Niveau 3: Pied sur le mollet - 30s",
                        "Niveau 4: Pied sur la cuisse intérieure - 30s",
                        "Répétez chaque côté, 2 séries"
                    ],
                    "benefit": "Progression douce pour améliorer l'équilibre et la stabilité"
                },
                "hip_opening": {
                    "title": "Papillon Assis (Baddha Konasana)",
                    "description": "Ouvrez vos hanches pour mieux placer le pied",
                    "duration": "3 minutes",
                    "difficulty": "beginner",
                    "steps": [
                        "Asseyez-vous, plantes des pieds l'une contre l'autre",
                        "Rapprochez les pieds de votre bassin",
                        "Laissez les genoux tomber sur les côtés",
                        "Gardez le dos droit",
                        "Maintenez 2-3 minutes en respirant profondément"
                    ],
                    "benefit": "Augmente la mobilité des hanches pour une posture de l'arbre plus confortable"
                },
                "focus": {
                    "title": "Méditation du Point Focal (Drishti)",
                    "description": "Améliorez votre concentration pour mieux tenir l'équilibre",
                    "duration": "5 minutes",
                    "difficulty": "beginner",
                    "steps": [
                        "Choisissez un point fixe devant vous",
                        "Debout en montagne (Tadasana)",
                        "Fixez le point sans cligner des yeux",
                        "Respirez calmement pendant 1 minute",
                        "Puis pratiquez la posture de l'arbre"
                    ],
                    "benefit": "Développe la concentration mentale essentielle à l'équilibre"
                }
            },
            "warrior2": {
                "arm_alignment": {
                    "title": "Renforcement des Bras en Guerrier 2 au Mur",
                    "description": "Utilisez le mur pour perfectionner l'alignement des bras",
                    "duration": "3 minutes",
                    "difficulty": "intermediate",
                    "steps": [
                        "Placez-vous en Guerrier 2 près d'un mur",
                        "Votre bras arrière touche le mur",
                        "Assurez-vous que les bras forment une ligne droite",
                        "Maintenez 1 minute par côté",
                        "Répétez 2 fois"
                    ],
                    "benefit": "Feedback tactile pour un alignement parfait des bras"
                },
                "knee_flexion": {
                    "title": "Squats de Renforcement des Quadriceps",
                    "description": "Renforcez vos jambes pour atteindre la flexion à 90°",
                    "duration": "5 minutes",
                    "difficulty": "intermediate",
                    "steps": [
                        "Squats profonds: 3 séries de 15 répétitions",
                        "Fentes avant: 3 séries de 10 par jambe",
                        "Chaise au mur (90°): 3×30 secondes",
                        "Reposez 30 secondes entre les séries"
                    ],
                    "benefit": "Développe la force des cuisses pour maintenir le genou plié à 90°"
                },
                "hip_opening": {
                    "title": "Fente Basse (Anjaneyasana)",
                    "description": "Ouvrez les hanches pour une meilleure rotation",
                    "duration": "4 minutes",
                    "difficulty": "beginner",
                    "steps": [
                        "Fente avant, genou arrière au sol",
                        "Poussez doucement le bassin vers l'avant",
                        "Levez les bras vers le ciel",
                        "Maintenez 1 minute par côté",
                        "Répétez 2 fois"
                    ],
                    "benefit": "Améliore la mobilité des hanches pour une ouverture optimale en Guerrier 2"
                }
            },
            "goddess": {
                "squat_depth": {
                    "title": "Progression du Squat de la Déesse",
                    "description": "Descendez progressivement plus bas",
                    "duration": "4 minutes",
                    "difficulty": "intermediate",
                    "steps": [
                        "Semaine 1: Squat à 1/4 - tenir 30s",
                        "Semaine 2: Squat à 1/2 - tenir 30s",
                        "Semaine 3: Squat à 3/4 - tenir 30s",
                        "Semaine 4: Squat complet - tenir 30s",
                        "3 répétitions par niveau"
                    ],
                    "benefit": "Progression sûre pour atteindre la profondeur optimale"
                },
                "knee_alignment": {
                    "title": "Squats avec Bande Élastique",
                    "description": "Corrigez l'alignement des genoux avec résistance",
                    "duration": "3 minutes",
                    "difficulty": "intermediate",
                    "steps": [
                        "Placez une bande élastique autour des cuisses",
                        "Position de la déesse, pieds écartés",
                        "La bande tire vos genoux vers l'intérieur",
                        "Résistez en poussant les genoux vers l'extérieur",
                        "10 répétitions, 3 séries"
                    ],
                    "benefit": "Renforce les muscles qui maintiennent l'alignement genoux-pieds"
                },
                "inner_thigh": {
                    "title": "Étirement des Adducteurs Assis",
                    "description": "Améliorez la flexibilité pour un meilleur écartement",
                    "duration": "5 minutes",
                    "difficulty": "beginner",
                    "steps": [
                        "Assis, jambes écartées en V",
                        "Gardez le dos droit",
                        "Penchez-vous vers l'avant doucement",
                        "Maintenez 2 minutes",
                        "Puis penchez-vous vers chaque jambe (1 min chacune)"
                    ],
                    "benefit": "Augmente la flexibilité des adducteurs pour un écartement plus large"
                }
            }
        }

    def get_recommendation(self, pose_name: str, priority_indicator: Dict,
                          user_skill_level: str = "intermediate") -> Optional[Dict]:
        """
        Génère une recommandation d'exercice basée sur l'indicateur prioritaire

        Args:
            pose_name: Nom de la pose analysée
            priority_indicator: Dict avec name, score, improvement_needed
            user_skill_level: Niveau de l'utilisateur (beginner/intermediate/advanced)

        Returns:
            Dict avec l'exercice recommandé ou None si pas de correspondance
        """
        indicator_name = priority_indicator.get('name')
        improvement_needed = priority_indicator.get('improvement_needed')

        if not indicator_name or not pose_name:
            return None

        # Chercher dans la base de données
        pose_exercises = self.exercise_database.get(pose_name, {})
        exercise = pose_exercises.get(indicator_name)

        if not exercise:
            # Pas d'exercice spécifique trouvé, retourner une recommandation générique
            return self._get_generic_recommendation(pose_name, indicator_name, improvement_needed)

        # Ajouter des informations contextuelles
        recommendation = exercise.copy()
        recommendation['target_indicator'] = indicator_name
        recommendation['current_score'] = priority_indicator.get('score', 0)
        recommendation['improvement_level'] = improvement_needed
        recommendation['pose'] = pose_name

        # Ajouter un message personnalisé
        recommendation['motivation'] = self._generate_motivation_message(
            improvement_needed, user_skill_level, indicator_name
        )

        return recommendation

    def _get_generic_recommendation(self, pose_name: str, indicator_name: str,
                                   improvement_needed: str) -> Dict:
        """Génère une recommandation générique si aucun exercice spécifique n'est trouvé"""
        return {
            "title": f"Amélioration de {indicator_name} pour {pose_name}",
            "description": f"Travaillez cet aspect en pratiquant la pose régulièrement",
            "duration": "5 minutes",
            "difficulty": "intermediate",
            "steps": [
                f"Pratiquez {pose_name} quotidiennement",
                f"Concentrez-vous spécifiquement sur {indicator_name}",
                "Utilisez un miroir pour vérifier votre forme",
                "Filmez-vous pour analyser vos progrès"
            ],
            "benefit": f"Améliore progressivement {indicator_name}",
            "target_indicator": indicator_name,
            "improvement_level": improvement_needed,
            "pose": pose_name,
            "motivation": "La pratique régulière est la clé du progrès !"
        }

    def _generate_motivation_message(self, improvement_level: str,
                                     user_skill_level: str, indicator_name: str) -> str:
        """Génère un message de motivation personnalisé"""
        messages = {
            "critique": {
                "beginner": f"🌱 Ne vous découragez pas ! {indicator_name} s'améliorera avec la pratique régulière.",
                "intermediate": f"💪 Vous avez identifié votre point faible. C'est le premier pas vers l'amélioration !",
                "advanced": f"🎯 Même les experts ont des points à perfectionner. Concentrez-vous sur {indicator_name}."
            },
            "important": {
                "beginner": f"✨ Excellent début ! Travaillez {indicator_name} et vous progresserez rapidement.",
                "intermediate": f"🔥 Vous êtes sur la bonne voie. Un peu plus de focus sur {indicator_name} fera la différence.",
                "advanced": f"⭐ Affinez {indicator_name} pour atteindre la maîtrise complète."
            },
            "modéré": {
                "beginner": f"👏 Très bien ! Quelques ajustements sur {indicator_name} et ce sera parfait.",
                "intermediate": f"🌟 Excellente progression ! Peaufinez {indicator_name} pour exceller.",
                "advanced": f"🏆 Presque parfait ! Quelques micro-ajustements sur {indicator_name}."
            },
            "minimal": {
                "beginner": f"🎉 Impressionnant ! Continuez à maintenir ce niveau sur {indicator_name}.",
                "intermediate": f"🔥 Performance exceptionnelle ! Maintenez votre excellence.",
                "advanced": f"👑 Maîtrise totale ! Vous pouvez enseigner cette pose."
            }
        }

        return messages.get(improvement_level, {}).get(
            user_skill_level,
            "Continuez votre pratique avec régularité !"
        )

    def get_multiple_recommendations(self, pose_name: str, indicators: Dict[str, float],
                                    top_n: int = 3, user_skill_level: str = "intermediate") -> List[Dict]:
        """
        Génère plusieurs recommandations basées sur les indicateurs les plus faibles

        Args:
            pose_name: Nom de la pose
            indicators: Tous les indicateurs
            top_n: Nombre de recommandations à retourner
            user_skill_level: Niveau de l'utilisateur

        Returns:
            Liste des exercices recommandés
        """
        # Trier les indicateurs par score croissant
        sorted_indicators = sorted(indicators.items(), key=lambda x: x[1])

        recommendations = []
        for indicator_name, score in sorted_indicators[:top_n]:
            # Déterminer le niveau d'amélioration
            if score >= 85:
                improvement_level = "minimal"
            elif score >= 70:
                improvement_level = "modéré"
            elif score >= 50:
                improvement_level = "important"
            else:
                improvement_level = "critique"

            priority_dict = {
                "name": indicator_name,
                "score": score,
                "improvement_needed": improvement_level
            }

            rec = self.get_recommendation(pose_name, priority_dict, user_skill_level)
            if rec:
                recommendations.append(rec)

        return recommendations
