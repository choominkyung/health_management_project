"""모듈 2: 핵심 비즈니스 로직 (CRUD, 중복 체크, BMI 재계산, 통계)"""

import csv
import os
from datetime import date

from modules.health_db import HealthManager, HealthRecord


class HealthService(HealthManager):
    """HealthManager에 CRUD/검색/통계 로직을 추가한 클래스."""

    def __init__(self, data_dir="data"):
        super().__init__()
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.json_path = os.path.join(data_dir, "health_data.json")
        self.records = self.load_json(self.json_path) if os.path.exists(self.json_path) else []

    # ---------- 저장 ----------
    def save_all(self):
        """4가지 형식 모두 동기화 저장."""
        d = self.data_dir
        ok = [self.save_json(os.path.join(d, "health_data.json")),
              self.save_csv(os.path.join(d, "health_data.csv")),
              self.save_txt(os.path.join(d, "health_data.txt")),
              self.save_pickle(os.path.join(d, "health_data.pkl"))]
        return all(ok)

    # ---------- 검증 ----------
    @staticmethod
    def validate(name, birth_year, gender, height, weight):
        """입력 검증. 문제 있으면 ValueError, 통과 시 변환된 값 반환."""
        name = str(name).strip()
        if not name:
            raise ValueError("이름을 입력하세요.")
        try:
            birth_year = int(birth_year)
            height = float(height)
            weight = float(weight)
        except (TypeError, ValueError):
            raise ValueError("생년, 키, 몸무게는 숫자로 입력하세요.")
        if not 1900 <= birth_year <= date.today().year:
            raise ValueError("생년이 올바르지 않습니다.")
        if gender not in ("남", "여"):
            raise ValueError("성별은 '남' 또는 '여'로 입력하세요.")
        if height <= 0 or weight <= 0:
            raise ValueError("키와 몸무게는 0보다 커야 합니다.")
        return name, birth_year, gender, height, weight
   # [AI 사용 기록]
    # - AI 종류: Claude 
    # - 사용 목적: 모듈2 입력값 검증 함수(validate) 작성
    # - 사용한 사람: 추민경
    # - 날짜: 2026-11-20
    #
    # [@staticmethod를 쓴 이유]
    # @는 '데코레이터'로, 바로 아래 함수의 동작 방식을 바꿔 주는 표시이다.
    # @staticmethod는 이 함수가 self(객체)나 cls(클래스)를 전혀 쓰지 않고,
    # 받은 값(name, birth_year 등)만으로 검증한다는 뜻이다.
    # 그래서 객체를 만들지 않고도 HealthService.validate(...)로 호출할 수 있고,
    # 객체 안에서는 self.validate(...)로도 호출할 수 있다.
    # 객체의 데이터(self.records 등)와 무관한 순수 검증 함수임을 코드만 봐도 알 수 있고,
    # 단독으로 테스트하기도 쉽다.
    # ---------- Create ----------
    def is_duplicate(self, name, birth_year, gender):
        return any(r.name == name and r.birth_year == birth_year and r.gender == gender
                   for r in self.records)

    def add_person(self, name, birth_year, gender, height, weight, save=True):
        """신규 등록: 검증 → 중복 체크 → ID 자동 발급 → 추가."""
        name, birth_year, gender, height, weight = self.validate(name, birth_year, gender, height, weight)
        if self.is_duplicate(name, birth_year, gender):
            raise ValueError(f"이미 등록된 사람입니다: {name}({birth_year}, {gender})")
        rec = HealthRecord(self.generate_id(), name, birth_year, gender, height, weight)
        self.add_record(rec)
        if save:
            self.save_all()
        return rec

    def import_csv(self, path):
        """CSV 일괄 등록. (추가 건수, 건너뛴 건수) 반환. id는 새로 발급."""
        added = skipped = 0
        try:
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    try:
                        self.add_person(row["name"], row["birth_year"], row["gender"],
                                        row["height"], row["weight"], save=False)
                        added += 1
                    except (ValueError, KeyError):
                        skipped += 1
        except OSError as e:
            print(f"[CSV 일괄등록 오류] {e}")
        self.save_all()
        return added, skipped

    # ---------- Retrieve ----------
    def get_all(self):
        return list(self.records)

    def get_by_id(self, rid):
        return next((r for r in self.records if r.id == rid), None)

    def search(self, name=None, rid=None, status=None):
        """이름(부분일치)·식별번호·비만도 조건으로 검색 (AND 조건)."""
        result = self.records
        if name:
            result = [r for r in result if name in r.name]
        if rid:
            result = [r for r in result if r.id == rid]
        if status:
            result = [r for r in result if r.status == status]
        return list(result)

    # ---------- Update ----------
    def update_record(self, rid, height=None, weight=None):
        """키/몸무게 수정 + BMI·비만도 자동 재계산."""
        rec = self.get_by_id(rid)
        if rec is None:
            raise ValueError(f"식별번호 {rid}를 찾을 수 없습니다.")
        try:
            h = rec.height if height is None else float(height)
            w = rec.weight if weight is None else float(weight)
        except (TypeError, ValueError):
            raise ValueError("키와 몸무게는 숫자로 입력하세요.")
        if h <= 0 or w <= 0:
            raise ValueError("키와 몸무게는 0보다 커야 합니다.")
        rec.height, rec.weight = h, w
        rec.recalculate()
        self.save_all()
        return rec

    # ---------- Delete ----------
    def delete_record(self, rid):
        rec = self.get_by_id(rid)
        if rec is None:
            return False
        self.records.remove(rec)
        self.save_all()
        return True

    # ---------- 통계 ----------
    def statistics(self):
        n = len(self.records)
        if n == 0:
            return {"count": 0, "avg_height": 0, "avg_weight": 0, "avg_bmi": 0, "status_count": {}}
        counts = {}
        for r in self.records:
            counts[r.status] = counts.get(r.status, 0) + 1
        return {
            "count": n,
            "avg_height": round(sum(r.height for r in self.records) / n, 2),
            "avg_weight": round(sum(r.weight for r in self.records) / n, 2),
            "avg_bmi": round(sum(r.bmi for r in self.records) / n, 2),
            "status_count": counts,
        }