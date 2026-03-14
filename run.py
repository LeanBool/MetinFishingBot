import numpy as np
import cv2
import time

import mouse
import keyboard
from pymouse import PyMouse
from pykeyboard import PyKeyboard

from PIL import Image
from mss import mss

from selector import capture_screen_region

while not keyboard.is_pressed('q'):
	pass

region = capture_screen_region()
rect_fishing = {"left": region.x1, "top": region.y1, "width": region.x2 - region.x1, "height": region.y2 - region.y1}

while not keyboard.is_pressed('q'):
	pass

region = capture_screen_region()
center = np.array([region.x1 + (region.x2 - region.x1)//2, region.y1 + (region.y2 - region.y1)//2])
radius = min(region.x2 - region.x1, region.y2 - region.y1)//2

# vid_writer = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'XVID'), 200.0, (128, 128), 0)

last_seen_timeout = 0.5
t_last_seen = time.time()

click_cooldown = 0.075
t_last_click = time.time()

fishing_cooldown = 4.0
m = PyMouse()
k = PyKeyboard()

with mss() as sct:
	while True:
		mouse_pos = None

		fish_found = False

		img = np.array(sct.grab(rect_fishing))
		img = img[:, :, 0]

		ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
		kernel = np.ones((3,3),np.uint8)
		img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=2)
		img = cv2.dilate(img, kernel*2)
		contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		if len(contours) == 1:
			x, y, w, h = cv2.boundingRect(contours[0])
			cv2.rectangle(img, (x, y), (x + w, y + h), (127), 1)
			fish_found = w*h < rect_fishing["width"]*rect_fishing["height"] // 2
		if fish_found:
			t_last_seen = time.time()
			mouse_src = np.array(mouse.get_position())
			mouse_dest = np.array((rect_fishing["left"] + x + w//2, rect_fishing["top"] + y + h//2))
			duration = 0.1
			mouse.drag(*mouse_src, *mouse_dest, duration=duration)
			if time.time() - t_last_click >= click_cooldown and np.linalg.norm(mouse_src - center) <= radius:
				m.click(*mouse.get_position(), 1)
				t_last_click = time.time()

		if not fish_found or time.time() - t_last_seen > last_seen_timeout:
			img = np.zeros_like(img)
			img = cv2.putText(img, "No fish", (rect_fishing["width"]//8, rect_fishing["height"]//3), cv2.FONT_HERSHEY_SIMPLEX, 0.75 * rect_fishing["width"]/128, (255,), 2)
			img = cv2.putText(img, "found", (rect_fishing["width"]//4, 3*rect_fishing["height"]//5), cv2.FONT_HERSHEY_SIMPLEX, 0.75 * rect_fishing["width"]/128, (255,), 2)
		if time.time() - t_last_seen > fishing_cooldown:
			k.tap_key(k.space)
			t_last_seen = time.time()
		cv2.imshow("feesh", cv2.resize(img, (0, 0), fx=2.0, fy=2.0))
		cv2.namedWindow('feesh',cv2.WND_PROP_FULLSCREEN)
		cv2.setWindowProperty('feesh', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
		# vid_writer.write(img)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			cv2.destroyAllWindows()
			# vid_writer.release()
			break

