# -*- coding: utf-8 -*-
import sys
import os
import fitz
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.app import App

if __name__ == "__main__":
    mode = None
    file_arg = None
    args = sys.argv[1:]
    if args and args[0].startswith("--"):
        mode = args[0][2:]
        file_arg = args[1] if len(args) > 1 else None
    elif args:
        file_arg = args[0]

    img_exts = {'.png','.jpg','.jpeg','.bmp','.tiff','.tif','.gif','.webp'}

    import tempfile, time

    def _collect_multi(file_path, tag):
        """Collect multi-file invocations via temp file + lock.
        Returns (is_primary, collected_list)."""
        lst = os.path.join(tempfile.gettempdir(), f"asri_{tag}_list.txt")
        lck = os.path.join(tempfile.gettempdir(), f"asri_{tag}_lock.txt")
        don = os.path.join(tempfile.gettempdir(), f"asri_{tag}_done.txt")
        # Clean stale files from crashed sessions (>10s old)
        _now = time.time()
        for _f in [lst, lck, don]:
            try:
                if os.path.getmtime(_f) < _now - 10:
                    os.remove(_f)
            except:
                pass
        if os.path.exists(don):
            return False, []
        # Write file path FIRST, then try lock
        try:
            with open(lst, "a", encoding="utf-8") as f:
                f.write(file_path + "\n")
        except:
            return False, []
        acquired = False
        for _ in range(100):
            if os.path.exists(don):
                return False, []
            try:
                fd = os.open(lck, os.O_CREAT | os.O_EXCL)
                os.close(fd)
                acquired = True
                break
            except FileExistsError:
                time.sleep(0.05)
        if acquired:
            time.sleep(0.5)
            if os.path.exists(don):
                try: os.remove(lst); os.remove(lck)
                except: pass
                return False, []
            with open(lst, "r", encoding="utf-8") as f:
                files = [line.strip() for line in f if line.strip()]
            if len(files) > 1:
                time.sleep(0.5)
                if os.path.exists(don):
                    try: os.remove(lst); os.remove(lck)
                    except: pass
                    return False, []
                with open(lst, "r", encoding="utf-8") as f:
                    files = [line.strip() for line in f if line.strip()]
            try:
                os.remove(lst)
                os.remove(lck)
                with open(don, "w") as f:
                    f.write("1")
            except:
                pass
            return True, files
        return False, []

    # Headless combine-pdf: combine all selected images into one PDF
    if mode == "combine-pdf" and file_arg and os.path.exists(file_arg):
        try:
            primary, files = _collect_multi(file_arg, "combine")
            if primary:
                files = [f for f in files if os.path.isfile(f) and os.path.splitext(f)[1].lower() in img_exts]
                files = list(dict.fromkeys(files))
                files.sort()
                if files:
                    first = files[0]
                    base = os.path.splitext(os.path.basename(first))[0]
                    pdf_path = os.path.join(os.path.dirname(first), f"{base}.pdf")
                    images = [Image.open(f).convert("RGB") for f in files]
                    images[0].save(pdf_path, "PDF", save_all=True, append_images=images[1:])
            sys.exit(0)
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(_t("Hata"), str(e))
            root.destroy()
            sys.exit(0)

    # Headless make-pdf: individual PDF per image
    if mode == "make-pdf" and file_arg and os.path.exists(file_arg):
        try:
            files = [os.path.abspath(f) for f in args[2:] if os.path.isfile(f)]
            files.insert(0, os.path.abspath(file_arg))
            files = list(dict.fromkeys(files))
            files = [f for f in files if os.path.splitext(f)[1].lower() in img_exts]
            for f in files:
                base = os.path.splitext(os.path.basename(f))[0]
                pdf_path = os.path.join(os.path.dirname(f), f"{base}.pdf")
                img = Image.open(f).convert("RGB")
                img.save(pdf_path, "PDF")
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(_t("Hata"), str(e))
            root.destroy()
        sys.exit(0)

    if mode == "extract-pdf" and file_arg and os.path.exists(file_arg):
        try:
            doc = fitz.open(file_arg)
            base = os.path.splitext(os.path.basename(file_arg))[0]
            pdf_dir = os.path.dirname(os.path.abspath(file_arg))
            out_dir = os.path.join(pdf_dir, f"{base}_resimler")
            os.makedirs(out_dir, exist_ok=True)
            for i in range(len(doc)):
                pix = doc[i].get_pixmap(matrix=fitz.Matrix(4, 4))
                pix.save(os.path.join(out_dir, f"{base}_{i + 1}.png"))
            doc.close()
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(_t("Hata"), str(e))
            root.destroy()
        sys.exit(0)

    # edit-multi: collect all files via temp, then open App with them
    multi_files = None
    if mode == "edit-multi" and file_arg and os.path.exists(file_arg):
        try:
            primary, collected = _collect_multi(file_arg, "editmulti")
            if not primary:
                sys.exit(0)
            multi_files = [f for f in collected if os.path.isfile(f) and os.path.splitext(f)[1].lower() in img_exts]
            multi_files = list(dict.fromkeys(multi_files))
            multi_files.sort()
        except Exception:
            pass

    # extract-pdf-gui: just open App and let _handle_command_line load the PDF
    # (no headless handler, falls through)

    app = App()
    if multi_files:
        app.root.after(300, lambda: app._handle_command_line(multi_files[0], "edit-multi", multi_files[1:]))
    elif file_arg:
        extra_files = args[2:] if mode and len(args) > 2 else []
        app.root.after(300, lambda: app._handle_command_line(file_arg, mode, extra_files))
    app.run()
