# SkinEngine Core Intelligence Rules
[v12.9.0] Last Updated: 2026-04-13

## 🚨 CORE PRINCIPLE: NO FALLBACKS, NO DEFAULTS
엔진 내부에서 인공지능 분석 결과가 누락되었을 때 임의의 수치를 할당하는 행위는 **데이터 오염**으로 간주합니다.

### 1. 🛡️ Strict Biometric Integrity
- AI가 `skin_age`, `elasticity_score`, `wrinkle_score` 등을 반환하지 않으면, 엔진은 절대 30이나 0.6 같은 값을 채워넣지 않습니다.
- 데이터 누락 감지 시 즉시 `ValueError`를 발생시켜 분석 리포트 생성을 중단하십시오.

### 2. ⚡ Fast-Error Relay
- 엔진에서 발생한 에러는 `api_gateway.py`를 통해 클라이언트에게 가감 없이 전달되어야 합니다.
- 시스템의 약점을 "괜찮은 척" 포장하지 마십시오.

### 3. 📝 Diagnostic Logging
- 모든 요청(`req_*.json`)과 응답(`res_*.json`)은 디버깅을 위해 상세히 기록되어야 하며, 특히 에러 발생 시의 입력 컨텍스트를 보존하십시오.

---
**"에러가 나지 않는 가짜 성공보다, 에러가 나는 진짜 실패를 선호한다."**
이 규칙을 위반하는 코드는 프로덕션에 배포될 수 없습니다.
