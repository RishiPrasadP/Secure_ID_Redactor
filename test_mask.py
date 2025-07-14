import cv2, pytesseract, re
img = cv2.imread("uploads/sample_id.jpg")
data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

for i, word in enumerate(data['text']):
    if re.fullmatch(r'\d{3}-\d{2}-\d{4}', word):
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)

cv2.imwrite("uploads/masked_test.png", img)
