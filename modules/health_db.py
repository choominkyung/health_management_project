
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
#  # ------------------------------------------------------------
    # [AI 사용 주석]
    # - AI 종류   : Claude
    # - 사용 목적 : HealthRecord의 to_dict() 메소드 작성 (레코드를 딕셔너리로 변환)
    # - 사용한 사람: 추민경
    # - 사용 날짜 : 2026-11-12
    # ------------------------------------------------------------
     # [왜 변환할까?]
        #   HealthRecord 객체는 파이썬 안에서만 쓰는 "객체"라서
        #   JSON/CSV 같은 파일에 그대로 쓸 수 없다.
        #   그래서 {"이름표": 값} 형태의 딕셔너리로 바꿔서 저장한다.
        #   (모듈 1 요구사항: 딕셔너리 변환 to_dict 지원)
        #
        # [변환하는 방법 3단계]
        #   1) 중괄호 { } 로 딕셔너리를 만든다.
        #   2) "이름표": 값  형태로 항목을 하나씩 적고, 항목 사이는 쉼표(,)로 구분한다.
        #   3) 값 자리에는 self.속성이름 을 쓴다.
        #      self는 "지금 이 레코드 자신"이므로, self.name은 이 사람의 이름 값을 꺼낸다.
        #
        # [변환 예시]
        #   객체 : HealthRecord(id="P2026-0001", name="홍길동", ... )
        #   결과 : {"id": "P2026-0001", "name": "홍길동", "birth_year": 1995, ... }
        #
        # [변환된 딕셔너리 사용하는 곳]
        #   - save_json(): 딕셔너리 리스트를 JSON 파일로 저장
        #   - save_csv() : 딕셔너리 한 개를 CSV 한 줄로 저장
        #   - save_txt() : 딕셔너리에서 값을 꺼내 한 줄 문자열로 저장
        #   - __eq__()   : 두 레코드의 딕셔너리를 비교해서 같은지 검증
        #
        # return : 만든 딕셔너리를 함수 밖으로 돌려준다.
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
    # ------------------------------------------------------------
    # [AI 사용 주석]
    # - AI 종류   : Claude
    # - 사용 목적 : HealthRecord의 from_dict() 메소드 설명 (@classmethod를 쓰는 이유)
    # - 사용한 사람: 추민경
    # - 사용 날짜 : 2026-11-13
    # ------------------------------------------------------------
    # [@는 무엇일까?]
    #   @ 로 시작하는 줄을 "데코레이터(decorator)"라고 한다.
    #   바로 아래에 있는 함수에 특별한 기능을 덧붙여 주는 표시이다.
    #   @classmethod 는 "이 메소드는 객체(self)가 아니라 클래스(cls)에 속한다"는 뜻이다.
    #
    # [왜 @classmethod를 쓸까?]
    #   일반 메소드는 첫 번째 자리에 self(만들어진 객체 자신)를 받는다.
    #   그런데 from_dict는 "객체를 새로 만들기 위한" 메소드라서,
    #   호출하는 시점에는 아직 객체가 존재하지 않는다.
    #   그래서 객체 없이 클래스 이름으로 바로 호출할 수 있어야 하고,
    #   이때 필요한 것이 @classmethod 이다.
    #
    #   - 일반 메소드     : rec.to_dict()               <- 객체를 먼저 만들어야 호출 가능
    #   - 클래스 메소드   : HealthRecord.from_dict(d)   <- 객체 없이 클래스로 바로 호출
    #
    #   만약 @classmethod 없이 def from_dict(self, d) 로 쓰면
    #   HealthRecord.from_dict(d) 호출 시 self 자리에 d가 들어가 버려서 오류가 난다.
    #
    # [cls는 무엇일까?]
    #   @classmethod가 붙으면 첫 번째 매개변수 자리에 self 대신 "클래스 자신"이 들어온다.
    #   관례적으로 이 매개변수 이름을 cls 라고 쓴다.
    #   그래서 cls(...) 는 HealthRecord(...) 와 같은 뜻이며, 새 객체를 만들어 돌려준다.
    #
    # [변환하는 방법]
    #   1) d["id"], d["name"] 처럼 딕셔너리에서 필요한 값을 이름표로 꺼낸다.
    #   2) 꺼낸 값을 cls(...) 에 넣어 새 HealthRecord 객체를 만든다.
    #   3) bmi와 status는 꺼내지 않는다.
    #      __init__ 안에서 height, weight로 다시 계산하기 때문이다.
    #   (CSV/TXT에서 읽은 값은 문자열이지만, __init__의 int(), float()가 숫자로 바꿔준다.)
    #
    # [변환 예시]
    #   딕셔너리 : {"id": "P2026-0001", "name": "홍길동", "birth_year": 1995, ...}
    #   결과     : HealthRecord(id="P2026-0001", name="홍길동", ...) 객체
    #
    # [사용하는 곳]
    #   - load_json(): JSON에서 읽은 딕셔너리를 객체로 복원
    #   - load_csv() : CSV 한 줄(딕셔너리)을 객체로 복원
    #   - load_txt() : TXT 한 줄을 딕셔너리로 만든 뒤 객체로 복원
    #
    # return : 딕셔너리 내용으로 새로 만든 HealthRecord 객체
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
 # ------------------------------------------------------------
    # [AI 사용 주석]
    # - AI 종류   : Claude
    # - 사용 목적 : HealthManager의 save_json() 메소드 작성 (레코드 목록을 JSON 파일로 저장)
    # - 사용한 사람: 추민경
    # - 사용 날짜 : 2026-11-13
    # ------------------------------------------------------------
    # [왜 JSON으로 저장할까?]
    #   JSON은 {"이름표": 값} 구조를 그대로 글자로 적어두는 파일 형식이다.
    #   프로그램을 꺼도 데이터가 남고, 메모장으로 열어서 내용을 눈으로 확인할 수 있다.
    #   (모듈 1 요구사항: JSON 파일 입출력 지원)
    #
    # [저장하는 방법 4단계]
    #   1) [r.to_dict() for r in self.records] 로 레코드 객체들을 딕셔너리 리스트로 바꾼다.
    #      (객체는 JSON에 바로 쓸 수 없기 때문에 to_dict()가 필요하다.)
    #   2) open(path, "w", encoding="utf-8") 로 파일을 쓰기 모드로 연다.
    #      - "w"는 쓰기 모드이며, 같은 이름의 파일이 있으면 내용을 덮어쓴다.
    #      - utf-8은 한글이 깨지지 않게 하는 인코딩이다.
    #      - with 문을 쓰면 블록이 끝날 때 파일이 자동으로 닫힌다.
    #   3) json.dump(데이터, 파일, ensure_ascii=False, indent=2) 로 파일에 쓴다.
    #      - ensure_ascii=False : 한글을 \uXXXX 같은 코드가 아닌 한글 그대로 저장
    #      - indent=2           : 들여쓰기 2칸으로 줄바꿈해서 사람이 읽기 좋게 저장
    #   4) 저장이 끝나면 True를 돌려준다.
    #
    # [예외 처리: try / except]
    #   - OSError  : 폴더가 없거나, 쓰기 권한이 없거나, 디스크 문제가 있을 때 발생
    #   - TypeError: JSON으로 바꿀 수 없는 값이 들어 있을 때 발생
    #   오류가 나도 프로그램이 멈추지 않고 오류 메시지를 출력한 뒤 False를 돌려준다.
    #
    # [저장 결과 예시 - health_data.json]
    #   [
    #     {
    #       "id": "P2026-0001",
    #       "name": "홍길동",
    #       "birth_year": 1995,
    #       ...
    #     },
    #     ...
    #   ]
    #
    # [사용하는 곳]
    #   - main(): targets 딕셔너리에 저장 함수로 등록되어 호출된다.
    #
    # return : 저장 성공하면 True, 실패하면 False (호출한 쪽에서 성공 여부 판단용)
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


