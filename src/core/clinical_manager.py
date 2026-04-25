import psycopg2
from typing import List, Dict, Any

class ClinicalManager:
    """
    [Clinical Intelligence Manager]
    Handles connection to SE_clinical tables and retrieves expert guidelines.
    """
    def __init__(self, db_params: Dict[str, Any]):
        self.db_params = db_params

    def _get_connection(self):
        return psycopg2.connect(**self.db_params)

    def get_clinical_advice(self, concerns: List[str]) -> Dict[str, Any]:
        """
        Retrieves clinical guidelines and ingredient mappings for a list of concerns.
        Concerns could be 'Atopy', 'Acne', etc.
        """
        advice = {
            "disease_guidelines": [],
            "ingredient_mappings": [],
            "regulatory_checks": []
        }
        
        if not concerns:
            return advice

        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            # 1. Fetch Disease Guidelines (Fuzzy match on name)
            for concern in concerns:
                cur.execute("""
                    SELECT disease_name, pathophysiology, guideline_source, core_medical_rx, 
                           cleansing_guide, moisturizing_guide, contraindications
                    FROM SE_disease_official_guidelines
                    WHERE disease_name ILIKE %s OR %s ILIKE '%%' || disease_name || '%%'
                """, (f"%{concern}%", concern))
                res = cur.fetchone()
                if res:
                    advice["disease_guidelines"].append({
                        "name": res[0],
                        "pathophysiology": res[1],
                        "source": res[2],
                        "medical_rx": res[3],
                        "cleansing": res[4],
                        "moisturizing": res[5],
                        "contraindications": res[6]
                    })

            # 2. Fetch Ingredient Mappings
            for concern in concerns:
                cur.execute("""
                    SELECT clinical_symptoms, hero_ingredients, villain_ingredients, clinical_evidence
                    FROM SE_symptom_ingredient_mapping
                    WHERE clinical_symptoms ILIKE %s OR %s ILIKE '%%' || clinical_symptoms || '%%'
                """, (f"%{concern}%", concern))
                res = cur.fetchone()
                if res:
                    advice["ingredient_mappings"].append({
                        "symptom": res[0],
                        "hero": res[1],
                        "villain": res[2],
                        "evidence": res[3]
                    })
                    
        finally:
            cur.close()
            conn.close()
            
        return advice

    def check_regulatory_limit(self, ingredient_name: str) -> Dict[str, Any]:
        """Checks if an ingredient has MFDS regulation."""
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT functional_category, inci_name, concentration_limit, efficacy_claim_rule
                FROM SE_mfds_ingredient_regulation
                WHERE inci_name ILIKE %s
            """, (f"%{ingredient_name}%",))
            res = cur.fetchone()
            if res:
                return {
                    "category": res[0],
                    "name": res[1],
                    "limit": res[2],
                    "efficacy": res[3]
                }
        finally:
            cur.close()
            conn.close()
        return None
