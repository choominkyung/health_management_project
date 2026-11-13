"""실행 진입점: 모듈1·2 콘솔 테스트 (모듈3 완성 후 GUI 실행으로 교체)"""
# [AI 사용 기록] AI: Claude / 목적: 모듈2 콘솔 테스트 작성 / 프롬프트: "지정프로젝트 모듈2 작성" / 사용자: (이름) / 날짜: 2026-11-13
import os
import shutil

from modules.health_logic import HealthService


def main():
    shutil.rmtree("data", ignore_errors=True)   # 테스트용 초기화
    svc = HealthService("data")

    # 1) 등록 + ID 자동발급
    svc.add_person("홍길동", 1995, "남", 175.0, 72.5)
    svc.add_person("김영희", 1998, "여", 162.0, 52.0)
    svc.add_person("이철수", 2000, "남", 180.0, 95.0)
    svc.print_all("등록 후")

    # 2) 중복 체크 / 입력 검증
    for args in [("홍길동", 1995, "남", 175, 72.5), ("박민수", 1999, "남", "abc", 70), ("최수진", 2001, "여", 160, -5)]:
        try:
            svc.add_person(*args)
        except ValueError as e:
            print("[예외 처리 OK]", e)

    # 3) CSV 일괄 등록
    with open("sample_import.csv", "w", encoding="utf-8", newline="") as f:
        f.write("name,birth_year,gender,height,weight\n정하늘,1999,여,165,48\n홍길동,1995,남,175,72.5\n")
    print("일괄등록(추가, 건너뜀):", svc.import_csv("sample_import.csv"))

    # 4) 검색
    print("\n[이름 '김' 검색]", [str(r) for r in svc.search(name="김")])
    print("[비만 검색]", [str(r) for r in svc.search(status="비만")])

    # 5) 수정 + BMI 재계산
    before = svc.get_by_id("P2026-0003").bmi
    rec = svc.update_record("P2026-0003", weight=75)
    print(f"\n[수정] BMI {before} -> {rec.bmi}, 상태 {rec.status}")

    # 6) 삭제
    print("[삭제]", svc.delete_record("P2026-0002"), "/ 없는 ID 삭제:", svc.delete_record("P9999-0000"))
    svc.print_all("최종")

    # 7) 통계
    print("\n[통계]", svc.statistics())

    # 8) 저장 파일 4종 일치 검증
    d = "data"
    loaders = {"json": svc.load_json, "csv": svc.load_csv, "txt": svc.load_txt, "pkl": svc.load_pickle}
    for ext, loader in loaders.items():
        loaded = loader(os.path.join(d, f"health_data.{ext}"))
        print(f"{ext.upper():7} 일치 여부:", loaded == svc.records)


if __name__ == "__main__":
    main()