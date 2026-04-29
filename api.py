from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Import core modules
from GymApp import ExerciseManager
from history_manager import HistoryManager
from generator import WorkoutGenerator

app = FastAPI(title="Smart PPL Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init system brain
manager = ExerciseManager('exercises.json')
history_manager = HistoryManager('history.json')
generator = WorkoutGenerator(manager, history_manager)

# FRONTEND
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    html_content = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Gym Coach</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; padding: 15px; max-width: 600px; margin: auto; background-color: #f0f2f5; color: #1c1e21; }
            h1 { text-align: center; color: #1877f2; font-size: 24px; margin-bottom: 5px;}
            .subtitle { text-align: center; color: #65676b; font-size: 14px; margin-bottom: 20px; }
            
            .control-panel { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 20px; }
            .input-group { margin-bottom: 15px; }
            label { display: block; font-weight: bold; margin-bottom: 8px; font-size: 14px;}
            select, input { width: 100%; padding: 12px; border: 1px solid #ccd0d5; border-radius: 8px; font-size: 16px; box-sizing: border-box; background: #f5f6f7;}
            
            .btn-group { display: flex; gap: 10px; margin-top: 15px; }
            button { flex: 1; padding: 14px; font-size: 15px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: 0.2s; color: white; }
            button:active { transform: scale(0.96); }
            
            .btn-standard { background-color: #8e44ad; }
            .btn-smart { background-color: #e67e22; }
            .btn-finish { background-color: #27ae60; width: 100%; margin-top: 20px; font-size: 18px; display: none; }
            
            .card { background: white; padding: 15px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 5px solid #1877f2; }
            .card-title { font-size: 16px; font-weight: bold; margin-bottom: 8px; color: #1c1e21;}
            .card-meta { font-size: 13px; color: #65676b; line-height: 1.5; }
            .badge-compound { background: #1c1e21; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; }
            .badge-isolation { background: #828282; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; }
            
            #loading { text-align: center; display: none; font-style: italic; color: #888; padding: 20px;}
            .summary { text-align: center; font-weight: bold; color: #e74c3c; margin-bottom: 15px; font-size: 18px;}
        </style>
    </head>
    <body>

        <h1>Smart Gym Coach</h1>
        <div class="subtitle">Hệ thống tối ưu hóa cơ bắp theo thời gian thực</div>

        <div class="control-panel">
            <div class="input-group">
                <label>Bạn có bao nhiêu phút hôm nay?</label>
                <input type="number" id="maxTime" value="45" min="15" max="120">
            </div>
            
            <div class="input-group">
                <label>Nhóm cơ mục tiêu:</label>
                <select id="dayType">
                    <option value="AUTO">🤖 AUTO (Tự quét lịch sử & chọn cơ)</option>
                    <option value="PUSH">Đẩy (Ngực, Vai, Tay sau)</option>
                    <option value="PULL">Kéo (Lưng, Tay trước, Vai sau)</option>
                    <option value="LEG">Chân (Đùi, Mông, Bắp chân)</option>
                </select>
            </div>

            <div class="btn-group">
                <button class="btn-standard" onclick="generateWorkout('standard')">Đổi Gió (Chuẩn)</button>
                <button class="btn-smart" onclick="generateWorkout('smart')">Tối Ưu DP</button>
            </div>
        </div>

        <div id="loading">Đang phân tích cơ bắp & xếp lịch...</div>
        <div id="workout-list"></div>
        
        <!-- Nút này ẩn đi, chỉ hiện khi đã có lịch tập -->
        <button id="btnFinish" class="btn-finish" onclick="completeWorkout()">✅ HOÀN THÀNH BUỔI TẬP</button>

        <script>
            // Biến toàn cục lưu trữ danh sách bài tập hiện tại
            let currentWorkoutData = [];

            async function generateWorkout(mode) {
                const listDiv = document.getElementById('workout-list');
                const loadingDiv = document.getElementById('loading');
                const btnFinish = document.getElementById('btnFinish');
                
                const time = document.getElementById('maxTime').value;
                const day = document.getElementById('dayType').value;
                
                listDiv.innerHTML = ''; 
                btnFinish.style.display = 'none';
                loadingDiv.style.display = 'block'; 

                let apiUrl = mode === 'standard' 
                    ? `/api/generate-standard?day=${day}&time=${time}`
                    : `/api/generate-smart?day=${day}&time=${time}`;

                try {
                    const response = await fetch(apiUrl);
                    const data = await response.json();
                    loadingDiv.style.display = 'none';

                    if (!data.workout || data.workout.length === 0) {
                        listDiv.innerHTML = '<p style="text-align:center; color: red;">Không tìm thấy bài tập phù hợp! (Có thể cơ bắp cần nghỉ ngơi thêm hoặc thời gian quá ngắn).</p>';
                        return;
                    }

                    // Lưu lại dữ liệu để gửi đi khi bấm Hoàn thành
                    currentWorkoutData = data.workout;

                    let totalTime = 0;
                    let totalScore = 0;

                    data.workout.forEach((ex, index) => {
                        totalTime += (ex.duration || 0);
                        totalScore += (ex.efficiency || 0);

                        const badgeClass = ex.type_score === 2 ? 'badge-compound' : 'badge-isolation';
                        const badgeText = ex.type_score === 2 ? 'Compound' : 'Isolation';
                        
                        const secondaryTargets = ex.secondary_targets && ex.secondary_targets.length > 0 
                                                 ? `<br>🎯 Cơ phụ: ${ex.secondary_targets.join(', ')}` 
                                                 : '';

                        // Lấy description (nếu không có thì để chuỗi rỗng)
                        const description = ex.description || "Đang cập nhật hướng dẫn cho bài tập này.";

                        const cardHTML = `
                            <div class="card">
                                <div class="card-title">${index + 1}. ${ex.name}</div>
                                <div class="card-meta">
                                    <span class="${badgeClass}">${badgeText}</span> 
                                    | Nhóm cơ: <b>${ex.target_area}</b>
                                    ${secondaryTargets}
                                    
                                    <div style="margin-top: 10px; background: #f0f2f5; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #ddd;">
                                        <span style="font-weight: bold; color: #2c3e50; font-size: 14px;">
                                            🔥 Khuyến nghị: ${ex.sets} Hiệp x ${ex.reps} Reps
                                        </span>
                                    </div>

                                    <div style="margin-top: 8px; color: #d35400;">
                                        ⏱ ${ex.duration} phút | ⭐ Điểm: ${ex.efficiency}
                                    </div>
                                    
                                    <!-- NÚT XEM CÁCH TẬP -->
                                    <button onclick="toggleDescription(${index})" style="background: none; border: none; color: #1877f2; font-size: 13px; font-weight: bold; cursor: pointer; padding: 0; margin-top: 8px; display: inline-block;">
                                        📖 Xem cách tập
                                    </button>

                                    <!-- KHUNG HƯỚNG DẪN (Mặc định Ẩn) -->
                                    <div id="desc-${index}" style="display: none; margin-top: 10px; padding: 12px; background: #e8f4fd; border-radius: 6px; font-size: 13.5px; color: #1c1e21; border-left: 4px solid #1877f2; line-height: 1.5;">
                                        <b>💡 Hướng dẫn chuẩn form:</b><br>
                                        ${description}
                                    </div>
                                </div>
                            </div>
                        `;
                        listDiv.innerHTML += cardHTML;
                    });
                    
                    listDiv.innerHTML = `<div class="summary">Tổng thời gian: ${totalTime} phút | Tổng điểm: ${totalScore}</div>` + listDiv.innerHTML;
                    
                    // Hiện nút Hoàn thành
                    btnFinish.style.display = 'block';

                } catch (error) {
                    loadingDiv.style.display = 'none';
                    listDiv.innerHTML = '<p style="color:red; text-align:center;">Lỗi kết nối tới Server!</p>';
                }
            }

            // Hàm gửi dữ liệu về Server để lưu lịch sử
            async function completeWorkout() {
                if (currentWorkoutData.length === 0) return;
                
                const btnFinish = document.getElementById('btnFinish');
                btnFinish.innerText = 'Đang lưu...';
                btnFinish.disabled = true;

                try {
                    const response = await fetch('/api/complete-workout', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ exercises: currentWorkoutData })
                    });
                    
                    const result = await response.json();
                    if (result.status === 'success') {
                        alert('🎉 Tuyệt vời! Hệ thống đã ghi nhận lịch sử tập luyện của bạn.');
                        document.getElementById('workout-list').innerHTML = '';
                        btnFinish.style.display = 'none';
                        btnFinish.innerText = '✅ HOÀN THÀNH BUỔI TẬP';
                        btnFinish.disabled = false;
                        currentWorkoutData = []; // Xóa data cũ
                    }
                } catch (error) {
                    alert('Lỗi khi lưu lịch sử. Vui lòng thử lại!');
                    btnFinish.innerText = '✅ HOÀN THÀNH BUỔI TẬP';
                    btnFinish.disabled = false;
                }
            }

            // Hàm xử lý việc đóng mở hướng dẫn tập
            function toggleDescription(index) {
                const descDiv = document.getElementById(`desc-${index}`);
                if (descDiv.style.display === 'none') {
                    descDiv.style.display = 'block';
                } else {
                    descDiv.style.display = 'none';
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# API ENDPOINTS

@app.get("/api/generate-standard")
def api_gen_standard(day: str, time: int):
    workout = generator.generate_standard_workout(day, time)
    return {"status": "success", "workout": workout}

@app.get("/api/generate-smart")
def api_gen_smart(day: str, time: int):
    workout = generator.generate_smart_workout(day, time)
    return {"status": "success", "workout": workout}

# Pydantic model for JSON
class WorkoutLog(BaseModel):
    exercises: List[dict]

@app.post("/api/complete-workout")
def api_complete_workout(log: WorkoutLog):
    # Call HistoryManager
    history_manager.record_workout(log.exercises)
    return {"status": "success", "message": "Đã cập nhật lịch sử."}