import fitz
import os

# 转为2k,用于未闭合区域检测
def pdf2image_2k(pdfPath):
    square_size = 2048

    (filepath, filename) = os.path.split(pdfPath)
    (shotname, extension) = os.path.splitext(filename)

    # 打开PDF文件
    pdf = fitz.open(pdfPath)
    # 逐页读取PDF
    for pg in range(0, pdf.pageCount):
        page = pdf[pg]
        r = page.rect

        zoom_ratio = square_size / r.width

        # 设置缩放和旋转系数
        trans = fitz.Matrix(zoom_ratio, zoom_ratio)
        pm = page.get_pixmap(matrix=trans, alpha=False)
        # 开始写图像,保存在当前文件夹中
        save_file = filepath+"\\"+shotname+".png"
        pm.save(save_file)

    pdf.close()
    return save_file


