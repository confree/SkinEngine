import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from api_gateway import filter_medical_terms

test_data = {
    "title": "Medical Report",
    "description": "The clinical treatment of acne vulgaris and dermatological diagnosis shows significant improvement.",
    "curation": {
        "skincare_prescription": "Skincare Prescription",
        "makeup_prescription": "Makeup Prescription (Rx)",
        "hair_prescription": "Hair Prescription"
    },
    "details": [
        "처방 결과는 다음과 같습니다.",
        "진단명: 여드름 치료를 위한 처방 진행",
        "Clinical result from medical clinic under therapy."
    ]
}

print("Original Data:")
print(test_data)
print("\nFiltered Data:")
filtered = filter_medical_terms(test_data)
import json
print(json.dumps(filtered, indent=4, ensure_ascii=False))
