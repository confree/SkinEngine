from typing import List, Dict, Set

class InteractionEngine:
    """
    Layer 3: Interaction - Chemical contraindication and synergy analysis.
    """
    
    def __init__(self):
        # Database of ingredient contraindications (risks)
        self.contraindications = {
            "Retinol": ["AHA", "BHA", "Glycolic Acid", "Salicylic Acid", "Ascorbic Acid"],
            "Ascorbic Acid": ["Retinol", "Copper Peptides", "Niacinamide (Low pH)"],
            "AHA": ["Retinol", "BHA", "Vitamin C"],
            "BHA": ["Retinol", "AHA", "Vitamin C"]
        }
        
        # Database of ingredient synergies (boosters)
        self.synergies = {
            "Ascorbic Acid": ["Vitamin E", "Ferulic Acid", "Alpha-Bisabolol"],
            "Retinol": ["Bakuchiol", "Ceramides"],
            "Niacinamide": ["Panthenol", "Ceramides", "Zinc PCA"],
            "Panthenol": ["Niacinamide", "Madecassoside"]
        }

    def analyze_interactions(self, ingredients: List[str]) -> Dict[str, List[str]]:
        """
        Analyzes a list of ingredients for risks (contraindications) and boosters (synergies).
        """
        results = {
            "contraindications": [],
            "synergies": []
        }
        
        ing_set = set(ingredients)
        
        # Check Contraindications
        for ing in ingredients:
            if ing in self.contraindications:
                for conflict in self.contraindications[ing]:
                    if conflict in ing_set:
                        results["contraindications"].append(f"Risk: {ing} + {conflict} (Potential irritation or deactivation)")
        
        # Check Synergies
        for ing in ingredients:
            if ing in self.synergies:
                for booster in self.synergies[ing]:
                    if booster in ing_set:
                        results["synergies"].append(f"Synergy: {ing} + {booster} (Enhanced performance)")
                        
        # Deduplicate
        results["contraindications"] = list(set(results["contraindications"]))
        results["synergies"] = list(set(results["synergies"]))
        
        return results

if __name__ == "__main__":
    engine = InteractionEngine()
    test_list = ["Retinol", "AHA", "Bakuchiol", "Ceramides", "Vitamin E", "Ascorbic Acid", "Ferulic Acid"]
    results = engine.analyze_interactions(test_list)
    
    print(f"Ingredients: {test_list}")
    print(f"Contraindications Found: {results['contraindications']}")
    print(f"Synergies Found: {results['synergies']}")
