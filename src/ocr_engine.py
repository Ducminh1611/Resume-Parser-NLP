import os
import re
import json
import spacy
from tika import parser

class ResumeParserPipeline:
    def __init__(self, model_path):
        """Khởi tạo Pipeline và nạp 'bộ não' AI vào bộ nhớ."""
        print(f" Đang khởi động AI từ: {model_path}...")
        try:
            self.nlp = spacy.load(model_path)
            print(" AI đã sẵn sàng!")
        except Exception as e:
            print(f" Lỗi khi tải mô hình: {e}")
            self.nlp = None

    def _extract_text(self, pdf_path):
        """Sử dụng Apache Tika để đọc PDF thành Text."""
        try:
            parsed_pdf = parser.from_file(pdf_path)
            text = parsed_pdf.get('content', '')
            if not text:
                return ""
            
            # Làm sạch text cơ bản
            text = re.sub(r'\n+', '\n', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception as e:
            print(f"❌ Lỗi khi đọc PDF {pdf_path}: {e}")
            return ""

    def process_resume(self, pdf_path):
        """Hàm chính: Xử lý End-to-End một file CV."""
        print(f"\n Đang xử lý: {os.path.basename(pdf_path)}")
        
        # 1. Trích xuất Text
        raw_text = self._extract_text(pdf_path)
        if not raw_text:
            return {"status": "error", "message": "Không thể trích xuất text."}

        # 2. Đưa Text cho AI bóc tách
        if not self.nlp:
            return {"status": "error", "message": "Mô hình AI chưa được tải."}
            
        doc = self.nlp(raw_text)
        
        # 3. Đóng gói kết quả thành JSON có cấu trúc
        entities_extracted = []
        for ent in doc.ents:
            entities_extracted.append({
                "label": ent.label_,
                "value": ent.text
            })

        result = {
            "status": "success",
            "file_name": os.path.basename(pdf_path),
            "text_length": len(raw_text),
            "entities": entities_extracted
        }
        
        return result

if __name__ == "__main__":
    # Đảm bảo bạn đang chạy file này từ thư mục gốc của dự án (Resume_Parser_Project)
    MODEL_DIR = "models/model-best"
    
    # Khởi tạo hệ thống
    parser_system = ResumeParserPipeline(model_path=MODEL_DIR)
    
    # Đọc thử một file PDF có trong thư mục data/raw/
    # (Bạn hãy chắc chắn trong folder data/raw/ có 1 file PDF tên là sample_cv.pdf nhé)
    TEST_PDF = "data/raw/sample_cv.pdf"
    
    if os.path.exists(TEST_PDF):
        final_result = parser_system.process_resume(TEST_PDF)
        
        print("\n KẾT QUẢ ĐẦU RA (JSON FORMAT DÀNH CHO DATA LAKE):")
        # In ra định dạng JSON đẹp mắt
        print(json.dumps(final_result, indent=4, ensure_ascii=False))
        
        # Lưu kết quả ra file JSON vào thư mục processed
        os.makedirs("data/processed", exist_ok=True)
        output_file = f"data/processed/{os.path.basename(TEST_PDF)}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=4, ensure_ascii=False)
        print(f"\n Đã lưu kết quả tại: {output_file}")
    else:
        print(f" Không tìm thấy file {TEST_PDF} để test. Hãy copy 1 file PDF vào đó nhé!")
