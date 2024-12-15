import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

filename = "prova_uab_liceu.png"

image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
print(image.shape)
_, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Dilation
kernel_height = 50  # Adjust height based on your requirements
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_height))
dilated = cv2.dilate(binary, kernel, iterations=1)
binary = dilated


print(binary.shape)

horizontal_projection = np.sum(binary, axis=1)

print(horizontal_projection.shape)

plt.figure(figsize=(10, 4)) 
plt.plot(horizontal_projection, color='blue')
plt.savefig("horizontal_projection.png", dpi=300, bbox_inches="tight") 
plt.close()

'''smoothed_projection = gaussian_filter(horizontal_projection, sigma=3)
horizontal_projection = smoothed_projection

plt.figure(figsize=(10, 4)) 
plt.plot(smoothed_projection, color='blue')
plt.savefig("smoothed_protection.png", dpi=300, bbox_inches="tight") 
plt.close()'''

threshold = np.mean(horizontal_projection) / 2  # Potser canviar a horizontal_projection
staff_bounds = np.where(horizontal_projection > threshold)[0]

print(staff_bounds.shape)
print(staff_bounds)

staffs = []
current_staff = []
for i in range(1, len(staff_bounds)):
    if staff_bounds[i] == staff_bounds[i - 1] + 1:
        current_staff.append(staff_bounds[i])
    else:
        staffs.append((current_staff[0], current_staff[-1]))
        current_staff = [staff_bounds[i]]
if current_staff:
    staffs.append((current_staff[0], current_staff[-1]))

staffs_np = np.array(staffs)
print(staffs_np.shape)
print(staffs)
max_height = int((staffs[0][1] + staffs[1][0])/2)
print(max_height)


image = cv2.imread(filename, cv2.IMREAD_COLOR)
staff_image = image[:max_height, :, :]
cv2.imwrite(f"prova_uab_liceu_tallada.png", staff_image)


