from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PIL import Image

# check if [a1, a2] and [b1, b2] overlap
def _intervals_overlap(a1, a2, b1, b2):
    if (a1 > b1) and (a1 < b2):
        return True
    if (a2 > b1) and (a2 < b2):
        return True
    return False

# check if two rects (x1, y1, w1, h1) and (x2, y2, w2, h2) overlap
def _extended_boards_overlap(eb1, eb2):
    x1, y1, w1, h1 = eb1.get_border_rect()
    x2, y2, w2, h2 = eb2.get_border_rect()
    if _intervals_overlap(x1, x1+w1, x2, x2+w2) and _intervals_overlap(y1, y1+h1, y2, y2+h2):
        return True
    return False

# check if [a1, a2] is inside [b1, b2]
def _interval_inside_interval(a1, a2, b1, b2):
    if a1 > b1 and a2 < b2:
        return True
    return False

# check if rect (x1, y1, w1, h1) is inside rect (x, y, w, h)
def _extended_board_inside_rect(eb, x, y, w, h):
    x1, y1, w1, h1 = eb.get_border_rect()
    if _interval_inside_interval(x1, x1+w1, x, x+w) and _interval_inside_interval(y1, y1+h1, y, y+h):
        return True
    return False

def _draw_extended_board(canvas, eb, margin_x_m, margin_y_m):
    img_reader = ImageReader(Image.fromarray(eb.img))
    # draw image
    x, y, w, h = eb.get_board_rect()
    x = (x+margin_x_m)*1000*mm
    y = (y+margin_y_m)*1000*mm
    w = w*1000*mm
    h = h*1000*mm
    canvas.drawImage(img_reader, x, y, w, h, mask='auto')
    # draw border
    x, y, w, h = eb.get_border_rect()
    x = (x+margin_x_m)*1000*mm
    y = (y+margin_y_m)*1000*mm
    w = w*1000*mm
    h = h*1000*mm
    canvas.setLineWidth(1)
    canvas.rect(x, y, w, h)


def create_charuco_boards_pdf(eb_list, margin_x_m=0.01, margin_y_m=0.01, tol_mm=1e-3, filename="charuco_boards_A4.pdf"):
    # for Path objects, convert filename to string
    filename = str(filename)
    # page dimensions
    page_w_pt, page_h_pt = A4
    page_w_mm, page_h_mm = page_w_pt/mm, page_h_pt/mm
    page_w_m, page_h_m = page_w_mm/1000, page_h_mm/1000
    # check if all boards fit in page with given margins 
    for i, eb in enumerate(eb_list):
        if not _extended_board_inside_rect(eb, 0-tol_mm/1000, 0-tol_mm/1000, page_w_m-2*margin_x_m+tol_mm/1000, page_h_m-2*margin_y_m+tol_mm/1000):
            raise ValueError(f"board {i} does not fit in the content area defined by the page size and the margins.")
    
    # check if boards overlap
    for i in range(len(eb_list)):
        for j in range(i+1, len(eb_list)):
            eb_i = eb_list[i]
            eb_j = eb_list[j]
            if _extended_boards_overlap(eb_i, eb_j):
                raise ValueError(f"boards {i} and {j} overlap.")
    
    # create PDF
    c = canvas.Canvas(filename, pagesize=A4)
    # draw each board
    for i, eb in enumerate(eb_list):
        _draw_extended_board(c, eb, margin_x_m, margin_y_m)
    c.save()
    print(f"saved {filename}.")