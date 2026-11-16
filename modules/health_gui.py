# health_gui.py : 모듈 3 - tkinter 화면(GUI)과 이벤트 처리


import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from modules.health_logic import HealthLogic


class HealthApp:
    """건강관리 프로그램의 화면 클래스."""

    def __init__(self):
        self.logic = HealthLogic()
        self.root = tk.Tk()
        self.root.title("BMI 건강관리 프로그램")
        self.root.geometry("900x650")

        self.make_form()
        self.make_buttons()
        self.make_search()
        self.make_table()
        self.make_stats()
        self.refresh_table()

    # ---------- 화면 만들기 ----------
    def make_form(self):
        """입력 폼 (식별번호, 이름, 생년, 성별, 키, 몸무게)"""
        frame = tk.LabelFrame(self.root, text="건강정보 입력", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.birth_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.weight_var = tk.StringVar()

        tk.Label(frame, text="식별번호").grid(row=0, column=0, padx=5, pady=3)
        tk.Entry(frame, textvariable=self.id_var, state="readonly", width=14).grid(row=0, column=1)
        tk.Label(frame, text="이름").grid(row=0, column=2, padx=5)
        tk.Entry(frame, textvariable=self.name_var, width=14).grid(row=0, column=3)
        tk.Label(frame, text="생년").grid(row=0, column=4, padx=5)
        tk.Entry(frame, textvariable=self.birth_var, width=10).grid(row=0, column=5)

        tk.Label(frame, text="성별").grid(row=1, column=0, padx=5, pady=3)
        ttk.Combobox(frame, textvariable=self.gender_var, values=["남", "여"],
                     state="readonly", width=11).grid(row=1, column=1)
        tk.Label(frame, text="키(cm)").grid(row=1, column=2, padx=5)
        tk.Entry(frame, textvariable=self.height_var, width=14).grid(row=1, column=3)
        tk.Label(frame, text="몸무게(kg)").grid(row=1, column=4, padx=5)
        tk.Entry(frame, textvariable=self.weight_var, width=10).grid(row=1, column=5)

    def make_buttons(self):
        """등록/수정/삭제/비우기/CSV 등록/파일 저장·불러오기 버튼"""
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Button(frame, text="등록", width=8, command=self.on_add).pack(side="left", padx=2)
        tk.Button(frame, text="수정", width=8, command=self.on_update).pack(side="left", padx=2)
        tk.Button(frame, text="삭제", width=8, command=self.on_delete).pack(side="left", padx=2)
        tk.Button(frame, text="입력창 비우기", command=self.clear_form).pack(side="left", padx=2)
        tk.Button(frame, text="CSV 일괄 등록", command=self.on_import_csv).pack(side="left", padx=10)

        # 오른쪽: 파일 형식 선택 + 저장/불러오기
        self.fmt_var = tk.StringVar(value="json")
        tk.Button(frame, text="불러오기", command=self.on_load).pack(side="right", padx=2)
        tk.Button(frame, text="저장", command=self.on_save).pack(side="right", padx=2)
        ttk.Combobox(frame, textvariable=self.fmt_var, values=["json", "csv", "txt", "pickle"],
                     state="readonly", width=8).pack(side="right", padx=2)
        tk.Label(frame, text="파일 형식").pack(side="right")

    def make_search(self):
        """검색 (이름/식별번호 + 비만도)"""
        frame = tk.LabelFrame(self.root, text="검색", padx=10, pady=5)
        frame.pack(fill="x", padx=10, pady=5)

        self.keyword_var = tk.StringVar()
        self.search_status_var = tk.StringVar(value="전체")

        tk.Label(frame, text="이름/식별번호").pack(side="left")
        tk.Entry(frame, textvariable=self.keyword_var, width=15).pack(side="left", padx=5)
        tk.Label(frame, text="비만도").pack(side="left")
        ttk.Combobox(frame, textvariable=self.search_status_var,
                     values=["전체", "저체중", "정상", "과체중", "비만"],
                     state="readonly", width=8).pack(side="left", padx=5)
        tk.Button(frame, text="검색", command=self.on_search).pack(side="left", padx=2)
        tk.Button(frame, text="전체 보기", command=self.on_show_all).pack(side="left", padx=2)

    def make_table(self):
        """표(Treeview) + 스크롤바"""
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "name", "birth_year", "gender", "height", "weight", "bmi", "status")
        headings = ("식별번호", "이름", "생년", "성별", "키(cm)", "몸무게(kg)", "BMI", "비만도")

        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col, head in zip(columns, headings):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=100, anchor="center")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # 행을 클릭하면 on_select 실행
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def make_stats(self):
        """아래쪽 통계 표시 글자"""
        self.stats_label = tk.Label(self.root, text="", justify="left", anchor="w",
                                    relief="groove", padx=10, pady=5)
        self.stats_label.pack(fill="x", padx=10, pady=5)

    # ---------- 화면 갱신 ----------
    def show_records(self, records):
        """표를 지우고 records를 다시 채운다."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in records:
            self.tree.insert("", "end", values=(r.id, r.name, r.birth_year, r.gender,
                                                r.height, r.weight, r.bmi, r.status))

    def refresh_table(self):
        """전체 목록을 표에 보여주고 통계도 갱신한다."""
        self.show_records(self.logic.get_all())
        s = self.logic.get_statistics()
        c = s["status_counts"]
        self.stats_label.config(text=(
            f"[통계] 총 {s['count']}명 | 평균 키 {s['avg_height']}cm | "
            f"평균 몸무게 {s['avg_weight']}kg | 평균 BMI {s['avg_bmi']}\n"
            f"저체중 {c['저체중']}명 | 정상 {c['정상']}명 | 과체중 {c['과체중']}명 | 비만 {c['비만']}명"))

    def clear_form(self):
        self.id_var.set("")
        self.name_var.set("")
        self.birth_var.set("")
        self.gender_var.set("")
        self.height_var.set("")
        self.weight_var.set("")

    # ---------- 이벤트 처리 ----------
    def on_select(self, event):
        """표의 행을 클릭하면 입력창에 값을 채운다."""
        selected = self.tree.selection()
        if len(selected) == 0:
            return
        values = self.tree.item(selected[0], "values")
        self.id_var.set(values[0])
        self.name_var.set(values[1])
        self.birth_var.set(values[2])
        self.gender_var.set(values[3])
        self.height_var.set(values[4])
        self.weight_var.set(values[5])

    def on_add(self):
        ok, msg = self.logic.add_record(self.name_var.get(), self.birth_var.get(),
                                        self.gender_var.get(), self.height_var.get(),
                                        self.weight_var.get())
        if ok:
            messagebox.showinfo("등록 완료", msg)
            self.clear_form()
            self.refresh_table()
        else:
            messagebox.showwarning("입력 오류", msg)

    def on_update(self):
        ok, msg = self.logic.update_record(self.id_var.get(), self.name_var.get(),
                                           self.birth_var.get(), self.gender_var.get(),
                                           self.height_var.get(), self.weight_var.get())
        if ok:
            messagebox.showinfo("수정 완료", msg)
            self.clear_form()
            self.refresh_table()
        else:
            messagebox.showwarning("수정 오류", msg)

    def on_delete(self):
        if self.id_var.get() == "":
            messagebox.showwarning("삭제 오류", "삭제할 사람을 표에서 먼저 선택하세요.")
            return
        if not messagebox.askyesno("삭제 확인", "정말 삭제할까요?"):
            return
        ok, msg = self.logic.delete_record(self.id_var.get())
        if ok:
            messagebox.showinfo("삭제 완료", msg)
            self.clear_form()
            self.refresh_table()
        else:
            messagebox.showwarning("삭제 오류", msg)

    def on_import_csv(self):
        path = filedialog.askopenfilename(title="CSV 파일 선택",
                                          filetypes=[("CSV 파일", "*.csv")])
        if path == "":
            return
        ok, msg = self.logic.add_from_csv(path)
        if ok:
            messagebox.showinfo("일괄 등록 완료", msg)
            self.refresh_table()
        else:
            messagebox.showwarning("일괄 등록 오류", msg)

    def on_search(self):
        result = self.logic.search(self.keyword_var.get(), self.search_status_var.get())
        self.show_records(result)

    def on_show_all(self):
        self.keyword_var.set("")
        self.search_status_var.set("전체")
        self.refresh_table()

    def on_save(self):
        fmt = self.fmt_var.get()
        if self.logic.save(fmt):
            self.logic.fmt = fmt
            messagebox.showinfo("저장 완료", f"{fmt} 형식으로 저장했습니다.")
        else:
            messagebox.showerror("저장 오류", "파일 저장에 실패했습니다.")

    def on_load(self):
        fmt = self.fmt_var.get()
        if self.logic.load(fmt):
            self.logic.fmt = fmt
            self.refresh_table()
            messagebox.showinfo("불러오기 완료", f"{fmt} 파일을 불러왔습니다.")
        else:
            messagebox.showerror("불러오기 오류", "파일이 없거나 읽을 수 없습니다.")

    def run(self):
        self.root.mainloop()