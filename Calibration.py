import cv2
import numpy as np
import os

def get_image_paths(folder_path):
    # 获取文件夹中的所有图像文件路径
    image_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith(('.jpg', '.jpeg', '.png'))]
    return image_paths

def cal_real_corner(corner_height, corner_width, square_size):
    '''
    根据标定板信息获得世界坐标
    :param corner_height:棋盘格长边角点数量
    :param corner_width: 棋盘格宽边角点数量
    :param square_size: 棋盘格尺寸/mm
    :return:世界坐标
    '''
    obj_corner = np.zeros([corner_height * corner_width, 3], np.float32)
    obj_corner[:, :2] = np.mgrid[0:corner_height, 0:corner_width].T.reshape(-1, 2)  # (w*h)*2
    return obj_corner * square_size

def compute_H(vP1, vP2):
    '''
    根据世界坐标和图像坐标的对应关系计算单应矩阵
    :param vP1: 世界坐标
    :param vP2: 图像坐标
    :return: 单应矩阵
    '''
    N = len(vP1)

    A = np.zeros((2 * N, 9), dtype=np.float32)

    for i in range(N):
        u1, v1 = vP1[i]
        u2, v2 = vP2[i]

        A[2 * i, 0:3] = [0.0, 0.0, 0.0]
        A[2 * i, 3:6] = [-u1, -v1, -1]
        A[2 * i, 6:9] = [v2 * u1, v2 * v1, v2]

        A[2 * i + 1, 0:3] = [u1, v1, 1]
        A[2 * i + 1, 3:6] = [0.0, 0.0, 0.0]
        A[2 * i + 1, 6:9] = [-u2 * u1, -u2 * v1, -u2]

    _, _, vt = np.linalg.svd(A, full_matrices=True)

    return vt[8, :].reshape((3, 3))

def calculationHomography(img_path,corner_height,corner_width,square_size):
    '''
    计算单应矩阵
    :param corner_height:棋盘格高边角点数量
    :param corner_width: 棋盘格宽边角点数量
    :param square_size: 棋盘格尺寸/mm
    :param img_path: 图像路径
    :return:
    '''

    corner_width  = corner_width
    corner_height = corner_height

    square_size = square_size

    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, img_corners = cv2.findChessboardCorners(gray, (corner_width, corner_height))

    # 生成48个点的坐标
    points = img_corners.squeeze()


    obj_corner = cal_real_corner(corner_width, corner_height, square_size)
    obj_corner = obj_corner[:, 0:2]

    myH = compute_H(obj_corner, points)
    new_myH = (1 / myH[2, 2]) * myH
    return new_myH,points


def compute_K(H_matrices):
    '''
    分解单应矩阵来获得内参
    :param H_matrices: n*3的单应矩阵
    :return: 内参
    '''
    n = len(H_matrices)
    onemat = np.zeros((2 * n, 6))

    for i in range(n):
        H = H_matrices[i]
        onemat[2*i, 0] = H[0, 0] * H[0, 1]
        onemat[2*i, 1] = H[0, 0] * H[1, 1] + H[0, 1] * H[1, 0]
        onemat[2*i, 2] = H[0, 1] * H[2, 0] + H[2, 1] * H[0, 0]
        onemat[2*i, 3] = H[1, 0] * H[1, 1]
        onemat[2*i, 4] = H[1, 1] * H[2, 0] + H[2, 1] * H[1, 0]
        onemat[2*i, 5] = H[2, 0] * H[2, 1]

        onemat[2*i+1, 0] = H[0, 0] ** 2 - H[0, 1] ** 2
        onemat[2*i+1, 1] = 2 * (H[0, 0] * H[1, 0] - H[0, 1] * H[1, 1])
        onemat[2*i+1, 2] = 2 * (H[0, 0] * H[2, 0] - H[0, 1] * H[2, 1])
        onemat[2*i+1, 3] = H[1, 0] ** 2 - H[1, 1] ** 2
        onemat[2*i+1, 4] = 2 * (H[1, 0] * H[2, 0] - H[1, 1] * H[2, 1])
        onemat[2*i+1, 5] = H[2, 0] ** 2 - H[2, 1] ** 2

    _, _, V = np.linalg.svd(onemat)
    null_space = V[-1, :]

    B = np.zeros((3, 3))
    B[0, 0] = null_space[0]
    B[0, 1] = null_space[1]
    B[0, 2] = null_space[2]
    B[1, 0] = null_space[1]
    B[1, 1] = null_space[3]
    B[1, 2] = null_space[4]
    B[2, 0] = null_space[2]
    B[2, 1] = null_space[4]
    B[2, 2] = null_space[5]

    v0 = ((B[0, 1] * B[0, 2]) - (B[0, 0] * B[1, 2])) / ((B[0, 0] * B[1, 1]) - (B[0, 1] ** 2))
    lambda1 = B[2, 2] - (((B[0, 2] ** 2) + (v0 * (B[0, 1] * B[0, 2] - B[1, 1] * B[1, 2]))) / B[0, 0])
    fx = np.sqrt(lambda1 / B[0, 0])
    fy = np.sqrt((lambda1 * B[0, 0]) / ((B[0, 0] * B[1, 1]) - (B[0, 1] ** 2)))
    c = -(B[0, 1] * (fx ** 2) * fy) / lambda1
    u0 = ((c * v0) / fy) - ((B[0, 2] * (fx ** 2)) / lambda1)
    K = np.zeros((3, 3))

    K[0, 0] = fx
    K[0, 1] = c
    K[0, 2] = u0
    K[1, 1] = fy
    K[1, 2] = v0
    K[2, 2] = 1
    return K,lambda1

def compute_RT(H_matrices,K,lambda1):
    '''
    分解单应矩阵得到的外参矩阵
    :param H_matrices: 单应矩阵
    :param K: 内参矩阵
    :param lambda1: 尺度系数
    :return: 外参
    '''
    n = len(H_matrices)
    RT_matrices = []
    K_n = np.linalg.inv(K)
    for i in range(n):
        H = H_matrices[i]
        r1 = (lambda1 * np.dot(K_n, H[:, 0])).reshape(-1, 1)
        r2 = (lambda1 * np.dot(K_n, H[:, 1])).reshape(-1, 1)
        r3 = np.cross(r1[:, 0], r2[:, 0]).reshape(-1, 1)
        t = (lambda1 * np.dot(K_n, H[:, 2])).reshape(-1, 1)
        RT = np.hstack([r1, r2, r3, t])
        RT = np.vstack([RT, [0, 0, 0, 1]])
        RT_matrices.append(RT)
    return RT_matrices

def reprojectError(K,RT_mats,img_points,w,h,s):
    '''
    根据计算来的内参和外参来计算重投影误差
    :param K: 相机内参
    :param RT_mats: 相机外参
    :param img_points: 图像坐标（角点）
    :param w: 标定板宽
    :param h: 标定板长
    :param s: 标定板单格尺寸
    :return: 平均重投影误差
    '''
    obj_corners = cal_real_corner(w, h, s)
    n = len(RT_mats)
    distances = []
    for i in range(n):
        reprojectlist = []
        for j in range(h * w):
            obj_corner = np.append(obj_corners[j], 1).reshape(-1, 1)
            RT_mat = RT_mats[i]
            reprojectPoint = K @ RT_mat @ obj_corner
            reprojectPoint = reprojectPoint / reprojectPoint[2]
            reprojectPoint = reprojectPoint[:2, :].reshape(-1, 2)
            reprojectlist.append(reprojectPoint)
        reprojectlist = np.array(reprojectlist).reshape(h * w, 2)
        img_point = img_points[i]
        distance = np.mean(np.sqrt(np.sum((img_point - reprojectlist) ** 2, axis=1)))
        distances.append(distance)
    dis = np.mean(distances)
    return dis


