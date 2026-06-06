# -*- coding: utf-8 -*-
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from .settings import RESIMLER_DIR
from .translations import _t, _current_lang, _set_lang, restart_app
from .utils import _mkbtn, _darken
from .crop_editor import CropEditor

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF_Create_Export_Edit")
        self.root.geometry("960x680")
        self.root.minsize(720, 480)

        self.image_dir = None
        self.images = []
        self.selection = {}
        self.thumb_refs = {}
        self.thumb_frames = {}

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def _build_ui(self):
        # ─── Header ───
        header = tk.Frame(self.root, bg="#1a252f", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text="PDF Image Export", fg="white", bg="#1a252f",
            font=("Segoe UI", 18, "bold"),
        ).pack(side=tk.LEFT, padx=20, pady=12)
        tk.Label(
            header, text=_t("PDF \u2194 Resim Dönüştürücü"),
            fg="#95a5a6", bg="#1a252f", font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, padx=6, pady=12)

        # ─── Toolbar (scrollable, 2 satır, gruplu hizalama) ───
        tbar_canvas = tk.Canvas(self.root, bg="#2c3e50", height=88, highlightthickness=0)
        tbar_canvas.pack(fill=tk.X)
        tbar_canvas.pack_propagate(False)

        toolbar = tk.Frame(tbar_canvas, bg="#2c3e50")
        toolbar.bind("<Configure>", lambda e: tbar_canvas.configure(
            scrollregion=tbar_canvas.bbox("all")))
        tbar_canvas.create_window((0, 0), window=toolbar, anchor="nw")
        tbar_canvas.bind("<MouseWheel>", lambda e: tbar_canvas.xview_scroll(
            -int(e.delta / 120), "units"))

        bg_color = "#2c3e50"

        def _group():
            g = tk.Frame(toolbar, bg=bg_color)
            g.pack(side=tk.LEFT, padx=2)
            r1 = tk.Frame(g, bg=bg_color)
            r1.pack(fill=tk.X, pady=(6, 3))
            r2 = tk.Frame(g, bg=bg_color)
            r2.pack(fill=tk.X, pady=(3, 6))
            return r1, r2

        # Grup 1: PDF Yükle / Resim Yükle — Tümünü Seç / Seçimi Kaldır
        g1r1, g1r2 = _group()
        _mkbtn(g1r1, "PDF Y\xfckle", self.open_pdf, bg="#3498db", width=14).pack(side=tk.LEFT, padx=6)
        _mkbtn(g1r1, "Resim Y\xfckle", self.open_images, bg="#3498db", width=14).pack(side=tk.LEFT, padx=6)
        _mkbtn(g1r2, "T\xfcm\xfcn\xfc Se\xe7", self.select_all, bg="#7f8c8d", width=14).pack(side=tk.LEFT, padx=6)
        _mkbtn(g1r2, "Se\xe7imi Kald\u0131r", self.deselect_all, bg="#7f8c8d", width=14).pack(side=tk.LEFT, padx=6)
        tk.Frame(toolbar, bg="#34495e", width=1).pack(side=tk.LEFT, fill=tk.Y, padx=6)

        # Grup 2: PDF Metin Düzenle — ↑ Yukarı / ↓ Aşağı
        g2r1, g2r2 = _group()
        _mkbtn(g2r1, "PDF Metin D\xfczenle", self.edit_pdf_text, bg="#e67e22", width=22).pack(side=tk.LEFT, padx=6)
        mid = tk.Frame(g2r2, bg=bg_color)
        mid.pack(side=tk.LEFT, padx=6, fill=tk.X, expand=True)
        _mkbtn(mid, "\u2191 Yukar\u0131", self.move_up, bg="#8e44ad", width=10).pack(side=tk.LEFT)
        tk.Label(mid, text="  ", bg=bg_color).pack(side=tk.LEFT)
        _mkbtn(mid, "\u2193 A\u015fa\u011f\u0131", self.move_down, bg="#8e44ad", width=10).pack(side=tk.LEFT)
        tk.Frame(toolbar, bg="#34495e", width=1).pack(side=tk.LEFT, fill=tk.Y, padx=6)

        # Grup 3: Resmi Düzenle / Seçilenleri PDF Yap / Seçileni Kaydet — Hakkında
        g3r1, g3r2 = _group()
        _mkbtn(g3r1, "Resmi D\xfczenle", self.crop_selected, bg="#27ae60", width=16).pack(side=tk.LEFT, padx=6)
        _mkbtn(g3r1, "Se\xe7ilenleri PDF Yap", self.make_pdf, bg="#e67e22", width=16).pack(side=tk.LEFT, padx=6)
        _mkbtn(g3r1, "Se\xe7ileni Kaydet", self.save_selected, bg="#2980b9", width=16).pack(side=tk.LEFT, padx=6)
        _mkbtn(g3r2, "Hakk\u0131nda", self.show_about, bg="#7f8c8d", width=16).pack(side=tk.LEFT, padx=6)
        _mkbtn(g3r2, "Sa\u011f Tu\u015fa Ekle", self.add_context_menu, bg="#27ae60", width=16).pack(side=tk.LEFT, padx=6)
        _mkbtn(g3r2, "Sa\u011f Tu\u015ftan Kald\u0131r", self.remove_context_menu, bg="#c0392b", width=16).pack(side=tk.LEFT, padx=6)
        tk.Frame(toolbar, bg="#34495e", width=1).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        _mkbtn(g3r2, "EN" if _current_lang == "tr" else "TR",
               self._toggle_lang, bg="#34495e", width=6).pack(side=tk.LEFT, padx=6)
        ttk.Separator(g3r2, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=4)
        _mkbtn(g3r2, "?", self.show_help, bg="#34495e", width=3).pack(side=tk.LEFT, padx=2)

        # ─── Thumbnail area ───
        container = tk.Frame(self.root, bg="#ecf0f1")
        container.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(container, bg="white", bd=1, relief="solid")
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.canvas_area = tk.Canvas(inner, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(inner, orient="vertical", command=self.canvas_area.yview)
        self.scrollable = tk.Frame(self.canvas_area, bg="white")

        self.scrollable.bind(
            "<Configure>",
            lambda e: self.canvas_area.configure(scrollregion=self.canvas_area.bbox("all")),
        )
        self.canvas_area.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas_area.configure(yscrollcommand=scrollbar.set)

        self.canvas_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ─── Status bar ───
        status_bar = tk.Frame(self.root, bg="#f8f9fa", height=30, bd=1, relief="sunken")
        status_bar.pack(fill=tk.X)
        status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            status_bar, text=_t("Haz\u0131r"), bg="#f8f9fa", fg="#555",
            font=("Segoe UI", 9),
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.count_label = tk.Label(
            status_bar, text=_t("0 g\xf6rsel"), bg="#f8f9fa", fg="#888",
            font=("Segoe UI", 9),
        )
        self.count_label.pack(side=tk.RIGHT, padx=10)

        self.canvas_area.bind("<Configure>", lambda e: self._show_thumbs())

    def _set_status(self, text):
        self.status_label.config(text=_t(text))

    def _toggle_lang(self):
        global _current_lang
        new = "en" if _current_lang == "tr" else "tr"
        _set_lang(new)
        self.root.destroy()
        restart_app()

    def clear_thumbs(self):
        for w in self.scrollable.winfo_children():
            w.destroy()
        self.images = []
        self.selection = {}
        self.thumb_refs = {}
        self.thumb_frames = {}
        self.count_label.config(text=_t("0 g\xf6rsel"))

    def load_images(self, paths):
        self.clear_thumbs()
        self.images = paths
        self.image_dir = os.path.dirname(paths[0]) if paths else None
        self.selection = {p: tk.BooleanVar(value=False) for p in paths}
        self._show_thumbs()
        self._set_status(_t("{n} görsel yüklendi").replace("{n}", str(len(paths))))
        self.count_label.config(text=f"{len(paths)} g\xf6rsel")

    def _show_thumbs(self, *_):
        for w in self.scrollable.winfo_children():
            w.destroy()

        if not self.images:
            return

        cw = self.canvas_area.winfo_width() or 700
        cols = max(1, (cw - 20) // 165)

        row = col = 0
        for i, path in enumerate(self.images):
            frame = tk.Frame(
                self.scrollable, bg="white", bd=1, relief="solid",
                highlightbackground="#dcdde1", highlightthickness=1,
            )
            frame.grid(row=row, column=col, padx=8, pady=8, sticky="n")
            self.thumb_frames[path] = frame

            try:
                img = Image.open(path)
                img.thumbnail((150, 150), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                self.thumb_refs[path] = tk_img
            except Exception:
                continue

            lbl = tk.Label(frame, image=tk_img, bg="white", cursor="hand2")
            lbl.pack(padx=4, pady=(4, 0))
            lbl.bind("<Double-Button-1>", lambda e, p=path: self.open_editor(p))

            cb = tk.Checkbutton(frame, variable=self.selection[path],
                                bg="white", cursor="hand2")
            cb.pack(pady=(2, 0))
            cb.bind("<Double-Button-1>", lambda e, p=path: self.open_editor(p))

            name = os.path.basename(path)
            tk.Label(frame, text=name, bg="white", fg="#555",
                     wraplength=150, font=("Segoe UI", 8)).pack(pady=(0, 4))

            frame.bind("<Button-1>", lambda e, p=path, idx=i: self._drag_start(e, p, idx))
            lbl.bind("<Button-1>", lambda e, p=path, idx=i: self._drag_start(e, p, idx))
            cb.bind("<Button-1>", lambda e, p=path, idx=i: self._drag_start(e, p, idx))

            col += 1
            if col >= cols:
                col = 0
                row += 1

        self.scrollable.update_idletasks()

    def _drag_start(self, e, path, idx):
        self._drag_source_path = path
        self._drag_source_idx = idx
        self._drag_widget = e.widget
        self._drag_start_x = e.x_root
        self._drag_start_y = e.y_root
        self._drag_widget.config(cursor="fleur")
        self._drag_widget.bind("<B1-Motion>", self._drag_motion)
        self._drag_widget.bind("<ButtonRelease-1>", self._drag_drop)

    def _drag_motion(self, e):
        w = e.widget
        dx = e.x_root - self._drag_start_x
        dy = e.y_root - self._drag_start_y
        if abs(dx) > 15 or abs(dy) > 15:
            w.config(cursor="fleur")

    def _drag_drop(self, e):
        w = self._drag_widget if hasattr(self, "_drag_widget") else e.widget
        w.unbind("<B1-Motion>")
        w.unbind("<ButtonRelease-1>")
        w.config(cursor="")
        if not hasattr(self, "_drag_source_path"):
            return
        dx = e.x_root - self._drag_start_x
        dy = e.y_root - self._drag_start_y
        if abs(dx) < 20 and abs(dy) < 20:
            del self._drag_source_path
            del self._drag_widget
            return
        drop_x, drop_y = e.x_root, e.y_root
        kids = self.scrollable.winfo_children()
        best_idx = self._drag_source_idx
        best_dist = 999999
        for i, child in enumerate(kids):
            if child == self.thumb_frames.get(self._drag_source_path):
                continue
            cx = child.winfo_rootx() + child.winfo_width() // 2
            cy = child.winfo_rooty() + child.winfo_height() // 2
            d = (cx - drop_x) ** 2 + (cy - drop_y) ** 2
            if d < best_dist:
                best_dist = d
                best_idx = i
        if best_idx != self._drag_source_idx:
            item = self.images.pop(self._drag_source_idx)
            target = best_idx if best_idx < self._drag_source_idx else best_idx - 1
            self.images.insert(target, item)
            self._show_thumbs()
            self._set_status(_t("Sıralama güncellendi"))
        del self._drag_source_path
        del self._drag_widget

    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path:
            return

        self._set_status(_t("PDF işleniyor..."))
        self.root.update()
        try:
            os.makedirs(RESIMLER_DIR, exist_ok=True)
            doc = fitz.open(path)
            base = os.path.splitext(os.path.basename(path))[0]
            paths = []
            for i in range(len(doc)):
                page = doc[i]
                pix = None
                for zoom in [2, 1, 0.5, 0.25]:
                    try:
                        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                        break
                    except Exception:
                        continue
                if pix is None:
                    raise RuntimeError("Sayfa cok buyuk, render edilemiyor")
                img_path = os.path.join(RESIMLER_DIR, f"{base}_{i + 1}.png")
                pix.save(img_path)
                pix = None
                paths.append(img_path)
            doc.close()
            paths.sort(key=lambda x: int(x.rsplit("_", 1)[1].rsplit(".", 1)[0]))
            self.load_images(paths)
        except Exception as e:
            self._set_status(_t("Hata: {e}").replace("{e}", str(e)))
            messagebox.showerror(_t("Hata"), str(e))

    def open_images(self):
        paths = filedialog.askopenfilenames(
            filetypes=[("Resim", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if paths:
            self.load_images(list(paths))

    def edit_pdf_text(self, path=None):
        if not path:
            path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
            if not path:
                return
        try:
            doc = fitz.open(path)
        except Exception as e:
            messagebox.showerror(_t("Hata"), f"PDF a\xe7\x0131lamad\u0131: {e}")
            return
        dlg = tk.Toplevel(self.root)
        dlg.title(f"PDF Metin D\xfczenle - {os.path.basename(path)}")
        dlg.geometry("750x650")
        dlg.transient(self.root)
        dlg.grab_set()
        _fullscreen = False
        _saved_geom = "750x650"
        def _toggle_fullscreen():
            nonlocal _fullscreen, _saved_geom
            if not _fullscreen:
                _saved_geom = dlg.geometry()
                dlg.attributes("-fullscreen", True)
            else:
                dlg.attributes("-fullscreen", False)
                dlg.geometry(_saved_geom)
            _fullscreen = not _fullscreen
            fs_btn.config(text="\u25a2 Tam Ekran" if not _fullscreen else "\u25a2 Pencere")
        def _exit_fs(e):
            if _fullscreen:
                _toggle_fullscreen()
        dlg.bind("<Escape>", _exit_fs)
        top = tk.Frame(dlg, bg="#2c3e50", height=40)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        page_var = tk.IntVar(value=1)
        page_blocks = {}
        def _load_page():
            block_list.delete(0, tk.END)
            edit_text.delete("1.0", tk.END)
            pi = page_var.get() - 1
            if pi in page_blocks:
                blks = page_blocks[pi]
            else:
                try:
                    page = doc[pi]
                    blks = []
                    for b in page.get_text("dict")["blocks"]:
                        if b["type"] != 0:
                            continue
                        for line in b["lines"]:
                            for span in line["spans"]:
                                txt = span["text"].strip()
                                if txt:
                                    origin = span.get("origin", (span["bbox"][0], span["bbox"][3]))
                                    blks.append((
                                        span["bbox"][0], span["bbox"][1],
                                        span["bbox"][2], span["bbox"][3],
                                        txt, span["size"], span["font"],
                                        origin[0], origin[1]
                                    ))
                    page_blocks[pi] = blks
                except Exception as e:
                    messagebox.showerror(_t("Hata"), str(e))
                    return
            blocks_data.clear()
            for b in blks:
                blocks_data.append(b)
                block_list.insert(tk.END, b[4][:60])
        def _prev():
            if page_var.get() > 1:
                page_var.set(page_var.get() - 1)
                _load_page()
        def _next():
            if page_var.get() < len(doc):
                page_var.set(page_var.get() + 1)
                _load_page()
        tk.Button(top, text="\u25c0", font=("Segoe UI", 10, "bold"),
                  bg="#34495e", fg="white", relief="flat", bd=0,
                  cursor="hand2", command=_prev).pack(side=tk.LEFT, padx=4)
        tk.Label(top, textvariable=page_var, bg="#2c3e50", fg="white",
                 font=("Segoe UI", 10, "bold"), width=4).pack(side=tk.LEFT)
        tk.Button(top, text="\u25b6", font=("Segoe UI", 10, "bold"),
                  bg="#34495e", fg="white", relief="flat", bd=0,
                  cursor="hand2", command=_next).pack(side=tk.LEFT, padx=4)
        tk.Label(top, text=f"/ {len(doc)}", bg="#2c3e50", fg="#bbb",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=2)
        fs_btn = tk.Button(top, text="\u25a2 Tam Ekran", font=("Segoe UI", 9),
                           bg="#34495e", fg="#bbb", relief="flat", bd=0,
                           cursor="hand2", command=_toggle_fullscreen)
        fs_btn.pack(side=tk.RIGHT, padx=8)
        body = tk.Frame(dlg, bg="#ecf0f1")
        body.pack(fill=tk.BOTH, expand=True)
        left_frame = tk.Frame(body, bg="#2c3e50", width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)
        tk.Label(left_frame, text="Metin Bloklar\u0131", bg="#2c3e50", fg="#bbb",
                 font=("Segoe UI", 8)).pack(pady=(6, 2))
        block_list = tk.Listbox(left_frame, bg="#34495e", fg="white",
                                selectbackground="#27ae60", font=("Segoe UI", 9),
                                bd=0, highlightthickness=0, exportselection=0)
        block_list.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)
        right_frame = tk.Frame(body, bg="#ecf0f1")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(right_frame, text="Metin \u0130\xe7eri\u011fi", bg="#ecf0f1", fg="#555",
                 font=("Segoe UI", 9, "bold")).pack(pady=(8, 4))
        edit_text = tk.Text(right_frame, bg="white", fg="#333",
                            font=("Segoe UI", 10), wrap=tk.WORD, bd=1,
                            relief="solid", padx=6, pady=6)
        edit_text.pack(fill=tk.BOTH, expand=True, padx=8)
        bottom = tk.Frame(dlg, bg="#f8f9fa", height=44)
        bottom.pack(fill=tk.X)
        bottom.pack_propagate(False)
        blocks_data = []
        def _on_select(event):
            sel = block_list.curselection()
            if not sel:
                return
            idx = sel[0]
            if idx < len(blocks_data):
                edit_text.delete("1.0", tk.END)
                edit_text.insert("1.0", blocks_data[idx][4])
        block_list.bind("<<ListboxSelect>>", _on_select)
        def _apply():
            sel = block_list.curselection()
            if not sel:
                return
            idx = sel[0]
            if idx >= len(blocks_data):
                return
            b = blocks_data[idx]
            new_text = edit_text.get("1.0", tk.END).strip()
            if not new_text:
                return
            try:
                pi = page_var.get() - 1
                page = doc[pi]
                rect = fitz.Rect(b[0], b[1], b[2], b[3])
                page.add_redact_annot(rect, fill=(1, 1, 1))
                page.apply_redactions()
                fontsize = b[5] if b[5] > 0 else 11
                fontname = b[6] if len(b) > 6 else "helv"
                origin_y = b[8] if len(b) > 8 else b[1] + fontsize
                std_fonts = {"helv", "hebo", "heit", "nimb", "nimbus",
                             "times", "tibo", "tibt", "cour", "cobo", "cobt"}
                font_lower = fontname.lower().replace(" ", "")
                font_lower = font_lower.replace("-", "")
                if any(s in font_lower for s in std_fonts):
                    page.insert_text((b[0], origin_y), new_text,
                                    fontsize=fontsize, color=(0, 0, 0),
                                    fontname=fontname)
                else:
                    arial = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", "arial.ttf")
                    if os.path.exists(arial):
                        page.insert_text((b[0], origin_y), new_text,
                                        fontsize=fontsize, color=(0, 0, 0),
                                        fontfile=arial, fontname="/ArialMT")
                    else:
                        page.insert_text((b[0], origin_y), new_text,
                                        fontsize=fontsize, color=(0, 0, 0))
                new_block = (b[0], b[1], b[2], b[3], new_text, b[5], b[6], b[7], b[8])
                blocks_data[idx] = new_block
                page_blocks[pi] = list(blocks_data)
                block_list.delete(idx)
                block_list.insert(idx, new_text[:60])
                block_list.selection_set(idx)
                self._set_status(_t("Sayfa {n} - blok {idx} güncellendi").replace("{n}", str(page_var.get())).replace("{idx}", str(idx)))
            except Exception as e:
                messagebox.showerror(_t("Hata"), f"Uygulanamad\u0131: {e}")
        def _save_pdf():
            out = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialdir=RESIMLER_DIR)
            if not out:
                return
            try:
                doc.save(out)
                res = messagebox.askyesno("Bitti", f"PDF kaydedildi:\n{out}\n\nA\xe7mak ister misiniz?")
                if res:
                    os.startfile(out)
            except Exception as e:
                messagebox.showerror(_t("Hata"), f"Kaydedilemedi: {e}")
        _mkbtn(bottom, "Uygula", _apply, bg="#27ae60", width=10).pack(
            side=tk.LEFT, padx=6, pady=6)
        _mkbtn(bottom, "PDF Kaydet", _save_pdf, bg="#2980b9", width=12).pack(
            side=tk.LEFT, padx=4, pady=6)
        _mkbtn(bottom, "Kapat", dlg.destroy, bg="#e74c3c", width=10).pack(
            side=tk.RIGHT, padx=6, pady=6)
        _load_page()

    def open_editor(self, path):

        def _on_save(p):
            self._refresh_thumb(p)

        CropEditor(self.root, path, on_save=_on_save)

    def _refresh_thumb(self, path):
        self._show_thumbs()

    def show_about(self):
        messagebox.showinfo(
            _t("Hakk\u0131nda"),
            _t("PDF_Create_Export_Edit\n\n"
               "Yaz\u0131l\u0131m: Asri Akdeniz\n"
               "Mail: asriakdeniz@gmail.com")
        )

    def show_help(self):
        title = _t("Yard\u0131m") if _current_lang == "tr" else "Help"
        if _current_lang == "tr":
            text = """\
PDF_Create_Export_Edit - Kullan\u0131m K\u0131lavuzu

========================================
1. PDF \u0130\u015flemleri
========================================

PDF Y\u00fckle:
  Bir PDF dosyas\u0131n\u0131 a\u00e7ar ve t\u00fcm sayfalar\u0131n\u0131 resim
  olarak g\u00f6sterir. Resimler resimler/ klas\u00f6r\u00fcne kaydedilir.

PDF Metin D\u00fczenle:
  Bir PDF'nin metin bloklar\u0131n\u0131 g\u00f6r\u00fcnt\u00fcler, d\u00fczenlemenize
  ve yeni PDF olarak kaydetmenize olanak tan\u0131r.

Sa\u011f Tu\u015fa Ekle:
  Windows sa\u011f t\u0131k men\u00fcs\u00fcne PDF Create Export Edit k\u0131sayollar\u0131n\u0131 ekler.
  PDF ve resim dosyalar\u0131na sa\u011f t\u0131klayarak h\u0131zl\u0131 eri\u015fim.

Sa\u011f Tu\u015ftan Kald\u0131r:
  PDF Create Export Edit sa\u011f t\u0131k men\u00fcs\u00fcn\u00fc kald\u0131r\u0131r.

========================================
2. Resim \u0130\u015flemleri
========================================

Resim Y\u00fckle:
  PNG, JPG, BMP, TIFF, GIF, WEBP dosyalar\u0131n\u0131 listeye ekler.

Resmi D\u00fczenle:
  Se\u00e7ili resmi CropEditor ile d\u00fczenler.
  Ara\u00e7lar: Kes, F\u0131r\u00e7a, Boya/Sil, Alan Se\u00e7, Metin,
  \u00c7izgi, Tek Ok, \u00c7ift Ok, K\u0131rp

Se\u00e7ilenleri PDF Yap:
  Se\u00e7ili resimlerden tek bir PDF olu\u015fturur.

Se\u00e7ileni Kaydet:
  Se\u00e7ili resim(ler)i farkl\u0131 formatta kaydeder.

========================================
3. CropEditor Ara\u00e7lar\u0131
========================================

Kes:      Fare ile alan\u0131 renklendirir/boyar.
F\u0131r\u00e7a: Serbest \u00e7izim yapar.
Boya/Sil: Belirtilen renkle boyar veya siler.
Alan Se\u00e7: Kare/dikd\u00f6rtgen se\u00e7im yapar.
Metin:    T\u0131klanan yere metin ekler.
\u00c7izgi:    \u00c7izgi \u00e7izer.
Tek Ok:   Tek y\u00f6nl\u00fc ok \u00e7izer.
\u00c7ift Ok: \u00c7ift y\u00f6nl\u00fc ok \u00e7izer.
K\u0131rp:     Alan se\u00e7ip g\u00f6r\u00fcnt\u00fcy\u00fc k\u0131rpar.

Se\u00e7im Sonras\u0131 \u0130\u015flemler:
- Kes: Se\u00e7ili alan\u0131 beyaz yapar
- Boya: Se\u00e7ili alan\u0131 renklendirir
- Kopyala: Se\u00e7imi kopyalar, Uygula ile yap\u0131\u015ft\u0131r\u0131n
- Ta\u015f\u0131: Se\u00e7imi ta\u015f\u0131r, Uygula ile yerle\u015ftirin
- D\u00f6nd\u00fcr: Se\u00e7imi a\u00e7\u0131l\u0131 d\u00f6nd\u00fcr\u00fcr
- Yans\u0131: Yatay/Dikey yans\u0131tma

K\u00f6\u015fe Tutama\u00e7lar\u0131:
- Beyaz kareler: S\u00fcr\u00fckleyerek d\u00f6nd\u00fcrme
- Turuncu kareler: Oransal \u00f6l\u00e7ekleme
- K\u0131rm\u0131z\u0131 kareler: Serbest yeniden boyutland\u0131rma

Alt \u00c7ubuk:
- Uygula: Ta\u015f\u0131ma/kopyalamay\u0131 tamamlar
- Geri Al: Son i\u015flemi geri al\u0131r
- Kaydet: Dosyan\u0131n \u00fczerine kaydeder
- Farkl\u0131 Kaydet: Yeni format/konumda kaydeder

========================================
4. PDF Metin D\u00fczenleyici
========================================
- Sol panelde metin bloklar\u0131n\u0131 g\u00f6r\u00fcn
- Bir blo\u011fa t\u0131klay\u0131n, i\u00e7eri\u011fi sa\u011f panelde d\u00fczenleyin
- Uygula: De\u011fi\u015fikli\u011fi ge\u00e7ici olarak uygular
- PDF Kaydet: De\u011fi\u015fikliklerle yeni PDF olu\u015fturur
- Tam Ekran: D\u00fczenleyiciyi b\u00fcy\u00fct\u00fcr
- \u25c0 \u25b6: Sayfalar aras\u0131 gezinti

========================================
5. Dil Se\u00e7imi
========================================
- EN butonu: T\u00fcrk\u00e7e'den \u0130ngilizce'ye ge\u00e7er
- TR butonu: \u0130ngilizce'den T\u00fcrk\u00e7e'ye ge\u00e7er
- Dil se\u00e7imi kaydedilir, program yeniden ba\u015flat\u0131l\u0131r

========================================
6. Komut Sat\u0131r\u0131 Kullan\u0131m\u0131
========================================
--extract-pdf <dosya.pdf>
  PDF'deki t\u00fcm sayfalar\u0131 resim olarak \u00e7\u0131kar\u0131r.

--edit-pdf <dosya.pdf>
  PDF metin d\u00fczenleyiciyi a\u00e7ar.

--edit-image <resim.png>
  CropEditor ile resmi d\u00fczenler.

--make-pdf <resim.png>
  Tek resmi PDF'e \u00e7evirir.

--combine-pdf <resim1.png> <resim2.png> ...
  Birden \u00e7ok resmi tek PDF'te birle\u015ftirir.

--edit-multi <resim1.png> <resim2.png> ...
  Resimleri CropEditor ile a\u00e7ar (se\u00e7imli).

--extract-pdf-gui <dosya.pdf>
  PDF resimlerini \u00e7\u0131kar\u0131p CropEditor ile a\u00e7ar.

========================================
7. S\u0131ralama
========================================
- \u2191 Yukar\u0131 / \u2193 A\u015fa\u011f\u0131: Se\u00e7ili g\u00f6rseli ta\u015f\u0131r
- S\u00fcr\u00fckle-b\u0131rak: G\u00f6rselleri fareyle s\u00fcr\u00fckleyerek s\u0131ralay\u0131n

========================================
8. Hakk\u0131nda
========================================
PDF_Create_Export_Edit
Yaz\u0131l\u0131m: Asri Akdeniz
Mail: asriakdeniz@gmail.com"""
        else:
            text = """\
PDF_Create_Export_Edit - User Guide

========================================
1. PDF Operations
========================================

Load PDF:
  Opens a PDF file and displays all pages as images.
  Images are saved to the resimler/ folder.

Edit PDF Text:
  View and edit text blocks of a PDF, save as a new PDF.

Add to Right-Click:
  Adds PDF Create Export Edit shortcuts to the Windows context menu.
  Quick access by right-clicking PDF and image files.

Remove from Right-Click:
  Removes PDF Create Export Edit from the right-click menu.

========================================
2. Image Operations
========================================

Load Image(s):
  Add PNG, JPG, BMP, TIFF, GIF, WEBP files to the list.

Edit Image:
  Opens the selected image in the CropEditor.
  Tools: Cut, Brush, Paint/Erase, Select Area, Text,
  Line, Single Arrow, Double Arrow, Crop

Make PDF from Selected:
  Creates a single PDF from selected images.

Save Selected:
  Saves selected image(s) in a different format.

========================================
3. CropEditor Tools
========================================

Cut:      Drag to color/fill an area.
Brush:    Freehand drawing.
Paint/Erase: Paint with selected color or erase.
Select Area: Make rectangular selection.
Text:     Click to add text.
Line:     Draw a line.
Single Arrow: Draw a single-headed arrow.
Double Arrow: Draw a double-headed arrow.
Crop:     Select area and crop the image.

Selection Actions:
- Cut: Makes selected area white
- Fill: Colors the selected area
- Copy: Copies selection, paste with Apply
- Move: Moves selection, place with Apply
- Rotate: Rotates selection by any angle
- Flip: Horizontal/Vertical flip

Corner Handles:
- White squares: Drag to rotate
- Orange squares: Proportional scale
- Red squares: Free resize

Bottom Bar:
- Apply: Confirm move/copy action
- Undo: Revert the last action
- Save: Overwrite the file
- Save As: Save in new format/location

========================================
4. PDF Text Editor
========================================
- View text blocks in the left panel
- Click a block, edit content in the right panel
- Apply: Temporarily apply the change
- Save PDF: Create a new PDF with changes
- Fullscreen: Enlarge the editor view
- \u25c0 \u25b6: Navigate between pages

========================================
5. Language Selection
========================================
- EN button: Switch from Turkish to English
- TR button: Switch from English to Turkish
- Language preference is saved, program restarts

========================================
6. Command Line Usage
========================================
--extract-pdf <file.pdf>
  Extracts all PDF pages as images.

--edit-pdf <file.pdf>
  Opens the PDF text editor.

--edit-image <image.png>
  Edits the image in CropEditor.

--make-pdf <image.png>
  Converts a single image to PDF.

--combine-pdf <img1.png> <img2.png> ...
  Combines multiple images into one PDF.

--edit-multi <img1.png> <img2.png> ...
  Opens images in CropEditor (selective).

--extract-pdf-gui <file.pdf>
  Extracts PDF images and opens in CropEditor.

========================================
7. Ordering
========================================
- \u2191 Move Up / \u2193 Move Down: Move selected image
- Drag-and-drop: Reorder images by dragging

========================================
8. About
========================================
PDF_Create_Export_Edit
Software: Asri Akdeniz
Mail: asriakdeniz@gmail.com"""

        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("700x600")
        win.minsize(500, 400)

        frame = tk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 10),
                              bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        text_widget.insert("1.0", text)
        text_widget.config(state=tk.DISABLED)

        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(win, bg="#f8f9fa")
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Button(btn_frame, text=_t("Kapat"), command=win.destroy,
                  bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", bd=0, cursor="hand2", width=12).pack(pady=4)

    def crop_selected(self):
        selected = [p for p, v in self.selection.items() if v.get()]
        if not selected:
            messagebox.showwarning(_t("Uyarı"), _t("Önce resim seçin"))
            return

        def _on_save(p):
            self._refresh_thumb(p)

        for p in selected:
            CropEditor(self.root, p, on_save=_on_save)

    def make_pdf(self):
        selected = [p for p, v in self.selection.items() if v.get()]
        if not selected:
            messagebox.showwarning(_t("Uyarı"), _t("Önce resim seçin"))
            return

        self._set_status(_t("PDF oluşturuluyor..."))
        self.root.update()

        try:
            images = [Image.open(p).convert("RGB") for p in selected]
            first_dir = os.path.dirname(selected[0])
            base = os.path.splitext(os.path.basename(selected[0]))[0]
            pdf_path = os.path.join(first_dir, f"{base}.pdf")
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            if len(images) == 1:
                images[0].save(pdf_path, "PDF")
            else:
                images[0].save(pdf_path, "PDF", save_all=True, append_images=images[1:])
            self.root.title(f"PDF_Create_Export_Edit - {os.path.basename(pdf_path)}")
            self._set_status(_t("PDF kaydedildi: {path}").replace("{path}", pdf_path))
            messagebox.showinfo(_t("Bitti"), f"PDF kaydedildi:\n{pdf_path}")
        except Exception as e:
            self._set_status(_t("Hata: {e}").replace("{e}", str(e)))
            messagebox.showerror(_t("Hata"), f"PDF olu\u015fturulamad\u0131:\n{e}")

    def save_selected(self):
        selected = [p for p, v in self.selection.items() if v.get()]
        if not selected:
            messagebox.showwarning(_t("Uyarı"), _t("Önce resim seçin"))
            return
        out = filedialog.askdirectory(title="Kay\u0131t klas\xf6r\xfc", initialdir=APP_DIR)
        if not out:
            return
        for p in selected:
            img = Image.open(p)
            name = os.path.basename(p)
            img.save(os.path.join(out, name))
        self._set_status(_t("{n} resim kaydedildi").replace("{n}", str(len(selected))))
        messagebox.showinfo(_t("Bitti"), f"{len(selected)} resim kaydedildi.")

    def select_all(self):
        for v in self.selection.values():
            v.set(True)

    def deselect_all(self):
        for v in self.selection.values():
            v.set(False)

    def move_up(self):
        self._move_selection(-1)

    def move_down(self):
        self._move_selection(1)

    def _move_selection(self, direction):
        selected = [(i, p) for i, p in enumerate(self.images) if self.selection[p].get()]
        if not selected:
            messagebox.showwarning(_t("Uyarı"), _t("Önce resim seçin"))
            return
        n = len(self.images)
        new_order = list(self.images)
        if direction == -1:
            selected.sort(key=lambda x: x[0])
            for i, p in selected:
                if i == 0:
                    continue
                new_order[i], new_order[i - 1] = new_order[i - 1], new_order[i]
        else:
            selected.sort(key=lambda x: x[0], reverse=True)
            for i, p in selected:
                if i == n - 1:
                    continue
                new_order[i], new_order[i + 1] = new_order[i + 1], new_order[i]
        self.images = new_order
        self._show_thumbs()
        self._set_status(_t("Sıralama güncellendi"))

    # ───── Context menu (Windows sag tus - PDF Create Export Edit) ─────
    def add_context_menu(self):
        import winreg
        if getattr(sys, "frozen", False):
            exe = sys.executable
            icon = exe
            script = None
        else:
            exe = sys.executable
            script = os.path.abspath(__file__)
            icon = ""

        def _cmd(flag):
            if getattr(sys, "frozen", False):
                return f'"{exe}" {flag} "%1"'
            else:
                return f'"{exe}" "{script}" {flag} "%1"'

        _img_exts = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp"]

        def _add_entries(base, ctx_key, items):
            """Create parent verb with ExtendedSubCommandsKey + sub-items under ctx_key."""
            # Parent verb
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, base)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "PDF Create Export Edit")
            winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, "PDF Create Export Edit")
            full_ctx = "SystemFileAssociations" + ctx_key
            winreg.SetValueEx(key, "ExtendedSubCommandsKey", 0, winreg.REG_SZ, full_ctx)
            if icon:
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)
            winreg.CloseKey(key)
            # Sub-items under context key
            for name, flag, label in items:
                sub = ctx_key + rf"\shell\{name}"
                k = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                    "Software\\Classes\\SystemFileAssociations" + sub)
                winreg.SetValueEx(k, "MUIVerb", 0, winreg.REG_SZ, label)
                winreg.CloseKey(k)
                k = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                    "Software\\Classes\\SystemFileAssociations" + sub + r"\command")
                winreg.SetValueEx(k, "", 0, winreg.REG_SZ, _cmd(flag))
                winreg.CloseKey(k)

        try:
            _add_entries(
                r"Software\Classes\SystemFileAssociations\.pdf\shell\ASRITools",
                r"\.pdf\ASRIToolsContext",
                [("01PDFResimCikar", "--extract-pdf", _t("PDF Resim \u00c7\u0131kar")),
                 ("02PDFMetinDuzenle", "--edit-pdf", _t("PDF Metin D\u00fczenle")),
                 ("03PDFResimCikarSecimli", "--extract-pdf-gui", _t("PDF Resim \u00c7\u0131kar (Se\u00e7imli)"))]
            )
        except Exception as e:
            messagebox.showerror(_t("Hata"), _t("PDF kayd\u0131 eklenemedi: {e}").replace("{e}", str(e)))
            return

        for ext in _img_exts:
            try:
                _add_entries(
                    f"Software\\Classes\\SystemFileAssociations\\{ext}\\shell\\ASRITools",
                    f"\\{ext}\\ASRIToolsContext",
                    [("01ResimDuzenle", "--edit-image", _t("Resim D\u00fczenle")),
                     ("02TekPDF", "--combine-pdf", _t("PDF yap")),
                     ("03TekTekPDF", "--make-pdf", _t("Tek Tek PDF yap")),
                     ("04SecimliPDF", "--edit-multi", _t("Se\u00e7imli PDF yap"))]
                )
            except Exception as e:
                messagebox.showerror(_t("Hata"), _t("{ext} kayd\u0131 eklenemedi: {e}").replace("{ext}", ext).replace("{e}", str(e)))
                return

        messagebox.showinfo(
            _t("Bitti"),
            _t("PDF Create Export Edit sa\u011f t\u0131k men\u00fcs\u00fcne eklendi.\n"
               "PDF ve resim dosyalar\u0131nda PDF Create Export Edit alt\u0131nda kullanabilirsiniz.")
        )

    def remove_context_menu(self):
        import winreg
        def _del(path):
            try:
                k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
                i = 0
                while True:
                    try:
                        sub = winreg.EnumKey(k, 0)
                        _del(path + "\\" + sub)
                    except WindowsError:
                        break
                winreg.CloseKey(k)
            except Exception:
                pass
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
            except Exception:
                pass
        base = r"Software\Classes\SystemFileAssociations"
        targets = [[".pdf", "ASRITools"], [".pdf", "ASRIToolsContext"]]
        for ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp"]:
            targets.append([ext, "ASRITools"])
            targets.append([ext, "ASRIToolsContext"])
            targets.append([ext, "ASRI_Combine_PDF"])
        for ext, key in targets:
            _del(f"{base}\\{ext}\\shell\\{key}")
            _del(f"{base}\\{ext}\\{key}")
        messagebox.showinfo(_t("Bitti"), _t("PDF Create Export Edit sağ tık menüsünden kaldırıldı."))

    def _extract_pdf(self, path):
        self._set_status(_t("PDF resimleri çıkarılıyor..."))
        self.root.update()
        try:
            os.makedirs(RESIMLER_DIR, exist_ok=True)
            doc = fitz.open(path)
            base = os.path.splitext(os.path.basename(path))[0]
            paths = []
            for i in range(len(doc)):
                page = doc[i]
                pix = None
                for zoom in [2, 1, 0.5, 0.25]:
                    try:
                        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                        break
                    except Exception:
                        continue
                if pix is None:
                    raise RuntimeError("Sayfa cok buyuk, render edilemiyor")
                img_path = os.path.join(RESIMLER_DIR, f"{base}_{i + 1}.png")
                pix.save(img_path)
                pix = None
                paths.append(img_path)
            doc.close()
            paths.sort(key=lambda x: int(x.rsplit("_", 1)[1].rsplit(".", 1)[0]))
            self.load_images(paths)
        except Exception as e:
            self._set_status(_t("Hata: {e}").replace("{e}", str(e)))
            messagebox.showerror(_t("Hata"), f"PDF resimleri cikarilamadi:\n{e}")

    def _make_pdf_from_image(self, path):
        base = os.path.splitext(os.path.basename(path))[0]
        pdf_path = os.path.join(RESIMLER_DIR, f"{base}.pdf")
        os.makedirs(RESIMLER_DIR, exist_ok=True)
        img = Image.open(path).convert("RGB")
        img.save(pdf_path, "PDF")
        messagebox.showinfo(_t("Bitti"), f"PDF olusturuldu:\n{pdf_path}")

    def _handle_command_line(self, file_arg, mode=None, extra_files=None):
        if extra_files is None:
            extra_files = []
        if not file_arg or not os.path.exists(file_arg):
            return
        try:
            ext = os.path.splitext(file_arg)[1].lower()
            _img_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp"}
            if mode == "extract-pdf" or (mode is None and ext == ".pdf"):
                self._extract_pdf(file_arg)
            elif mode == "edit-pdf":
                self.edit_pdf_text(file_arg)
            elif mode == "edit-image":
                self.load_images([file_arg])
                self.selection[file_arg].set(True)
                self.open_editor(file_arg)
            elif mode == "make-pdf":
                self._make_pdf_from_image(file_arg)
            elif mode == "combine-pdf":
                self._make_pdf_from_image(file_arg)
            elif mode == "extract-pdf-gui":
                self._extract_pdf(file_arg)
            elif mode == "edit-multi":
                all_files = [file_arg] + [f for f in extra_files if os.path.isfile(f)]
                if all_files:
                    self.load_images(all_files)
            elif ext == ".pdf":
                self.edit_pdf_text(file_arg)
            elif ext in _img_exts:
                self.load_images([file_arg])
                self.selection[file_arg].set(True)
                self.open_editor(file_arg)
            else:
                messagebox.showwarning(_t("Uyarı"), f"Desteklenmeyen dosya: {ext}")
        except Exception as e:
            messagebox.showerror(_t("Hata"), str(e))

    def run(self):
        self.root.mainloop()


