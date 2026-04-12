document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const preview = document.getElementById('preview');
    const placeholder = document.getElementById('placeholder');
    const scanLine = document.getElementById('scan-line');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultsSection = document.getElementById('results');
    const locationInput = document.getElementById('location');
    const locationDisplay = document.getElementById('location-display');
    const detectLocBtn = document.getElementById('detect-loc-btn');

    // --- Location & Weather Management (OpenWeatherMap Integration) ---
    async function fetchCurrentLocation() {
        if (!locationInput) return;
        locationInput.value = "Detecting global environment & climate...";
        
        const OWM_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"; // 🔑 USER: Please replace with your actual key

        try {
            // Priority 1: Get Lat/Lon via geolocation-db
            const geoRes = await fetch('https://geolocation-db.com/json/');
            const geoData = await geoRes.json();
            
            if (geoData.latitude) {
                const { latitude, longitude, city, country_name } = geoData;
                locationInput.value = `${city}, ${country_name}`;
                
                // Priority 2: Get Precise Climate via OpenWeatherMap One Call 3.0
                try {
                    const weatherRes = await fetch(`https://api.openweathermap.org/data/3.0/onecall?lat=${latitude}&lon=${longitude}&exclude=minutely,hourly,daily&appid=${OWM_API_KEY}&units=metric`);
                    const weatherData = await weatherRes.json();
                    
                    if (weatherData.current) {
                        const { temp, humidity, uvi } = weatherData.current;
                        const weatherDesc = weatherData.current.weather[0].description;
                        
                        // Store climate data in dataset for the AI engine
                        const climateStr = `${weatherDesc}, Temp: ${temp}°C, Humidity: ${humidity}%, UV Index: ${uvi}`;
                        locationDisplay.dataset.weather = climateStr;
                        locationDisplay.innerText = `📍 ${city} (${climateStr})`;
                        console.log(`✅ [Climate] Data Synced: ${climateStr}`);
                    }
                } catch (weatherErr) {
                    console.warn("⚠️ [Climate] OWM API failed (check key). Using basic location.");
                    locationDisplay.innerText = `📍 ${city}, ${country_name}`;
                    locationDisplay.dataset.weather = "Clear (Standard)";
                }
                return;
            }
        } catch (e) {
            console.warn("📡 [Location] Geolocation primary service failed.");
        }

        locationInput.value = "Seoul, Korea (Manual)";
        locationDisplay.dataset.weather = "Clear, Humidity: 40%, UV: Low";
    }

    // Only run when user explicitly clicks the 📍 button
    if (detectLocBtn) {
        detectLocBtn.addEventListener('click', (e) => {
            e.preventDefault();
            fetchCurrentLocation();
        });
    }

    let currentFileHash = 0;

    const scannerOverlay = document.getElementById('scanner-overlay');
    const faceStatus = document.getElementById('face-status');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');

    // 🟢 [Face-api.js] Initialize Models
    async function loadModels() {
        console.log("📡 [AI-Scanner] Loading Tracking Models...");
        const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/';
        try {
            await Promise.all([
                faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
            ]);
            console.log("✅ [AI-Scanner] Detection Models Loaded Successfully.");
        } catch (e) {
            console.error("❌ [AI-Scanner] Model loading failed:", e);
        }
    }
    loadModels();

    // 1. File Upload Logic
    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', handleFile);

    function handleFile(e) {
        const file = e.target.files[0];
        if (file) {
            currentFileHash = Array.from(file.name).reduce((s, c) => s + c.charCodeAt(0), 0) + file.size;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                preview.classList.remove('hidden');
                placeholder.classList.add('hidden');
                
                // Show fixed guide and instruction
                scannerOverlay.classList.remove('hidden');
                faceStatus.innerText = "ALIGN YOUR FACE (CENTRAL)";
                faceStatus.style.color = "#00ff64";
            };
            reader.readAsDataURL(file);
        }
    }

    // 👁️ [PRE-PROCESSING] Eye Sclera based White Balance Correction
    async function applyEyeWhiteBalance(imageElement, landmarks) {
        console.log("👁️ [Pre-processing] Initiating Eye-Sclera White Balance Correction...");
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = imageElement.naturalWidth;
        canvas.height = imageElement.naturalHeight;
        ctx.drawImage(imageElement, 0, 0);

        // Indices for left and right eyes in 68-point landmarks
        const leftEyeIndices = [36, 37, 38, 39, 40, 41];
        const rightEyeIndices = [42, 43, 44, 45, 46, 47];

        const sampleEyePixels = (indices) => {
            let rTotal = 0, gTotal = 0, bTotal = 0, count = 0;
            const points = indices.map(i => landmarks.positions[i]);
            
            // Calculate eye bounding box
            const minX = Math.min(...points.map(p => p.x));
            const maxX = Math.max(...points.map(p => p.x));
            const minY = Math.min(...points.map(p => p.y));
            const maxY = Math.max(...points.map(p => p.y));
            
            // Sample pixels inside the eye region
            const imageData = ctx.getImageData(minX, minY, maxX - minX, maxY - minY);
            const data = imageData.data;
            
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i], g = data[i+1], b = data[i+2];
                // Focus on "white-ish" pixels (Sclera) to avoid iris/pupil
                if (r > 150 && g > 150 && b > 150 && Math.abs(r-g) < 30 && Math.abs(g-b) < 30) {
                    rTotal += r; gTotal += g; bTotal += b;
                    count++;
                }
            }
            return count > 0 ? { r: rTotal/count, g: gTotal/count, b: bTotal/count } : null;
        };

        const leftRes = sampleEyePixels(leftEyeIndices);
        const rightRes = sampleEyePixels(rightEyeIndices);

        let finalRef = null;

        if (leftRes || rightRes) {
            finalRef = leftRes && rightRes ? 
                { r: (leftRes.r + rightRes.r)/2, g: (leftRes.g + rightRes.g)/2, b: (leftRes.b + rightRes.b)/2 } :
                (leftRes || rightRes);
            console.log(`🎯 [Pre-processing] Eye Sclera Reference Found: ${Math.round(finalRef.r)}, ${Math.round(finalRef.g)}, ${Math.round(avg.b)}`);
        } else {
            // 🌫️ [Fallback] Gray World Algorithm: Assume average of image is neutral gray
            console.log("🌫️ [Pre-processing] Eye Sclera not found. Falling back to Grayworld Algorithm...");
            const fullData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
            let rSum = 0, gSum = 0, bSum = 0;
            for (let i = 0; i < fullData.length; i += 4) {
                rSum += fullData[i]; gSum += fullData[i+1]; bSum += fullData[i+2];
            }
            const pixCount = fullData.length / 4;
            finalRef = { r: rSum/pixCount, g: gSum/pixCount, b: bSum/pixCount };
            console.log(`🎯 [Pre-processing] Grayworld Reference: ${Math.round(finalRef.r)}, ${Math.round(finalRef.g)}, ${Math.round(finalRef.b)}`);
        }

        if (finalRef) {
            // Apply Correction
            const targetGray = (finalRef.r + finalRef.g + finalRef.b) / 3;
            const rGain = targetGray / finalRef.r;
            const gGain = targetGray / finalRef.g;
            const bGain = targetGray / finalRef.b;

            const fullImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const pixels = fullImageData.data;
            for (let i = 0; i < pixels.length; i += 4) {
                pixels[i]   = Math.min(255, pixels[i]   * rGain);
                pixels[i+1] = Math.min(255, pixels[i+1] * gGain);
                pixels[i+2] = Math.min(255, pixels[i+2] * bGain);
            }
            ctx.putImageData(fullImageData, 0, 0);
            console.log("✅ [Pre-processing] Hybrid White Balance Applied.");
        }

        return new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.95));
    }

    // 2. Real-time Analysis Integration
    analyzeBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (!file) {
            alert("고객님, 먼저 셀카 사진을 업로드해 주세요.");
            return;
        }

        analyzeBtn.innerText = "Processing Biometrics...";
        analyzeBtn.disabled = true;
        scannerOverlay.classList.add('active-scan');
        scannerOverlay.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            // 🔍 [Step 1] Face Detection for Pre-processing
            const landmarks = await faceapi.detectSingleFace(preview, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks();
            
            let finalImageBlob = file;
            if (landmarks) {
                // 🔍 [Step 2] Apply Eye Sclera White Balance
                finalImageBlob = await applyEyeWhiteBalance(preview, landmarks);
            }

            // 🔍 [Step 3] Proceed to API Gateway
            const isLocalFile = window.location.protocol === 'file:';
            const API_URL = isLocalFile ? 'http://localhost:8000/analyze' : '/analyze';
            
            const formData = new FormData();
            formData.append('image', finalImageBlob, 'processed.jpg');
            formData.append('location', locationInput.value);
            formData.append('weather', locationDisplay.dataset.weather || "Clear (Standard)");

            console.log(`🚀 Sending request to: ${API_URL}`);
            const response = await fetch(API_URL, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorBody = await response.text();
                throw new Error(`Server Error: ${response.status} - ${errorBody}`);
            }

            const report = await response.json();
            displayResults(report);
            
            // Finalize
            scannerOverlay.classList.add('hidden');
            scannerOverlay.classList.remove('active-scan'); // Stop laser
            analyzeBtn.innerText = "Analysis Complete";
            analyzeBtn.disabled = false;
            
            // Show result sections and scroll
            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error("AI Analysis Debug Info:", error);
            alert("가디언 엔진 연결에 실패했습니다.\n\n확인사항:\n1. 브라우저 주소창이 http://localhost:8000 인가요?\n2. 터미널에서 python src/api_gateway.py 가 실행 중인가요?");
            analyzeBtn.innerText = "Retry Analysis";
            analyzeBtn.disabled = false;
            scannerOverlay.classList.add('hidden');
            scannerOverlay.classList.remove('active-scan');
        }
    });

    function displayResults(data) {
        const imageType = data.image_type || "face";
        const biometricsPanel = document.querySelector('.biometrics-panel');
        
        // 0. Dynamic UI Filtering (Hide biometrics for non-face images)
        if (imageType !== "face") {
            biometricsPanel.style.display = "none";
            console.log(`🧹 [UI] ${imageType} 모드: 피부 수치 패널 숨김 처리`);
        } else {
            biometricsPanel.style.display = "block";
            
            // 1. Update Medical Biometrics (Only for Face)
            const skinTypeMap = {
                "Very Fair": "매우 밝은 피부 (Typology I)",
                "Fair": "밝은 피부 (Typology II)",
                "Intermediate": "보통 피부 (중간톤 / Typology III)",
                "Tan": "태닝된 피부 (Typology IV)",
                "Brown": "갈색 피부 (Typology V)",
                "Black": "어두운 피부 (Typology VI)"
            };
            
            document.getElementById('ita-val').innerText = data.biometrics.ita;
            document.getElementById('skin-type').innerText = skinTypeMap[data.biometrics.skin_type] || data.biometrics.skin_type;
            document.getElementById('skin-age-val').innerText = data.biometrics.skin_age;
            
            document.getElementById('melanin-val').innerText = (data.biometrics.melanin_index || 0).toFixed(1);
            document.getElementById('erythema-val').innerText = (data.biometrics.erythema_index || 0).toFixed(1);
            document.getElementById('elasticity-val').innerText = (data.biometrics.elasticity_score || 0).toFixed(1);
        }

        // 2. Bind Expert Strategic Consultation (New 4 Fields)
        if (data.consult) {
            document.getElementById('consult-summary').innerText = data.consult.summary;
            document.getElementById('consult-skincare').innerText = data.consult.skincare;
            document.getElementById('consult-makeup').innerText = data.consult.makeup;
            document.getElementById('consult-hair').innerText = data.consult.hair;
        }

        // 3. Bind Long-form Professional Dossier
        document.getElementById('medical-report-text').innerText = data.dossier.medical_report;
        document.getElementById('makeup-strategy-text').innerText = data.dossier.makeup_strategy;
        document.getElementById('hair-architecture-text').innerText = data.dossier.hair_architecture;

        // 4. Holistic Prescriptions
        document.getElementById('p-skin-desc').innerText = data.curation.skincare_prescription;
        document.getElementById('shampoo-desc').innerText = data.dossier.shampoo_prescription;
        document.getElementById('nutrient-desc').innerText = data.dossier.nutritional_advice || data.risks.nutritional_prescription;

        console.log(`✅ [UI] ${imageType.toUpperCase()} Dossier v4.0 Filtered & Rendered.`);
    }

    // 📄 PDF Download Logic (Fixed: Pro-Customer White Mode)
    downloadPdfBtn.addEventListener('click', async () => {
        const element = document.querySelector('.dossier-wrapper');
        
        if (!element || element.innerText.trim().length < 10) {
            alert("고객님, 먼저 피부 분석을 완료해 주세요.");
            return;
        }

        // 🟢 Switch BODY to Medical White Mode for capture
        document.body.classList.add('pdf-export-mode');
        window.scrollTo(0, 0);

        const opt = {
            margin:       [10, 5, 10, 5],
            filename:     `VeriSkin_Report_고객님_${new Date().toISOString().slice(0,10)}.pdf`,
            image:        { type: 'jpeg', quality: 1.0 },
            html2canvas:  { 
                scale: 4, // Upgraded to 4 for ultra-sharp vector-like text
                useCORS: true, 
                logging: false, 
                letterRendering: true,
                backgroundColor: '#ffffff'
            },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak:    { mode: ['avoid-all', 'css', 'legacy'] }
        };
        
        try {
            await html2pdf().set(opt).from(element).save();
            console.log("✅ [PDF] 고객님 전용 고대비 화이트 리포트 생성 완료");
        } catch (err) {
            console.error("❌ PDF generation error:", err);
            alert("리포트 생성 중 오류가 발생했습니다.");
        } finally {
            // 🔴 Restore Dark Mode for UI
            document.body.classList.remove('pdf-export-mode');
        }
    });
});
