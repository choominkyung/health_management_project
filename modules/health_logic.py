# health_logic.py : 모듈 2 - 핵심 로직 (CRUD, 검색, 통계)
#
# [AI 사용 기록]
# AI 종류 : Claude (Anthropic)
# 사용 목적 : 모듈 2(health_logic.py) 코드 작성
# 프롬프트 : (실제로 입력한 프롬프트를 여기에 적으세요)
# 사용자/날짜 : (본인 이름) / 2026-11-16

from datetime import datetime
from modules.health_db import HealthManager, HealthRecord, read_csv_rows


class HealthLogic(HealthManager):
    """HealthManager(저장/불러오기)에 등록·검색·수정·삭제·통계 기능을 더한 클래스."""

    def __init__(self):
        super().__init__()
        self.fmt = "json"       # 현재 자동 저장에 쓰는 파일 형식
        self.load(self.fmt)     # 시작할 때 저장된 파일을 불러옴

    # ---------- 입력값 검사 ----------
    def check_input(self, name, birth_year, gender, height, weight):
        """입력값을 검사하고 (이름, 생년, 성별, 키, 몸무게)로 바꿔 돌려준다.

        잘못된 값이면 ValueError(안내 메시지)를 일으킨다.
        """
        name = str(name).strip()
        if name == "":
            raise ValueError("이름을 입력하세요.")
        if "," in name:
            raise ValueError("이름에 쉼표(,)는 쓸 수 없습니다.")

        try:
            birth_year = int(birth_year)
        except ValueError:
            raise ValueError("생년은 숫자로 입력하세요. 예) 1995")
        if birth_year < 1900 or birth_year > datetime.now().year:
            raise ValueError("생년이 올바르지 않습니다.")

        if gender not in ("남", "여"):
            raise ValueError("성별은 '남' 또는 '여'를 선택하세요.")

        try:
            height = float(height)
            weight = float(weight)
        except ValueError:
            raise ValueError("키와 몸무게는 숫자로 입력하세요.")
        if height <= 0 or weight <= 0:
            raise ValueError("키와 몸무게는 0보다 커야 합니다.")

        return name, birth_year, gender, height, weight

    # ---------- 중복 체크 ----------
    def is_duplicate(self, name, birth_year, gender, skip_id=None):
        """이름+생년+성별이 같은 사람이 이미 있으면 True. (skip_id는 검사에서 뺄 식별번호)"""
        for r in self.records:
            if r.id == skip_id:
                continue
            if r.name == name and r.birth_year == birth_year and r.gender == gender:
                return True
        return False

    # ---------- 등록 (Create) ----------
    def add_record(self, name, birth_year, gender, height, weight):
        """새 레코드를 등록한다. (성공 여부, 메시지)를 돌려준다."""
        try:
            name, birth_year, gender, height, weight = self.check_input(
                name, birth_year, gender, height, weight)
        except ValueError as e:
            return False, str(e)

        if self.is_duplicate(name, birth_year, gender):
            return False, "이미 등록된 사람입니다. (이름·생년·성별 동일)"

        new_id = self.make_id()
        self.records.append(HealthRecord(new_id, name, birth_year, gender, height, weight))
        self.save(self.fmt)
        return True, f"등록되었습니다. (식별번호: {new_id})"

    def add_from_csv(self, path):
        """CSV 파일의 여러 사람을 한꺼번에 등록한다. (성공 여부, 메시지)"""
        rows = read_csv_rows(path)
        if len(rows) == 0:
            return False, "읽을 수 있는 데이터가 없습니다. (파일 형식을 확인하세요)"

        added = 0
        skipped = 0
        for row in rows:
            try:
                name, birth_year, gender, height, weight = self.check_input(
                    row.get("name", ""), row.get("birth_year", ""), row.get("gender", ""),
                    row.get("height", ""), row.get("weight", ""))
            except ValueError:
                skipped += 1
                continue
            if self.is_duplicate(name, birth_year, gender):
                skipped += 1
                continue
            new_id = self.make_id()   # 식별번호는 항상 새로 발급
            self.records.append(HealthRecord(new_id, name, birth_year, gender, height, weight))
            added += 1

        self.save(self.fmt)
        return True, f"{added}명 등록, {skipped}명 제외(오류 또는 중복)"

    # ---------- 조회 (Retrieve) ----------
    def get_all(self):
        return self.records

    def get_record(self, record_id):
        """식별번호로 레코드 한 개를 찾는다. 없으면 None."""
        for r in self.records:
            if r.id == record_id:
                return r
        return None

    def search(self, keyword="", status="전체"):
        """이름 또는 식별번호에 keyword가 들어 있고, 비만도가 status인 레코드를 찾는다."""
        keyword = keyword.strip()
        result = []
        for r in self.records:
            if keyword != "" and keyword not in r.name and keyword not in r.id:
                continue
            if status != "전체" and r.status != status:
                continue
            result.append(r)
        return result

    # ---------- 수정 (Update) ----------
    def update_record(self, record_id, name, birth_year, gender, height, weight):
        """레코드를 수정하고 BMI를 다시 계산한다. (성공 여부, 메시지)"""
        record = self.get_record(record_id)
        if record is None:
            return False, "수정할 사람을 표에서 먼저 선택하세요."
        try:
            name, birth_year, gender, height, weight = self.check_input(
                name, birth_year, gender, height, weight)
        except ValueError as e:
            return False, str(e)

        if self.is_duplicate(name, birth_year, gender, skip_id=record_id):
            return False, "같은 정보를 가진 다른 사람이 이미 있습니다."

        record.name = name
        record.birth_year = birth_year
        record.gender = gender
        record.height = height
        record.weight = weight
        record.update_bmi()          # BMI·비만도 자동 재계산
        self.save(self.fmt)
        return True, f"수정되었습니다. (BMI {record.bmi}, {record.status})"

    # ---------- 삭제 (Delete) ----------
    def delete_record(self, record_id):
        """레코드를 삭제한다. (성공 여부, 메시지)"""
        record = self.get_record(record_id)
        if record is None:
            return False, "삭제할 사람을 표에서 먼저 선택하세요."
        self.records.remove(record)
        self.save(self.fmt)
        return True, "삭제되었습니다."

    # ---------- 통계 ----------
    def get_statistics(self):
        """인원수, 평균 키/몸무게/BMI, 비만도별 인원수를 딕셔너리로 돌려준다."""
        count = len(self.records)
        counts = {"저체중": 0, "정상": 0, "과체중": 0, "비만": 0}
        if count == 0:
            return {"count": 0, "avg_height": 0, "avg_weight": 0, "avg_bmi": 0,
                    "status_counts": counts}

        total_h = total_w = total_b = 0
        for r in self.records:
            total_h += r.height
            total_w += r.weight
            total_b += r.bmi
            counts[r.status] += 1
        return {
            "count": count,
            "avg_height": round(total_h / count, 2),
            "avg_weight": round(total_w / count, 2),
            "avg_bmi": round(total_b / count, 2),
            "status_counts": counts,
        }


# ---------- 콘솔 테스트 (12주차용) ----------
# 프로젝트 루트 폴더에서  python -m modules.health_logic  로 실행
if __name__ == "__main__":
    logic = HealthLogic()
    while True:
        print("\n1.등록 2.전체목록 3.검색 4.수정 5.삭제 6.통계 0.종료")
        menu = input("선택: ")
        if menu == "1":
            print(logic.add_record(input("이름: "), input("생년: "), input("성별(남/여): "),
                                   input("키(cm): "), input("몸무게(kg): ")))
        elif menu == "2":
            for r in logic.get_all():
                print(r.to_dict())
        elif menu == "3":
            for r in logic.search(input("이름/식별번호: ")):
                print(r.to_dict())
        elif menu == "4":
            print(logic.update_record(input("식별번호: "), input("이름: "), input("생년: "),
                                      input("성별(남/여): "), input("키(cm): "), input("몸무게(kg): ")))
        elif menu == "5":
            print(logic.delete_record(input("식별번호: ")))
        elif menu == "6":
            print(logic.get_statistics())
        elif menu == "0":
            break