# PDF Create Export Edit

PDF → Görsel & Görsel → PDF dönüştürücü, görsel düzenleyici, PDF metin editörü ve Windows sağ tık menüsü entegrasyonu.

PDF → Image & Image → PDF converter, image editor, PDF text editor with Windows right-click context menu integration.

---

## 🇹🇷 Türkçe

### Açıklama
PDF Create Export Edit, PDF dosyalarını yüksek çözünürlüklü görsellere dönüştüren, görselleri PDF yapan, görsel düzenleme (kesme, boyama, metin ekleme, ok çizme, kırpma, döndürme vb.) ve PDF metin düzenleme işlemlerini tek bir arayüzde sunan bir Windows masaüstü uygulamasıdır.

### Özellikler
- **PDF → Görsel**: PDF sayfalarını PNG olarak dışa aktarır
- **Görsel → PDF**: Seçili görsellerden tek veya ayrı ayrı PDF oluşturur
- **Görsel Düzenleme (CropEditor)**:
  - Kes, Fırça, Boya/Sil, Alan Seç, Metin, Çizgi, Ok, Kırp
  - Seçim araçları: Kes, Boya, Kopyala, Taşı, Döndür, Yansıt
  - Köşe/kenar tutamaçları ile ölçekleme ve döndürme
  - Renk paleti, kalınlık/yazı boyutu ayarları
  - Geri Al, Yakınlaştır/Uzaklaştır
- **PDF Metin Düzenleme**: Sayfa bazında metin bloklarını düzenleme
- **Windows Sağ Tık Menüsü**: PDF ve resim dosyalarında hızlı erişim
- **Dil Desteği**: Türkçe / İngilizce (ayarlar kaydedilir)
- **Komut Satırı Desteği**: Headless modda PDF çıkarma, PDF oluşturma

### Komut Satırı Kullanımı
```
PDF_Create_Export_Edit.exe --extract-pdf <dosya.pdf>
PDF_Create_Export_Edit.exe --edit-pdf <dosya.pdf>
PDF_Create_Export_Edit.exe --edit-image <resim.png>
PDF_Create_Export_Edit.exe --make-pdf <resim.png>
PDF_Create_Export_Edit.exe --combine-pdf <resim1.png> <resim2.png> ...
PDF_Create_Export_Edit.exe --edit-multi <resim1.png> <resim2.png> ...
PDF_Create_Export_Edit.exe --extract-pdf-gui <dosya.pdf>
```

### Gereksinimler
- Windows 10 veya üzeri
- Python 3.14+ (geliştirme için)
- Bağımlılıklar: `PyMuPDF`, `Pillow`, `PyInstaller` (derleme için)

### Derleme
```bash
pip install PyMuPDF Pillow PyInstaller
python -m PyInstaller PDF_Create_Export_Edit.spec
```

### İletişim
Yazılım: Asri Akdeniz  
Mail: asriakdeniz@gmail.com

---

## 🇬🇧 English

### Description
PDF Create Export Edit is a Windows desktop application that converts PDFs to high-resolution images, images to PDFs, and provides image editing (crop, paint, text, arrows, rotate, flip, etc.) and PDF text editing in a single interface.

### Features
- **PDF → Image**: Export PDF pages as PNG images
- **Image → PDF**: Create single or individual PDFs from selected images
- **Image Editor (CropEditor)**:
  - Cut, Brush, Paint/Erase, Select Area, Text, Line, Arrow, Crop
  - Selection tools: Cut, Fill, Copy, Move, Rotate, Flip
  - Corner/edge handles for scaling and rotation
  - Color palette, brush/font size controls
  - Undo, Zoom In/Out
- **PDF Text Editor**: Edit text blocks page by page
- **Windows Right-Click Menu**: Quick access for PDF and image files
- **Language Support**: Turkish / English (preference saved)
- **Command Line Support**: Headless PDF extraction and creation

### Command Line Usage
```
PDF_Create_Export_Edit.exe --extract-pdf <file.pdf>
PDF_Create_Export_Edit.exe --edit-pdf <file.pdf>
PDF_Create_Export_Edit.exe --edit-image <image.png>
PDF_Create_Export_Edit.exe --make-pdf <image.png>
PDF_Create_Export_Edit.exe --combine-pdf <img1.png> <img2.png> ...
PDF_Create_Export_Edit.exe --edit-multi <img1.png> <img2.png> ...
PDF_Create_Export_Edit.exe --extract-pdf-gui <file.pdf>
```

### Requirements
- Windows 10 or later
- Python 3.14+ (for development)
- Dependencies: `PyMuPDF`, `Pillow`, `PyInstaller` (for building)

### Build
```bash
pip install PyMuPDF Pillow PyInstaller
python -m PyInstaller PDF_Create_Export_Edit.spec
```

### Contact
Software: Asri Akdeniz  
Mail: asriakdeniz@gmail.com
