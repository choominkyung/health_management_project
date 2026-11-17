# health_db.py : 모듈 1 - 데이터 구조(레코드)와 파일 입출력

import os
import json
import csv
import pickle
from datetime import datetime

# data 폴더 위치 (modules 폴더의 바로 위에 있는 data 폴더)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# 파일에 저장할 항목 이름 (순서 중요)
FIELDS = ["id", "name", "birth_year", "gender", "height", "weight", "bmi", "status"]

# 파일 형식별 확장자
EXTENSIONS = {"json": "json", "csv": "csv", "txt": "txt", "pickle": "pkl"}


def calc_bmi(height, weight):
    """BMI를 계산해서 소수 둘째 자리까지 반올림해 돌려준다.

    height: 키(cm), weight: 몸무게(kg)
    공식: 몸무게 / (키(m) * 키(m))
    """
    return round(weight / ((height / 100) ** 2), 2)


def get_status(bmi):
    """BMI 수치로 비만도 판정 결과(문자열)를 돌려준다."""
    if bmi < 18.5:
        return "저체중"
    elif bmi < 23:
        return "정상"
    elif bmi < 25:
        return "과체중"
    else:
        return "비만"


class HealthRecord:
    """사람 한 명의 건강정보를 담는 클래스."""

    def __init__(self, id, name, birth_year, gender, height, weight):
        self.id = id
        self.name = name
        self.birth_year = int(birth_year)
        self.gender = gender
        self.height = float(height)
        self.weight = float(weight)
        self.bmi = 0.0
        self.status = ""
        self.update_bmi()

    def update_bmi(self):
        """키/몸무게로 BMI와 비만도를 다시 계산한다."""
        self.bmi = calc_bmi(self.height, self.weight)
        self.status = get_status(self.bmi)

    def to_dict(self):
        """레코드를 딕셔너리로 바꾼다 (JSON, CSV 저장에 사용)."""
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
#사용한 AI : chapgpt
# 사용한 목적 : 정적 메서드로 만들기 위해서
#사용한 사람 : 추민경
# 사용한 날짜 : 2026-11-17
    @staticmethod
    def from_dict(d):
        """딕셔너리를 HealthRecord 객체로 바꾼다. (BMI는 다시 계산)"""
        return HealthRecord(
            d["id"], d["name"], d["birth_year"], d["gender"], d["height"], d["weight"]
        )

    def __repr__(self):
        return (f'HealthRecord(id="{self.id}", name="{self.name}", '
                f'height={self.height}, weight={self.weight})')


def read_csv_rows(path):
    """CSV 파일을 읽어 딕셔너리 리스트로 돌려준다. 실패하면 빈 리스트."""
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as e:
        print("CSV 읽기 오류:", e)
        return []


class HealthManager:
    """레코드 목록을 들고 있으면서 파일로 저장/불러오기를 하는 클래스."""

    def __init__(self):
        self.records = []  # HealthRecord 객체들의 리스트

    # ---------- 식별번호 ----------
    def make_id(self):
        """고유한 식별번호를 만든다. 예) P2026-0001"""
        max_no = 0
        for r in self.records:
            try:
                no = int(r.id.split("-")[1])
                if no > max_no:
                    max_no = no
            except (IndexError, ValueError):
                pass
        return f"P{datetime.now().year}-{max_no + 1:04d}"

    # ---------- 파일 경로 ----------
    def get_path(self, fmt):
        return os.path.join(DATA_DIR, "health_data." + EXTENSIONS[fmt])

    # ---------- 저장 ----------
    def save(self, fmt="json"):
        """현재 레코드들을 fmt 형식(json/csv/txt/pickle)으로 저장. 성공하면 True."""
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            path = self.get_path(fmt)
            if fmt == "json":
                with open(path, "w", encoding="utf-8") as f:
                    json.dump([r.to_dict() for r in self.records], f,
                              ensure_ascii=False, indent=4)
            elif fmt == "csv":
                with open(path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=FIELDS)
                    writer.writeheader()
                    for r in self.records:
                        writer.writerow(r.to_dict())
            elif fmt == "txt":
                with open(path, "w", encoding="utf-8") as f:
                    for r in self.records:
                        d = r.to_dict()
                        f.write(",".join(str(d[k]) for k in FIELDS) + "\n")
            elif fmt == "pickle":
                with open(path, "wb") as f:
                    pickle.dump(self.records, f)
            else:
                return False
            return True
        except Exception as e:
            print("저장 오류:", e)
            return False

    # ---------- 불러오기 ----------
    def load(self, fmt="json"):
        """fmt 형식 파일에서 레코드를 불러온다. 성공하면 True.

        파일이 없거나 깨졌으면 False (기존 데이터는 그대로 둔다).
        """
        try:
            path = self.get_path(fmt)
            new_records = []
            if fmt == "json":
                with open(path, "r", encoding="utf-8") as f:
                    for d in json.load(f):
                        new_records.append(HealthRecord.from_dict(d))
            elif fmt == "csv":
                for d in read_csv_rows(path):
                    new_records.append(HealthRecord.from_dict(d))
            elif fmt == "txt":
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line == "":
                            continue
                        parts = line.split(",")
                        d = dict(zip(FIELDS, parts))
                        new_records.append(HealthRecord.from_dict(d))
            elif fmt == "pickle":
                with open(path, "rb") as f:
                    new_records = pickle.load(f)
            else:
                return False
            self.records = new_records
            return True
        except Exception as e:
            print("불러오기 오류:", e)
            return False