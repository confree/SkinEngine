import math
from typing import Dict, Tuple

class BiometricsEngine:
    """
    Layer 1: Biometrics - Analysis of pixel data to extract skin health indicators.
    """
    
    def __init__(self):
        # Chardon et al. 1988 / 1991 Skin Color Typology (ITA)
        self.skin_types = [
            {"range": (55, 90), "name": "Very Light"},
            {"range": (41, 55), "name": "Light"},
            {"range": (28, 41), "name": "Intermediate"},
            {"range": (10, 28), "name": "Tan"},
            {"range": (-30, 10), "name": "Brown"},
            {"range": (-90, -30), "name": "Dark"}
        ]

    def rgb_to_lab(self, r: int, g: int, b: int) -> Dict[str, float]:
        """
        Converts RGB to CIELAB color space.
        Simplified conversion (Reference: https://www.easyrgb.com/)
        """
        # 1. Normalize RGB to [0, 1]
        var_R = r / 255.0
        var_G = g / 255.0
        var_B = b / 255.0

        # Linearize RGB (Inverse Gamma)
        def pivot_rgb(n):
            return ((n + 0.055) / 1.055) ** 2.4 if n > 0.04045 else n / 12.92

        var_R = pivot_rgb(var_R) * 100
        var_G = pivot_rgb(var_G) * 100
        var_B = pivot_rgb(var_B) * 100

        # 2. RGB to XYZ
        X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
        Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
        Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505

        # 3. XYZ to LAB (Reference white D65)
        var_X = X / 95.047
        var_Y = Y / 100.000
        var_Z = Z / 108.883

        def pivot_xyz(n):
            return n ** (1/3) if n > 0.008856 else (7.787 * n) + (16 / 116)

        var_X = pivot_xyz(var_X)
        var_Y = pivot_xyz(var_Y)
        var_Z = pivot_xyz(var_Z)

        L = (116 * var_Y) - 16
        a = 500 * (var_X - var_Y)
        b = 200 * (var_Y - var_Z)

        return {"L": L, "a": a, "b": b}

    def calculate_ita(self, L: float, b: float) -> float:
        """
        Calculates Individual Typology Angle (ITA).
        Formula: ITA = Arctan((L* - 50) / b*) * (180 / PI)
        """
        if b == 0:
            return 0.0
        ita = math.atan2((L - 50), b) * (180 / math.pi)
        return ita

    def classify_skin_type(self, ita: float) -> str:
        """
        Classifies skin color based on ITA value using Chardon et al. (1988) criteria.
        """
        for entry in self.skin_types:
            low, high = entry["range"]
            if low <= ita < high:
                return entry["name"]
        return "Unknown"

    def quantify_indices(self, lab: Dict[str, float]) -> Tuple[float, float]:
        """
        Quantifies Melanin and Erythema Index.
        Melanin: Based on L* (Brightness)
        Erythema: Based on a* (Redness)
        """
        L, a = lab["L"], lab["a"]
        
        # Simple Melanin Index estimation (0-100)
        melanin_index = (100.0 - L)
        
        # Simple Erythema Index estimation (0-100)
        # erythema_index reflects redness, higher scale if redder
        erythema_index = max(0.0, a * 2.0) 
        
        return melanin_index, erythema_index

if __name__ == "__main__":
    engine = BiometricsEngine()
    # Test with Asian Intermediate Skin (L=60, a=10, b=15)
    lab = {"L": 62.0, "a": 12.0, "b": 18.0}
    ita = engine.calculate_ita(lab["L"], lab["b"])
    skin_type = engine.classify_skin_type(ita)
    mi, ei = engine.quantify_indices(lab)
    
    print(f"LAB: {lab}")
    print(f"ITA: {ita:.2f}")
    print(f"Skin Type: {skin_type}")
    print(f"Melanin: {mi:.2f}, Erythema: {ei:.2f}")
