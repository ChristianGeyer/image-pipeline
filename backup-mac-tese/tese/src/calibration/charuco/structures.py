import cv2

#---------------#
# CharucoBoard class
#---------------#
class CharucoBoardInfo:
    def __init__(self, squaresX, squaresY, squareLength, markerLength, dict_name):
        self.squaresX = squaresX
        self.squaresY = squaresY
        self.squareLength = squareLength
        self.markerLength = markerLength
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dict_name))
        self.initialize_charuco()

    def initialize_charuco(self):
        self.charuco = cv2.aruco.CharucoBoard(
            size=(self.squaresX, self.squaresY),
            squareLength=self.squareLength,
            markerLength=self.markerLength,
            dictionary=self.aruco_dict
        )
        self.board_w_m = self.squaresX * self.squareLength
        self.board_h_m = self.squaresY * self.squareLength

#---------------#
# ExtendedCharucoBoard class
#---------------#
class ExtendedCharucoBoardInfo():
    def __init__(self, board, x_center_m=0.0, y_center_m=0.0, border_w_m=0.170, border_h_m=0.170, px_per_mm=25, tol_mm = 1e-3):
        self.board = board
        self.x_center_m = x_center_m
        self.y_center_m = y_center_m
        self.border_w_m = border_w_m
        self.border_h_m = border_h_m
        self.board_w_m = self.board.board_w_m
        self.board_h_m = self.board.board_h_m
        self.charuco = self.board.charuco
        self.px_per_mm = px_per_mm
        self.img = self.board.charuco.generateImage((int(self.board.board_w_m*1000*self.px_per_mm), int(self.board.board_h_m*1000*self.px_per_mm)), self.px_per_mm/1000)
        # check if board dimensions are too large for border dimensions
        if self.board_w_m > self.border_w_m+tol_mm/1000:
            raise ValueError(f"border_w_m={self.border_w_m} is too small to fit board with width={self.board_w_m}")
        if self.board_h_m > self.border_h_m+tol_mm/1000:
            raise ValueError(f"border_h_m={self.border_h_m} is too small to fit board with height={self.board_h_m}")

    # set center coordinates of the board in meters
    def set_center(self, x_center_m, y_center_m):
        self.x_center_m = x_center_m
        self.y_center_m = y_center_m

    # set border dimensions in meters
    def set_border(self, border_w_m, border_h_m):
        self.border_w_m = border_w_m
        self.border_h_m = border_h_m

    # get the bounding rect of the board in meters, defined by (x, y, w, h)
    def get_board_rect(self):
        x = self.x_center_m - self.board_w_m/2
        y = self.y_center_m - self.board_h_m/2
        w = self.board_w_m
        h = self.board_h_m
        return x, y, w, h

    # get the bounding rect of the border in meters, defined by (x, y, w, h)
    def get_border_rect(self):
        x = self.x_center_m - self.border_w_m/2
        y = self.y_center_m - self.border_h_m/2
        w = self.border_w_m
        h = self.border_h_m
        return x, y, w, h