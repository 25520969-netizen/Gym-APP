import json

class ExerciseManager:
    def __init__(self, file_path):
        # 1. Đọc dữ liệu thô từ file JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.raw_exercises = data['exercises']
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file {file_path}")
            self.raw_exercises = []

        # 2. CTDL Bảng Băm (Hash Table) - Truy xuất O(1) bằng ID
        self.exercise_dict = {ex['id']: ex for ex in self.raw_exercises}

        # 3. CTDL Bảng Băm phân loại theo Target Area (Chuẩn bị cho Template Tuần 2)
        # Ví dụ: self.target_areas["UPPER_CHEST"] = [{bài 101}, {bài 102}, ...]
        self.target_areas = {}
        for ex in self.raw_exercises:
            t_area = ex['target_area']
            if t_area not in self.target_areas:
                self.target_areas[t_area] = []
            self.target_areas[t_area].append(ex)

        # 4. CTDL Đồ Thị (Adjacency List) - Dùng cho tính năng Thay thế bài
        self.graph = {ex['id']: ex['substitutes'] for ex in self.raw_exercises}

    def get_exercise_by_id(self, ex_id):
        """Trả về chi tiết một bài tập dựa vào ID (O(1))"""
        return self.exercise_dict.get(ex_id)

    def get_substitutes(self, ex_id):
        """Duyệt đồ thị để trả về danh sách các bài tập có thể thay thế"""
        sub_ids = self.graph.get(ex_id, [])
        # Trích xuất chi tiết các bài tập từ danh sách ID
        return [self.exercise_dict[sid] for sid in sub_ids if sid in self.exercise_dict]

    def get_by_target_area(self, target_area):
        """Lấy danh sách các bài tập thuộc một nhóm cơ nhỏ (O(1))"""
        return self.target_areas.get(target_area, [])
