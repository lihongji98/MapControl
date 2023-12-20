import json
import PIL.Image
import matplotlib.pyplot as plt
import numpy as np


def get_map_mask(img_path):
    img = np.array(PIL.Image.open(img_path))

    def process(process_img, mapName):
        if mapName == "mirage":
            paraList = [[1, 19, 48], [1, 66, 39], [70, 14, 34], [800, 1000], [0, 250]]
        elif mapName == "inferno":
            paraList = [[6, 69, 36], [8, 22, 45], [74, 16, 33], [0, 300], [0, 300]]
        else:
            ValueError("choose 'inferno'!")
        for x in range(len(process_img)):
            for y in range(len(process_img[x])):
                if (process_img[x][y][0] == paraList[0][0] and process_img[x][y][1] == paraList[0][1] and
                    process_img[x][y][2] == paraList[0][2]) or \
                        (process_img[x][y][0] == paraList[1][0] and process_img[x][y][1] == paraList[1][1] and
                         process_img[x][y][2] == paraList[1][2]) or \
                        (process_img[x][y][0] == paraList[2][0] and process_img[x][y][1] == paraList[2][1] and
                         process_img[x][y][2] == paraList[2][2]):
                    process_img[x][y][0], process_img[x][y][1], process_img[x][y][2], process_img[x][y][
                        3] = 255, 255, 255, 255
        for x in range(paraList[3][0], paraList[3][1]):
            for y in range(paraList[4][0], paraList[4][1]):
                process_img[x][y][0], process_img[x][y][1], process_img[x][y][2] = 0, 0, 0
        return process_img

    img = process(img, "de_inferno")

    grey_image = np.array(PIL.Image.fromarray(img).convert("L"))
    for i in range(len(grey_image)):
        for j in range(len(grey_image[i])):
            if grey_image[i][j] != 0 and grey_image[i][j] != 255:
                grey_image[i][j] = 0

    mask = grey_image.tolist()
    json_filename = img_path[3: -4] + ".json"
    with open(json_filename, 'w') as json_file:
        json.dump(mask, json_file)


# get_map_mask("mapMetaData/de_inferno.png")

with open("D:\pycharm_projects\CSGO_Analytics\Maps\mapMetaData\infernoMask.json", ) as f:
    # Load JSON data from file
    data = json.load(f)

data = np.array(data)
plt.imshow(data, cmap="gray")
plt.show()
