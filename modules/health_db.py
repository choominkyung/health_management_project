# ============================================================
# [AI 사용 주석]
# - AI 종류   : Claude (Anthropic)
# - 사용 목적 : 모듈 1(health_db.py) 코드 작성 (데이터 구조화 및 4종 파일 I/O)
# - 프롬프트  : "지정프로젝트 요구사항(BMI 건강관리 프로그램)에 맞춰 11주차 모듈 1 코드를
#               작성해줘. HealthRecord/관리자 클래스, JSON·CSV·TXT·Pickle 저장/로드,
#               저장 전후 검증 main() 포함"
# - 사용한 사람: (본인 이름 기입)
# - 사용 날짜 : 2026-11-12
# ============================================================
"""모듈 1: 건강정보 레코드 모델링 및 파일 입출력 (JSON, CSV, TXT, Pickle)"""

import csv
import json
import os
import pickle
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

FIELDS = ["id", "name", "birth_year", "gender", "height", "weight", "bmi", "status"]


def calc_bmi(height_cm, weight_kg):
    """BMI 계산 (소수 둘째 자리 반올림)."""
    m = height_cm / 100
    return round(weight_kg / (m * m), 2)


def judge_status(bmi):
    """BMI 수치로 비만도 판정 (저체중/정상/과체중/비만)."""
    if bmi < 18.5:
        return "저체중"
    if bmi < 23:
        return "정상"
    if bmi < 25:
        return "과체중"
    return "비만"


class HealthRecord:
    """한 사람의 건강정보 레코드."""

    def __init__(self, id, name, birth_year, gender, height, weight):
        self.id = id
        self.name = name
        self.birth_year = int(birth_year)
        self.gender = gender
        self.height = float(height)
        self.weight = float(weight)
        self.bmi = calc_bmi(self.height, self.weight)
        self.status = judge_status(self.bmi)

    def to_dict(self):
        """레코드를 딕셔너리로 변환."""
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "bmi": self.bmi,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d):
        """딕셔너리로부터 레코드 생성 (bmi/status는 다시 계산)."""
        return cls(d["id"], d["name"], d["birth_year"], d["gender"],
                   d["height"], d["weight"])

    def __eq__(self, other):
        return isinstance(other, HealthRecord) and self.to_dict() == other.to_dict()

    def __repr__(self):
        return (f"HealthRecord(id={self.id!r}, name={self.name!r}, "
                f"height={self.height}, weight={self.weight})")


class HealthManager:
    """건강정보 레코드 목록 관리 및 파일 저장/로드."""

    def __init__(self, year=2026):
        self.records = []
        self.year = year
        self._seq = 0

    def generate_id(self):
        """고유 식별번호 자동 생성 (예: P2026-0001)."""
        existing = {r.id for r in self.records}
        while True:
            self._seq += 1
            new_id = f"P{self.year}-{self._seq:04d}"
            if new_id not in existing:
                return new_id

    def add_record(self, name, birth_year, gender, height, weight):
        """신규 레코드를 만들어 목록에 추가하고 반환."""
        rec = HealthRecord(self.generate_id(), name, birth_year, gender, height, weight)
        self.records.append(rec)
        return rec

    def print_all(self, title="건강정보 목록", records=None):
        """레코드 목록을 표 형태로 출력."""
        records = self.records if records is None else records
        print(f"\n=== {title} ({len(records)}건) ===")
        print(f"{'ID':<12}{'이름':<8}{'생년':<6}{'성별':<4}{'키':<7}{'몸무게':<7}{'BMI':<7}{'상태'}")
        for r in records:
            print(f"{r.id:<12}{r.name:<8}{r.birth_year:<6}{r.gender:<4}"
                  f"{r.height:<7}{r.weight:<7}{r.bmi:<7}{r.status}")

    # ---------- JSON ----------
    def save_json(self, path):
        """JSON 파일로 저장. 성공 여부 반환."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump([r.to_dict() for r in self.records], f,
                          ensure_ascii=False, indent=2)
            return True
        except (OSError, TypeError) as e:
            print(f"[오류] JSON 저장 실패: {e}")
            return False

    def load_json(self, path):
        """JSON 파일 로드. 실패 시 빈 리스트 반환."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return [HealthRecord.from_dict(d) for d in json.load(f)]
        except (OSError, ValueError, KeyError, TypeError) as e:
            print(f"[오류] JSON 로드 실패: {e}")
            return []

    # ---------- CSV ----------
    def save_csv(self, path):
        """CSV 파일로 저장 (첫 행 헤더). 성공 여부 반환."""
        try:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()
                for r in self.records:
                    w.writerow(r.to_dict())
            return True
        except OSError as e:
            print(f"[오류] CSV 저장 실패: {e}")
            return False

    def load_csv(self, path):
        """CSV 파일 로드. 실패 시 빈 리스트 반환."""
        try:
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                return [HealthRecord.from_dict(row) for row in csv.DictReader(f)]
        except (OSError, ValueError, KeyError, TypeError) as e:
            print(f"[오류] CSV 로드 실패: {e}")
            return []

    # ---------- TXT ----------
    def save_txt(self, path):
        """쉼표 구분 한 줄 문자열 형태의 TXT로 저장. 성공 여부 반환."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                for r in self.records:
                    d = r.to_dict()
                    f.write(",".join(str(d[k]) for k in FIELDS) + "\n")
            return True
        except OSError as e:
            print(f"[오류] TXT 저장 실패: {e}")
            return False

    def load_txt(self, path):
        """TXT 파일 로드. 실패 시 빈 리스트 반환."""
        try:
            result = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    d = dict(zip(FIELDS, line.split(",")))
                    result.append(HealthRecord.from_dict(d))
            return result
        except (OSError, ValueError, KeyError, TypeError) as e:
            print(f"[오류] TXT 로드 실패: {e}")
            return []

    # ---------- Pickle ----------
    def save_pickle(self, path):
        """Pickle(이진) 파일로 객체 목록 통째로 저장. 성공 여부 반환."""
        try:
            with open(path, "wb") as f:
                pickle.dump(self.records, f)
            return True
        except (OSError, pickle.PickleError) as e:
            print(f"[오류] Pickle 저장 실패: {e}")
            return False

    def load_pickle(self, path):
        """Pickle 파일 로드. 실패 시 빈 리스트 반환."""
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except (OSError, pickle.PickleError, EOFError, AttributeError) as e:
            print(f"[오류] Pickle 로드 실패: {e}")
            return []


def main():
    """샘플 데이터 입력 -> 4종 파일 저장 -> 각각 로드 -> 원본과 일치 검증."""
    os.makedirs(DATA_DIR, exist_ok=True)

    mgr = HealthManager()
    mgr.add_record("홍길동", 1995, "남", 175.0, 72.5)
    mgr.add_record("김영희", 1998, "여", 162.0, 52.0)
    mgr.add_record("이철수", 2001, "남", 180.0, 62.0)
    mgr.add_record("박민지", 1990, "여", 158.0, 75.0)
    mgr.add_record("최수진", 2003, "여", 165.0, 45.0)
    mgr.print_all("원본 데이터")

    targets = {
        "JSON":   ("health_data.json", mgr.save_json,   mgr.load_json),
        "CSV":    ("health_data.csv",  mgr.save_csv,    mgr.load_csv),
        "TXT":    ("health_data.txt",  mgr.save_txt,    mgr.load_txt),
        "PICKLE": ("health_data.pkl",  mgr.save_pickle, mgr.load_pickle),
    }

    print("\n--- 파일 저장 / 로드 / 검증 ---")
    all_ok = True
    for name, (fname, save, load) in targets.items():
        path = os.path.join(DATA_DIR, fname)
        saved = save(path)
        loaded = load(path)
        mgr.print_all(f"{name} 로드 결과", loaded)
        ok = saved and loaded == mgr.records
        all_ok = all_ok and ok
        print(f"[{name}] 저장: {'성공' if saved else '실패'} / 원본과 일치: {'O' if ok else 'X'}")

    print("\n최종 검증 결과:", "모든 파일 형식 일치 ✔" if all_ok else "불일치 발견 ✘")


if __name__ == "__main__":
    sys.path.insert(0, BASE_DIR)
    from modules.health_db import main as _main
    _main()


