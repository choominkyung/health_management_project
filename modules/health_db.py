"""모듈 1: 데이터 구조화(HealthRecord) 및 파일 I/O (JSON, CSV, TXT, Pickle)"""

import csv
import json
import os
import pickle
from dataclasses import dataclass, asdict

FIELDS = ["id", "name", "birth_year", "gender", "height", "weight", "bmi", "status"]


def calc_bmi(height_cm, weight_kg):
    """BMI = 체중 / (키(m))^2, 소수 둘째 자리 반올림."""
    return round(weight_kg / ((height_cm / 100) ** 2), 2)


def judge_status(bmi):
    """BMI 수치로 비만도 판정 (저체중/정상/과체중/비만)."""
    if bmi < 18.5:
        return "저체중"
    if bmi < 23:
        return "정상"
    if bmi < 25:
        return "과체중"
    return "비만"


@dataclass
class HealthRecord:
    """한 사람의 건강정보 레코드."""
    id: str
    name: str
    birth_year: int
    gender: str
    height: float
    weight: float
    bmi: float = 0.0
    status: str = ""

    def __post_init__(self):
        self.recalculate()

    def recalculate(self):
        """키/몸무게 기준으로 BMI와 비만도 재계산."""
        self.bmi = calc_bmi(self.height, self.weight)
        self.status = judge_status(self.bmi)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(id=str(d["id"]), name=str(d["name"]), birth_year=int(d["birth_year"]),
                   gender=str(d["gender"]), height=float(d["height"]), weight=float(d["weight"]))

    def __str__(self):
        return (f"{self.id} | {self.name} | {self.birth_year} | {self.gender} | "
                f"{self.height}cm | {self.weight}kg | BMI {self.bmi} | {self.status}")


class HealthManager:
    """건강정보 객체 목록 관리 + 4가지 파일 저장/로드."""

    def __init__(self):
        self.records = []

    def add_record(self, record):
        self.records.append(record)

    def generate_id(self, year=2026):
        """P2026-0001 형식의 고유 식별번호 발급."""
        prefix = f"P{year}-"
        nums = [int(r.id.split("-")[1]) for r in self.records if r.id.startswith(prefix)]
        return f"{prefix}{(max(nums) + 1 if nums else 1):04d}"

    def print_all(self, title="목록"):
        print(f"\n===== {title} ({len(self.records)}건) =====")
        for r in self.records:
            print(r)

    # ---------- JSON ----------
    def save_json(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump([r.to_dict() for r in self.records], f, ensure_ascii=False, indent=2)
            return True
        except (OSError, TypeError) as e:
            print(f"[JSON 저장 오류] {e}")
            return False
   # [AI 사용 기록]
    # - AI 종류: Claude 
    # - 사용 목적: 모듈1 JSON 파일 저장(save_json) / 불러오기(load_json) 메소드 작성
    # - 사용한 사람: 추민경
    # - 날짜: 2026-11-20
    #
    # [코드 설명]
    # save_json: 레코드 객체 목록을 JSON 파일로 저장한다.
    #  - open(path, "w", encoding="utf-8"): 쓰기 모드로 파일을 연다. utf-8이라 한글이 깨지지 않는다.
    #  - with문: 블록이 끝나면 파일을 자동으로 닫아 준다.
    #  - [r.to_dict() for r in self.records]: 객체(HealthRecord)는 JSON으로 바로 못 바꾸므로
    #    각 객체를 딕셔너리로 바꾼 리스트를 만든다.
    #  - json.dump(..., ensure_ascii=False, indent=2): 리스트를 파일에 쓴다.
    #    ensure_ascii=False는 한글을 그대로 저장하고, indent=2는 보기 좋게 들여쓴다.
    #  - try-except: 파일 권한 문제나 디스크 오류(OSError), 변환 불가 값(TypeError)이 생겨도
    #    프로그램이 죽지 않고 오류를 출력한 뒤 False를 반환한다. 성공하면 True를 반환한다.
    def load_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return [HealthRecord.from_dict(d) for d in json.load(f)]
        except (OSError, ValueError, KeyError, TypeError) as e:
            print(f"[JSON 로드 오류] {e}")
            return []

    # ---------- CSV ----------
    def save_csv(self, path):
        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()
                for r in self.records:
                    w.writerow(r.to_dict())
            return True
        except OSError as e:
            print(f"[CSV 저장 오류] {e}")
            return False

    def load_csv(self, path):
        try:
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                return [HealthRecord.from_dict(row) for row in csv.DictReader(f)]
        except (OSError, ValueError, KeyError) as e:
            print(f"[CSV 로드 오류] {e}")
            return []

    # ---------- TXT ----------
    def save_txt(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                for r in self.records:
                    d = r.to_dict()
                    f.write(",".join(str(d[k]) for k in FIELDS) + "\n")
            return True
        except OSError as e:
            print(f"[TXT 저장 오류] {e}")
            return False

    def load_txt(self, path):
        result = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    result.append(HealthRecord.from_dict(dict(zip(FIELDS, parts))))
            return result
        except (OSError, ValueError, KeyError) as e:
            print(f"[TXT 로드 오류] {e}")
            return []

    # ---------- Pickle ----------
    def save_pickle(self, path):
        try:
            with open(path, "wb") as f:
                pickle.dump(self.records, f)
            return True
        except (OSError, pickle.PicklingError) as e:
            print(f"[Pickle 저장 오류] {e}")
            return False

    def load_pickle(self, path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except (OSError, pickle.UnpicklingError, EOFError, AttributeError) as e:
            print(f"[Pickle 로드 오류] {e}")
            return []