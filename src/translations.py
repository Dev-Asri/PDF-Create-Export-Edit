# -*- coding: utf-8 -*-
import os
import json
import sys
from . import settings


_current_lang = settings._load_settings().get("lang", "tr")

_TRANS = {
    # General UI
    "PDF Yükle": "Load PDF",
    "Resim Yükle": "Load Image(s)",
    "Tümünü Seç": "Select All",
    "Seçimi Kaldır": "Deselect All",
    "PDF Metin Düzenle": "Edit PDF Text",
    "↑ Yukarı": "↑ Move Up",
    "↓ Aşağı": "↓ Move Down",
    "Resmi Düzenle": "Edit Image",
    "Seçilenleri PDF Yap": "Make PDF from Selected",
    "Seçileni Kaydet": "Save Selected",
    "Hakkında": "About",
    "Sağ Tuşa Ekle": "Add to Right-Click",
    "Sağ Tuştan Kaldır": "Remove from Right-Click",
    "PDF ↔ Resim Dönüştürücü": "PDF ↔ Image Converter",
    # CropEditor mode labels
    "Kes": "Cut",
    "F\u0131r\u00e7a": "Brush",
    "Boya/Sil": "Paint/Erase",
    "Alan Se\u00e7": "Select Area",
    "Metin": "Text",
    "\u00c7izgi": "Line",
    "Tek Ok": "Single Arrow",
    "\u00c7ift Ok": "Double Arrow",
    "K\u0131rp": "Crop",
    # CropEditor tooltips
    "Alan renklendirmek i\u00e7in s\u00fcr\u00fckleyin": "Drag to color the area",
    "F\u0131r\u00e7a ile \u00e7izin": "Draw with brush",
    "Se\u00e7ili renk ile boyay\u0131n": "Paint with selected color",
    "Se\u00e7im yap\u0131n: Ta\u015f\u0131/Kes/Boya": "Select: Move/Cut/Paint",
    "Metin eklemek i\u00e7in t\u0131klay\u0131n": "Click to add text",
    "\u00c7izgi \u00e7ekmek i\u00e7in s\u00fcr\u00fckleyin": "Drag to draw a line",
    "Ok \u00e7ekmek i\u00e7in s\u00fcr\u00fckleyin": "Drag to draw an arrow",
    "\u00c7ift y\u00f6nl\u00fc ok \u00e7ekin": "Draw a double-headed arrow",
    "G\u00f6r\u00fcnt\u00fcy\u00fc k\u0131rpmak i\u00e7in alan se\u00e7in": "Select area to crop image",
    # CropEditor selection buttons
    "✂ Kes": "✂ Cut",
    "Boya": "Fill",
    "Kopyala": "Copy",
    "Taşı": "Move",
    "Döndür": "Rotate",
    "↔ Yansı": "↔ Flip H",
    "↕ Yansı": "↕ Flip V",
    # CropEditor controls
    "Renk": "Color",
    "■ Palet": "■ Palette",
    "Kal\u0131nl\u0131k": "Thickness",
    "Yaz\u0131 Boyutu": "Font Size",
    # CropEditor bottom bar
    "Uygula": "Apply",
    "Geri Al": "Undo",
    "Kaydet": "Save",
    "Farklı Kaydet": "Save As",
    "Kapat": "Close",
    # Status messages
    "Araç seçin": "Select a tool",
    "Köşeyi sürükleyerek döndürün": "Drag corner to rotate",
    "{closest} kenarından sürükleyin": "Drag from {closest} edge",
    "Döndürme: {deg}°": "Rotation: {deg}°",
    "Yeniden boyutlandırma: {nw}x{nh}": "Resize: {nw}x{nh}",
    "Oransal küçült/büyüt: köşeden sürükleyin": "Scale: drag from corner",
    "Oransal: {nw}x{nh}": "Scale: {nw}x{nh}",
    "Döndürüldü: {deg}°": "Rotated: {deg}°",
    "Ölçeklendi": "Scaled",
    "Yeniden boyutlandı": "Resized",
    "Seçimi sürükleyin": "Drag the selection",
    "Kes: ({ix1},{iy1}) → ({ix2},{iy2})": "Cut: ({ix1},{iy1}) → ({ix2},{iy2})",
    "Görüntü kırpıldı: {w}x{h}": "Image cropped: {w}x{h}",
    "Taşı iptal": "Move cancelled",
    "Taşı: Uygula'ya basın": "Move: press Apply",
    "Seçim taşındı": "Selection moved",
    "Alan seçildi": "Area selected",
    "Metin eklendi: \"{text}\"": "Text added: \"{text}\"",
    "90 derece döndürüldü": "Rotated 90°",
    "Alan renklendirildi": "Area colored",
    "Taşı uygulandı": "Move applied",
    "Alan boyandı": "Area painted",
    "Alan kesildi": "Area cut",
    "Kopya oluştu, Uygula ile yapıştırın": "Copy created, paste with Apply",
    "Yatay yansıtıldı": "Flipped horizontally",
    "Dikey yansıtıldı": "Flipped vertically",
    "Alan döndürüldü: {angle}°": "Area rotated: {angle}°",
    "Seçimi sürükleyip bırakın": "Drag and release to move",
    "Geri alındı": "Undone",
    "Hazır": "Ready",
    "{n} görsel": "{n} image(s)",
    "0 görsel": "0 images",
    "{n} görsel yüklendi": "{n} image(s) loaded",
    "Sıralama güncellendi": "Order updated",
    "PDF işleniyor...": "Processing PDF...",
    "Hata: {e}": "Error: {e}",
    "Sayfa {n} - blok {idx} güncellendi": "Page {n} - block {idx} updated",
    "PDF oluşturuluyor...": "Creating PDF...",
    "PDF kaydedildi: {path}": "PDF saved: {path}",
    "{n} resim kaydedildi": "{n} image(s) saved",
    "PDF resimleri çıkarılıyor...": "Extracting PDF images...",
    # Dialog titles / messages
    "D\xfczenle": "Edit",
    "Renk Se\xe7": "Choose Color",
    "Renk Paleti": "Color Palette",
    "Metin Ekle": "Add Text",
    "PDF Metin Düzenle - {name}": "PDF Text Editor - {name}",
    "Kayıt klasörü": "Save folder",
    "Tam Ekran": "Fullscreen",
    "Pencere": "Window",
    "☒ Tam Ekran": "☒ Fullscreen",
    "☒ Pencere": "☒ Window",
    "Metin Blokları": "Text Blocks",
    "Metin İçeriği": "Text Content",
    "PDF Kaydet": "Save PDF",
    "Metin:": "Text:",
    "Ekle": "Add",
    "Açı (0-360):": "Angle (0-360):",
    "%{zoom}%": "%{zoom}%",
    # Messagebox content
    "Resim kaydedildi.": "Image saved.",
    "Resim kaydedildi:\n{path}": "Image saved:\n{path}",
    "PDF açılamadı: {e}": "Could not open PDF: {e}",
    "Uygulanamadı: {e}": "Could not apply: {e}",
    "PDF kaydedildi:\n{out}\n\nAçmak ister misiniz?": "PDF saved:\n{out}\n\nOpen it?",
    "Kaydedilemedi: {e}": "Could not save: {e}",
    "Önce resim seçin": "Select images first",
    "PDF kaydedildi:\n{pdf_path}": "PDF saved:\n{pdf_path}",
    "PDF oluşturulamadı:\n{e}": "Could not create PDF:\n{e}",
    "{n} resim kaydedildi.": "{n} image(s) saved.",
    "PDF resimleri çıkarılamadı:\n{e}": "Could not extract PDF images:\n{e}",
    "PDF oluşturuldu:\n{pdf_path}": "PDF created:\n{pdf_path}",
    "Desteklenmeyen dosya: {ext}": "Unsupported file: {ext}",
    "PDF kaydı eklenemedi: {e}": "Could not add PDF entry: {e}",
    "{ext} kaydı eklenemedi: {e}": "Could not add {ext} entry: {e}",
    # Misc
    "Sayfa çok büyük, render edilemiyor": "Page too large, cannot render",
    "Tüm Formatlar": "All Formats",
    "Renk Seçin:": "Choose Color:",
    "■ Özel Renk...": "■ Custom Color...",
    "Döndür 90": "Rotate 90",
    # Context menu
    "PDF Create Export Edit": "PDF Create Export Edit",
    "PDF Resim Çıkar": "Extract PDF Images",
    "PDF Metin Düzenle": "Edit PDF Text",
    "PDF Resim Çıkar (Seçimli)": "Extract PDF Images (Selective)",
    "Resim Düzenle": "Edit Image",
    "PDF yap": "Make PDF",
    "Tek Tek PDF yap": "Make PDF (Individual)",
    "Seçimli PDF yap": "Make PDF (Selective)",
    # About
    "PDF_Create_Export_Edit\n\nYazılım: Asri Akdeniz\nMail: asriakdeniz@gmail.com": "PDF_Create_Export_Edit\n\nSoftware: Asri Akdeniz\nMail: asriakdeniz@gmail.com",
    # Context menu notifications
    "PDF Create Export Edit sağ tık menüsüne eklendi.\nPDF ve resim dosyalarında PDF Create Export Edit altında kullanabilirsiniz.": "PDF Create Export Edit added to right-click menu.\nUse under PDF Create Export Edit for PDF and image files.",
    "PDF Create Export Edit sağ tık menüsünden kaldırıldı.": "PDF Create Export Edit removed from right-click menu.",
}

def _t(text):
    if _current_lang == "tr":
        return text
    return _TRANS.get(text, text)

def _set_lang(lang):
    global _current_lang
    _current_lang = lang
    _save_settings({"lang": lang})


def restart_app():
    python = sys.executable
    args = [python] + sys.argv
    if getattr(sys, "frozen", False):
        args = [sys.executable] + sys.argv[1:]
    os.execl(python, *args)

