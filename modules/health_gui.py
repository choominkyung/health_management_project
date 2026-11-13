"""모듈 3: Tkinter 기반 GUI 및 이벤트 바인딩 (로직은 모듈 2 HealthService 호출)"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from modules.health_logic import HealthService

COLUMNS = [("id", "식별번호", 100), ("name", "이름", 80), ("birth_year", "생년", 60),
           ("gender", "성별", 50), ("height", "키(cm)", 70), ("weight", "몸무게(kg)", 80),
           ("bmi", "BMI", 60), ("status", "비만도", 70)]
FORMATS = {"JSON": "json", "CSV": "csv", "TXT": "txt", "PICKLE": "pkl"}


class HealthApp(tk.Tk):
    """건강관리 프로그램 메인 윈도우."""

    def __init__(self, data_dir="data"):
        super().__init__()
        self.title("BMI 건강관리 프로그램")
        self.geometry("920x600")
        self.svc = HealthService(data_dir)
        self.data_dir = data_dir
        self.vars = {k: tk.StringVar() for k in ("id", "name", "birth_year", "gender", "height", "weight")}
        self.search_name = tk.StringVar()
        self.search_status = tk.StringVar(value="전체")
        self.file_fmt = tk.StringVar(value="JSON")
        self._build_form()
        self._build_search()
        self._build_table()
        self._build_statusbar()
        self.refresh()

    # ---------- 화면 구성 ----------
    def _build_form(self):
        frm = ttk.LabelFrame(self, text="건강정보 입력")
        frm.pack(fill="x", padx=10, pady=(10, 5))
        labels = [("식별번호(자동)", "id"), ("이름", "name"), ("생년", "birth_year"),
                  ("성별", "gender"), ("키(cm)", "height"), ("몸무게(kg)", "weight")]
        for i, (text, key) in enumerate(labels):
            ttk.Label(frm, text=text).grid(row=0, column=i, padx=5, pady=(5, 0))
            if key == "gender":
                w = ttk.Combobox(frm, textvariable=self.vars[key], values=["남", "여"], width=8, state="readonly")
            else:
                w = ttk.Entry(frm, textvariable=self.vars[key], width=12,
                              state="readonly" if key == "id" else "normal")
            w.grid(row=1, column=i, padx=5, pady=5)

        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=6, pady=5)
        for text, cmd in [("등록", self.on_add), ("수정", self.on_update), ("삭제", self.on_delete),
                          ("입력 초기화", self.clear_form), ("CSV 일괄등록", self.on_import)]:
            ttk.Button(btns, text=text, command=cmd).pack(side="left", padx=4)

    def _build_search(self):
        frm = ttk.LabelFrame(self, text="검색 / 파일")
        frm.pack(fill="x", padx=10, pady=5)
        ttk.Label(frm, text="이름").pack(side="left", padx=5)
        ttk.Entry(frm, textvariable=self.search_name, width=12).pack(side="left")
        ttk.Label(frm, text="비만도").pack(side="left", padx=5)
        ttk.Combobox(frm, textvariable=self.search_status, width=8, state="readonly",
                     values=["전체", "저체중", "정상", "과체중", "비만"]).pack(side="left")
        ttk.Button(frm, text="검색", command=self.on_search).pack(side="left", padx=4)
        ttk.Button(frm, text="전체보기", command=self.on_show_all).pack(side="left", padx=4)
        ttk.Button(frm, text="통계", command=self.on_stats).pack(side="left", padx=4)

        ttk.Combobox(frm, textvariable=self.file_fmt, width=8, state="readonly",
                     values=list(FORMATS)).pack(side="right", padx=5)
        ttk.Button(frm, text="불러오기", command=self.on_load).pack(side="right", padx=2)
        ttk.Button(frm, text="저장", command=self.on_save).pack(side="right", padx=2)
        ttk.Label(frm, text="파일형식").pack(side="right", padx=5)

    def _build_table(self):
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(frm, columns=[c[0] for c in COLUMNS], show="headings")
        for key, text, width in COLUMNS:
            self.tree.heading(key, text=text)
            self.tree.column(key, width=width, anchor="center")
        sb = ttk.Scrollbar(frm, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _build_statusbar(self):
        self.status_label = ttk.Label(self, anchor="w", relief="sunken")
        self.status_label.pack(fill="x", side="bottom")

    # ---------- 공통 ----------
    def refresh(self, records=None):
        """표 갱신 (records가 없으면 전체)."""
        self.tree.delete(*self.tree.get_children())
        for r in (self.svc.get_all() if records is None else records):
            self.tree.insert("", "end", iid=r.id, values=(r.id, r.name, r.birth_year, r.gender,
                                                         r.height, r.weight, r.bmi, r.status))
        s = self.svc.statistics()
        self.status_label.config(text=f" 총 {s['count']}명 | 평균 키 {s['avg_height']}cm | "
                                      f"평균 몸무게 {s['avg_weight']}kg | 평균 BMI {s['avg_bmi']}")

    def clear_form(self):
        for v in self.vars.values():
            v.set("")
        self.tree.selection_remove(self.tree.selection())

    def _form(self, key):
        return self.vars[key].get().strip()

    # ---------- 이벤트 ----------
    def on_select(self, _event=None):
        """표의 행 클릭 시 입력 폼 자동 채움."""
        sel = self.tree.selection()
        if not sel:
            return
        r = self.svc.get_by_id(sel[0])
        if r:
            for k in self.vars:
                self.vars[k].set(str(getattr(r, k)))

    def on_add(self):
        try:
            r = self.svc.add_person(self._form("name"), self._form("birth_year"), self._form("gender"),
                                    self._form("height"), self._form("weight"))
        except ValueError as e:
            messagebox.showwarning("입력 오류", str(e))
            return
        messagebox.showinfo("등록 완료", f"{r.name}님이 {r.id}로 등록되었습니다.")
        self.clear_form()
        self.refresh()

    def on_update(self):
        rid = self._form("id")
        if not rid:
            messagebox.showwarning("선택 필요", "수정할 행을 먼저 선택하세요.")
            return
        try:
            r = self.svc.update_record(rid, self._form("height"), self._form("weight"))
        except ValueError as e:
            messagebox.showwarning("입력 오류", str(e))
            return
        messagebox.showinfo("수정 완료", f"BMI {r.bmi} ({r.status})로 갱신되었습니다.")
        self.refresh()
        self.tree.selection_set(rid)

    def on_delete(self):
        rid = self._form("id")
        if not rid:
            messagebox.showwarning("선택 필요", "삭제할 행을 먼저 선택하세요.")
            return
        if not messagebox.askyesno("삭제 확인", f"{rid}을(를) 삭제할까요?"):
            return
        if self.svc.delete_record(rid):
            messagebox.showinfo("삭제 완료", "삭제되었습니다.")
            self.clear_form()
            self.refresh()
        else:
            messagebox.showerror("오류", "삭제할 수 없습니다.")

    def on_search(self):
        status = self.search_status.get()
        result = self.svc.search(name=self.search_name.get().strip() or None,
                                 status=None if status == "전체" else status)
        self.refresh(result)

    def on_show_all(self):
        self.search_name.set("")
        self.search_status.set("전체")
        self.refresh()

    def on_import(self):
        path = filedialog.askopenfilename(title="CSV 선택", filetypes=[("CSV", "*.csv"), ("모든 파일", "*.*")])
        if not path:
            return
        added, skipped = self.svc.import_csv(path)
        messagebox.showinfo("일괄등록 완료", f"추가 {added}건, 건너뜀(중복/오류) {skipped}건")
        self.refresh()

    def on_stats(self):
        s = self.svc.statistics()
        counts = "\n".join(f"  {k}: {v}명" for k, v in s["status_count"].items()) or "  (없음)"
        messagebox.showinfo("통계", f"총 인원: {s['count']}명\n평균 키: {s['avg_height']}cm\n"
                                    f"평균 몸무게: {s['avg_weight']}kg\n평균 BMI: {s['avg_bmi']}\n\n비만도별:\n{counts}")

    def _path(self):
        return os.path.join(self.data_dir, f"health_data.{FORMATS[self.file_fmt.get()]}")

    def on_save(self):
        saver = {"json": self.svc.save_json, "csv": self.svc.save_csv,
                 "txt": self.svc.save_txt, "pkl": self.svc.save_pickle}[FORMATS[self.file_fmt.get()]]
        if saver(self._path()):
            messagebox.showinfo("저장 완료", f"{self._path()} 에 저장했습니다.")
        else:
            messagebox.showerror("저장 실패", "파일을 저장하지 못했습니다.")

    def on_load(self):
        if not os.path.exists(self._path()):
            messagebox.showwarning("파일 없음", f"{self._path()} 파일이 없습니다.")
            return
        loader = {"json": self.svc.load_json, "csv": self.svc.load_csv,
                  "txt": self.svc.load_txt, "pkl": self.svc.load_pickle}[FORMATS[self.file_fmt.get()]]
        self.svc.records = loader(self._path())
        self.refresh()
        messagebox.showinfo("불러오기 완료", f"{len(self.svc.records)}건을 불러왔습니다.")


def run():
    HealthApp().mainloop()