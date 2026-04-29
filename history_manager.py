import json
import os
from datetime import datetime

# MUSCLE METADATA
MUSCLE_INFO = {
    "UPPER_CHEST": {"size": "LARGE", "rest_hours": 48, "priority": 10},
    "MID_CHEST": {"size": "LARGE", "rest_hours": 48, "priority": 10},
    "CHEST_FLY": {"size": "SMALL", "rest_hours": 24, "priority": 5},
    "FRONT_DELT": {"size": "SMALL", "rest_hours": 24, "priority": 6},
    "LATERAL_DELT": {"size": "SMALL", "rest_hours": 24, "priority": 6},
    "TRICEP_LATERAL": {"size": "SMALL", "rest_hours": 24, "priority": 5},
    "TRICEP_LONG": {"size": "SMALL", "rest_hours": 24, "priority": 5},
    
    "BACK_VERTICAL": {"size": "LARGE", "rest_hours": 48, "priority": 10},
    "BACK_HORIZONTAL": {"size": "LARGE", "rest_hours": 48, "priority": 10},
    "BACK_ISOLATION": {"size": "SMALL", "rest_hours": 24, "priority": 5},
    "REAR_DELT": {"size": "SMALL", "rest_hours": 24, "priority": 6},
    "BICEP_LONG": {"size": "SMALL", "rest_hours": 24, "priority": 5},
    "BICEP_SHORT_BRAC": {"size": "SMALL", "rest_hours": 24, "priority": 5},
    
    "QUAD_PRIMARY": {"size": "LARGE", "rest_hours": 48, "priority": 10},
    "HAMSTRING_PRIMARY": {"size": "LARGE", "rest_hours": 48, "priority": 10},
    "QUAD_SECONDARY": {"size": "LARGE", "rest_hours": 48, "priority": 8},
    "QUAD_ISOLATION": {"size": "SMALL", "rest_hours": 24, "priority": 4},
    "HAMSTRING_ISOLATION": {"size": "SMALL", "rest_hours": 24, "priority": 4},
    "CALF_ISOLATION": {"size": "SMALL", "rest_hours": 24, "priority": 3}
}

class HistoryManager:
    def __init__(self, filename='history.json'):
        self.filename = filename
        self.history = self.load_history()
        self.auto_reset_weekly()  # Auto reset check

    def load_history(self):
        """Đọc file lịch sử, nếu chưa có thì tạo dictionary rỗng"""
        if not os.path.exists(self.filename):
            return {}
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save_history(self):
        """Lưu lại lịch sử hiện tại ra file JSON"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=4)

    def auto_reset_weekly(self):
        """Xóa hits_this_week nếu chuyển sang tuần mới, giữ nguyên timestamp"""
        now = datetime.now()
        current_year, current_week, _ = now.isocalendar()
        current_week_str = f"{current_year}-W{current_week}"

        # Check old week
        last_reset_week = self.history.get("_metadata", {}).get("last_reset_week", "")
        
        if last_reset_week != current_week_str:
            print(f"🔄 Phát hiện tuần mới ({current_week_str}). Đang reset số lần tập...")
            for key, data in self.history.items():
                if key != "_metadata" and isinstance(data, dict):
                    data["hits_this_week"] = 0
                    # Keep timestamp
            
            # Update metadata
            self.history["_metadata"] = {"last_reset_week": current_week_str}
            self.save_history()

    def record_workout(self, completed_exercises):
        now_str = datetime.now().isoformat()
        
        muscles_hit_today = set()
        isolation_hits_today = set() 

        for ex in completed_exercises:
            target = ex.get("target_area")
            # Primary muscles only
            if target:
                muscles_hit_today.add(target)
                if ex.get("type_score") == 1:
                    isolation_hits_today.add(target)

        # Update history dict
        for muscle in muscles_hit_today:
            if muscle not in self.history:
                self.history[muscle] = {"hits_this_week": 0, "isolation_hits_this_week": 0, "last_trained_timestamp": ""}
            
            self.history[muscle]["hits_this_week"] += 1
            self.history[muscle]["last_trained_timestamp"] = now_str
            
            if muscle in isolation_hits_today:
                self.history[muscle]["isolation_hits_this_week"] += 1

        self.save_history()

# TEST
if __name__ == "__main__":
    hm = HistoryManager()
    
    # Simulate Bench Press
    fake_workout = [
        {
            "id": 104, 
            "name": "Flat Barbell Bench Press", 
            "target_area": "MID_CHEST", 
            "secondary_targets": ["FRONT_DELT", "TRICEP_LATERAL", "TRICEP_LONG"]
        }
    ]
    
    print("Mô phỏng: User vừa tập xong Bench Press...")
    hm.record_workout(fake_workout)
    
    print("\nDữ liệu lưu trong history.json lúc này:")
    print(json.dumps(hm.history, indent=4))