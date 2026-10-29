
import cv2
import os

ROOT = '/root/Desktop/pictures'
FACES = '/root/Desktop/faces'
TRAIN = '/root/Desktop/training'


def detect(srcdir=ROOT, tgdir=FACES, train_dir=TRAIN):
    os.makedirs(tgdir, exist_ok=True)

    training = os.path.join(
        train_dir, 'haarcascade_frontalface_alt.xml'
    )
    cascade = cv2.CascadeClassifier(training)

    if cascade.empty():
        print(f'Could not load cascade file: {training}')
        return

    for fname in os.listdir(srcdir):
        if not fname.upper().endswith('.JPG'):
            continue

        fullname = os.path.join(srcdir, fname)
        newname = os.path.join(tgdir, fname)

        img = cv2.imread(fullname)
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rects = cascade.detectMultiScale(gray, 1.3, 5)

        if len(rects) == 0:
            print(f'No faces found in {fname}.')
            continue

        print(f'Got a face in {fname}')

        # Convert (x, y, width, height) to corner coordinates
        rects[:, 2:] += rects[:, :2]

        # Highlight the faces in the image
        for x1, y1, x2, y2 in rects:
            cv2.rectangle(img, (x1, y1), (x2, y2),
                          (127, 255, 0), 2)

        cv2.imwrite(newname, img)


if __name__ == '__main__':
    detect()
