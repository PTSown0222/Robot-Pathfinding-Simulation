# -*- coding: utf-8 -*-
"""
Mô tả: Tìm đường đi ngắn nhất từ Start đến Goal trong bản đồ lưới 2D
"""
import sys
import io

# Thiết lập encoding UTF-8 cho console (hỗ trợ tiếng Việt)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


# Cell Types
CELL_NORMAL = 0      # Normal cell, cost = 1
CELL_WALL = 1        # Wall, impassable
CELL_START = 2       # Start point
CELL_END = 3         # End point
CELL_TRAP = 4        # High cost/Trap, cost = 5
CELL_ROAD = 5        # Low cost/Road, cost = 0.5


class Node:
    """
    Lớp Node: Đại diện cho một nút trong bản đồ lưới
    
    Thuộc tính:
        - row, col: Tọa độ của nút trong bản đồ (hàng, cột)
        - cell_type: Loại cell (NORMAL, WALL, START, END, TRAP, ROAD)
        - weight: Chi phí di chuyển qua cell này (1 cho normal, 5 cho trap, 0.5 cho road)
        - parent: Nút cha (để truy vết đường đi)
        - g_score: Chi phí thực tế từ Start đến nút hiện tại
        - h_score: Chi phí ước tính (heuristic) từ nút hiện tại đến Goal
        - f_score: Tổng chi phí f = g + h (dùng để sắp xếp trong thuật toán A*)
    """
    
    def __init__(self, row, col, cell_type=CELL_NORMAL, parent=None):
        self.row = row          # Hàng trong bản đồ
        self.col = col          # Cột trong bản đồ
        self.cell_type = cell_type  # Loại cell
        self.parent = parent    # Nút cha (để truy vết đường đi)
        self.g_score = 0        # Chi phí thực tế từ Start đến nút này
        self.h_score = 0        # Chi phí ước tính (heuristic) từ nút này đến Goal
        self.f_score = 0        # Tổng chi phí f = g + h
        
        # Tính weight dựa trên cell_type
        if cell_type == CELL_WALL:
            self.weight = float('inf')  # Không thể đi qua
        elif cell_type == CELL_TRAP:
            self.weight = 5.0  # Chi phí cao
        elif cell_type == CELL_ROAD:
            self.weight = 0.5  # Chi phí thấp
        else:  # NORMAL, START, END
            self.weight = 1.0  # Chi phí bình thường
    
    def is_passable(self):
        """Kiểm tra xem có thể đi qua cell này không"""
        return self.cell_type != CELL_WALL
    
    def __eq__(self, other):
        """So sánh 2 nút: bằng nhau nếu cùng tọa độ"""
        return self.row == other.row and self.col == other.col
    
    def __lt__(self, other):
        """So sánh để sắp xếp: nút có f_score nhỏ hơn sẽ được ưu tiên"""
        return self.f_score < other.f_score
    
    def __repr__(self):
        """Hiển thị thông tin nút khi in ra"""
        return f"Node({self.row}, {self.col}, type={self.cell_type}, weight={self.weight}, f={self.f_score})"


class AStarRobot:
    """
    Lớp AStarRobot: Chứa logic tìm đường bằng thuật toán A*
    
    Thuật toán A* hoạt động:
        1. Mở rộng nút có f_score nhỏ nhất
        2. f_score = g_score + h_score
           - g_score: Chi phí thực tế từ Start đến nút hiện tại
           - h_score: Chi phí ước tính từ nút hiện tại đến Goal (Manhattan Distance)
        3. Khi đến Goal, truy vết đường đi ngược lại qua parent
    """
    
    def __init__(self, room_map, start, goal, allow_diagonal=False):
        """
        Khởi tạo robot với bản đồ và điểm bắt đầu/kết thúc
        
        Args:
            room_map: Ma trận 2D đại diện cho bản đồ (0=đi được, 1=vật cản)
            start: Tuple (row, col) điểm bắt đầu
            goal: Tuple (row, col) điểm đích
            allow_diagonal: True nếu cho phép đi chéo (8 hướng), False nếu chỉ 4 hướng
        """
        self.room_map = room_map        # Bản đồ phòng
        self.rows = len(room_map)       # Số hàng
        self.cols = len(room_map[0])    # Số cột
        self.start = start              # Điểm bắt đầu (row, col)
        self.goal = goal                # Điểm đích (row, col)
        self.allow_diagonal = allow_diagonal  # Cho phép đi chéo hay không
        
        # 4 hướng di chuyển cơ bản: Lên, Xuống, Trái, Phải
        self.directions_4 = [
            (-1, 0, 1.0),  # Lên (giảm hàng), chi phí = 1
            (1, 0, 1.0),   # Xuống (tăng hàng), chi phí = 1
            (0, -1, 1.0),  # Trái (giảm cột), chi phí = 1
            (0, 1, 1.0)    # Phải (tăng cột), chi phí = 1
        ]
        
        # 8 hướng di chuyển (bao gồm cả đường chéo)
        # Chi phí đường chéo = √2 ≈ 1.414
        import math
        diagonal_cost = math.sqrt(2)
        self.directions_8 = [
            (-1, 0, 1.0),      # Lên
            (1, 0, 1.0),       # Xuống
            (0, -1, 1.0),      # Trái
            (0, 1, 1.0),       # Phải
            (-1, -1, diagonal_cost),  # Lên-Trái (chéo)
            (-1, 1, diagonal_cost),   # Lên-Phải (chéo)
            (1, -1, diagonal_cost),   # Xuống-Trái (chéo)
            (1, 1, diagonal_cost)     # Xuống-Phải (chéo)
        ]
        
        # Chọn hướng di chuyển dựa trên allow_diagonal
        self.directions = self.directions_8 if allow_diagonal else self.directions_4
    
    def manhattan_distance(self, row1, col1, row2, col2):
        """
        Tính khoảng cách Manhattan giữa 2 điểm
        
        Công thức: |row1 - row2| + |col1 - col2|
        
        Manhattan Distance phù hợp với di chuyển 4 hướng vì:
        - Đây là khoảng cách thực tế tối thiểu khi chỉ đi Lên/Xuống/Trái/Phải
        - Luôn admissible (không bao giờ đánh giá quá cao) → đảm bảo tìm được đường tối ưu
        - Tính toán nhanh hơn Euclidean (không cần căn bậc 2)
        
        Args:
            row1, col1: Tọa độ điểm 1
            row2, col2: Tọa độ điểm 2
        
        Returns:
            Khoảng cách Manhattan (số thực)
        """
        return abs(row1 - row2) + abs(col1 - col2)
    
    def euclidean_distance(self, row1, col1, row2, col2):
        """
        Tính khoảng cách Euclidean giữa 2 điểm
        
        Công thức: √((row1 - row2)² + (col1 - col2)²)
        
        Euclidean Distance phù hợp với di chuyển 8 hướng (có chéo) vì:
        - Đây là khoảng cách đường thẳng thực tế
        - Luôn admissible (không bao giờ đánh giá quá cao) → đảm bảo tìm được đường tối ưu
        - Phản ánh chính xác chi phí khi có thể đi chéo
        
        Args:
            row1, col1: Tọa độ điểm 1
            row2, col2: Tọa độ điểm 2
        
        Returns:
            Khoảng cách Euclidean (số thực)
        """
        import math
        return math.sqrt((row1 - row2) ** 2 + (col1 - col2) ** 2)
    
    def is_valid(self, row, col):
        """
        Kiểm tra xem ô (row, col) có hợp lệ để đi vào không
        
        Điều kiện:
            - Nằm trong phạm vi bản đồ (0 <= row < rows, 0 <= col < cols)
            - Không phải vật cản (room_map[row][col] == 0)
        
        Args:
            row, col: Tọa độ cần kiểm tra
        
        Returns:
            True nếu ô hợp lệ, False nếu không
        """
        # Kiểm tra nằm trong phạm vi bản đồ
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        
        # Kiểm tra không phải vật cản (0 = đi được, 1 = vật cản)
        if self.room_map[row][col] == 1:
            return False
        
        return True
    
    def get_neighbors(self, node):
        """
        Lấy danh sách các nút lân cận hợp lệ của nút hiện tại
        
        Hỗ trợ 4 hướng hoặc 8 hướng (tùy theo allow_diagonal)
        - 4 hướng: Lên, Xuống, Trái, Phải (chi phí = 1)
        - 8 hướng: Bao gồm cả 4 hướng chéo (chi phí = √2)
        
        Args:
            node: Nút hiện tại
        
        Returns:
            Danh sách các nút lân cận hợp lệ, mỗi nút có thông tin chi phí di chuyển
        """
        neighbors = []
        
        # Duyệt qua các hướng di chuyển (dr, dc, cost)
        for dr, dc, move_cost in self.directions:
            new_row = node.row + dr
            new_col = node.col + dc
            
            # Kiểm tra bounds: đảm bảo 0 <= new_row < rows và 0 <= new_col < cols
            if new_row < 0 or new_row >= self.rows or new_col < 0 or new_col >= self.cols:
                continue
            
            # Kiểm tra không phải vật cản
            if not self.is_valid(new_row, new_col):
                continue
            
            # Tạo nút mới với thông tin chi phí di chuyển
            neighbor = Node(new_row, new_col, parent=node)
            neighbor.move_cost = move_cost  # Lưu chi phí di chuyển đến nút này
            neighbors.append(neighbor)
        
        return neighbors
    
    def find_path(self):
        """
        Tìm đường đi từ Start đến Goal bằng thuật toán A*
        
        Thuật toán A*:
            1. Khởi tạo: Thêm Start vào open_set (danh sách nút cần xét)
            2. Lặp:
               a. Chọn nút có f_score nhỏ nhất từ open_set
               b. Nếu là Goal → tìm thấy đường đi, truy vết
               c. Thêm vào closed_set (đã xét)
               d. Xét các nút lân cận:
                  - Nếu chưa xét hoặc có đường đi tốt hơn → cập nhật và thêm vào open_set
            3. Nếu open_set rỗng → không tìm thấy đường đi
        
        Returns:
            Danh sách các nút từ Start đến Goal (đường đi), hoặc None nếu không tìm thấy
        """
        # Khởi tạo nút bắt đầu
        start_node = Node(self.start[0], self.start[1])
        start_node.g_score = 0  # Chi phí từ Start đến Start = 0
        
        # Chọn heuristic dựa trên allow_diagonal
        if self.allow_diagonal:
            start_node.h_score = self.euclidean_distance(
                start_node.row, start_node.col, 
                self.goal[0], self.goal[1]
            )
        else:
            start_node.h_score = self.manhattan_distance(
                start_node.row, start_node.col, 
                self.goal[0], self.goal[1]
            )
        
        start_node.f_score = start_node.g_score + start_node.h_score  # f = g + h
        
        # Danh sách nút cần xét (sắp xếp theo f_score)
        open_set = [start_node]
        
        # Danh sách nút đã xét (để tránh xét lại)
        closed_set = set()
        
        # Lặp cho đến khi tìm thấy Goal hoặc hết nút để xét
        while open_set:
            # Sắp xếp open_set theo f_score (nút có f_score nhỏ nhất ở đầu)
            open_set.sort()
            current = open_set.pop(0)  # Lấy nút có f_score nhỏ nhất
            
            # Đánh dấu đã xét
            closed_set.add((current.row, current.col))
            
            # Nếu đến Goal → tìm thấy đường đi
            if current.row == self.goal[0] and current.col == self.goal[1]:
                # Truy vết đường đi ngược lại qua parent
                path = []
                node = current
                while node is not None:
                    path.append((node.row, node.col))
                    node = node.parent
                path.reverse()  # Đảo ngược để có đường đi từ Start đến Goal
                return path
            
            # Xét các nút lân cận
            for neighbor in self.get_neighbors(current):
                neighbor_pos = (neighbor.row, neighbor.col)
                
                # Bỏ qua nếu đã xét
                if neighbor_pos in closed_set:
                    continue
                
                # Tính chi phí từ Start đến nút lân cận (qua nút hiện tại)
                # Chi phí phụ thuộc vào hướng di chuyển (1.0 cho 4 hướng, √2 cho chéo)
                move_cost = getattr(neighbor, 'move_cost', 1.0)  # Mặc định = 1.0
                tentative_g_score = current.g_score + move_cost
                
                # Kiểm tra xem nút lân cận đã có trong open_set chưa
                neighbor_in_open = False
                for node in open_set:
                    if node.row == neighbor.row and node.col == neighbor.col:
                        neighbor_in_open = True
                        # Nếu tìm thấy đường đi tốt hơn, cập nhật
                        if tentative_g_score < node.g_score:
                            node.parent = current
                            node.g_score = tentative_g_score
                            # Chọn heuristic dựa trên allow_diagonal
                            if self.allow_diagonal:
                                node.h_score = self.euclidean_distance(
                                    node.row, node.col, 
                                    self.goal[0], self.goal[1]
                                )
                            else:
                                node.h_score = self.manhattan_distance(
                                    node.row, node.col, 
                                    self.goal[0], self.goal[1]
                                )
                            node.f_score = node.g_score + node.h_score  # f = g + h
                        break
                
                # Nếu chưa có trong open_set, thêm vào
                if not neighbor_in_open:
                    neighbor.g_score = tentative_g_score
                    # Chọn heuristic dựa trên allow_diagonal
                    if self.allow_diagonal:
                        neighbor.h_score = self.euclidean_distance(
                            neighbor.row, neighbor.col, 
                            self.goal[0], self.goal[1]
                        )
                    else:
                        neighbor.h_score = self.manhattan_distance(
                            neighbor.row, neighbor.col, 
                            self.goal[0], self.goal[1]
                        )
                    neighbor.f_score = neighbor.g_score + neighbor.h_score  # f = g + h
                    open_set.append(neighbor)
        
        # Không tìm thấy đường đi
        return None


class Grid:
    """
    Lớp Grid: Quản lý lưới 2D các Node
    
    Thuộc tính:
        - rows, cols: Kích thước lưới
        - grid: Ma trận 2D các Node
        - start: Vị trí Start
        - end: Vị trí End
    """
    
    def __init__(self, rows=20, cols=20):
        """
        Khởi tạo Grid
        
        Args:
            rows: Số hàng (10-30)
            cols: Số cột (10-30)
        """
        self.rows = max(10, min(30, rows))
        self.cols = max(10, min(30, cols))
        self.grid = []
        self.start = None
        self.end = None
        
        # Khởi tạo grid với các Node NORMAL
        for row in range(self.rows):
            grid_row = []
            for col in range(self.cols):
                grid_row.append(Node(row, col, CELL_NORMAL))
            self.grid.append(grid_row)
    
    def get_node(self, row, col):
        """Lấy Node tại vị trí (row, col)"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None
    
    def set_cell_type(self, row, col, cell_type):
        """Đặt loại cell tại vị trí (row, col)"""
        node = self.get_node(row, col)
        if node:
            # Nếu đặt Start hoặc End, xóa Start/End cũ
            if cell_type == CELL_START:
                if self.start:
                    old_node = self.get_node(self.start[0], self.start[1])
                    if old_node:
                        old_node.cell_type = CELL_NORMAL
                self.start = (row, col)
            elif cell_type == CELL_END:
                if self.end:
                    old_node = self.get_node(self.end[0], self.end[1])
                    if old_node:
                        old_node.cell_type = CELL_NORMAL
                self.end = (row, col)
            
            node.cell_type = cell_type
            # Cập nhật weight
            if cell_type == CELL_WALL:
                node.weight = float('inf')
            elif cell_type == CELL_TRAP:
                node.weight = 5.0
            elif cell_type == CELL_ROAD:
                node.weight = 0.5
            else:
                node.weight = 1.0
    
    def get_neighbors(self, node, allow_diagonal=False):
        """
        Lấy danh sách các nút lân cận hợp lệ
        
        Args:
            node: Nút hiện tại
            allow_diagonal: True nếu cho phép đi chéo (8 hướng), False nếu chỉ 4 hướng
        
        Returns:
            List các tuple (neighbor_node, move_cost) với:
            - neighbor_node: Node lân cận
            - move_cost: Chi phí di chuyển (1.0 cho 4 hướng, √2 cho chéo)
        """
        import math
        neighbors = []
        
        # 4 hướng cơ bản: Lên, Xuống, Trái, Phải (chi phí = 1.0)
        directions_4 = [
            (-1, 0, 1.0),  # Lên
            (1, 0, 1.0),   # Xuống
            (0, -1, 1.0),  # Trái
            (0, 1, 1.0)    # Phải
        ]
        
        # 8 hướng (bao gồm cả đường chéo)
        diagonal_cost = math.sqrt(2)  # Chi phí đường chéo = √2 ≈ 1.414
        directions_8 = directions_4 + [
            (-1, -1, diagonal_cost),  # Lên-Trái (chéo)
            (-1, 1, diagonal_cost),   # Lên-Phải (chéo)
            (1, -1, diagonal_cost),   # Xuống-Trái (chéo)
            (1, 1, diagonal_cost)    # Xuống-Phải (chéo)
        ]
        
        # Chọn hướng di chuyển dựa trên allow_diagonal
        directions = directions_8 if allow_diagonal else directions_4
        
        for dr, dc, move_cost in directions:
            new_row = node.row + dr
            new_col = node.col + dc
            neighbor = self.get_node(new_row, new_col)
            if neighbor and neighbor.is_passable():
                # Trả về tuple (neighbor, move_cost) để thuật toán tính toán chính xác
                neighbors.append((neighbor, move_cost))
        
        return neighbors
    
    def reset_pathfinding_data(self):
        """Reset tất cả dữ liệu pathfinding (g_score, h_score, f_score, parent)"""
        for row in self.grid:
            for node in row:
                node.g_score = 0
                node.h_score = 0
                node.f_score = 0
                node.parent = None
    
    def has_path(self):
        """
        Kiểm tra xem có đường đi từ Start đến End không (sử dụng BFS đơn giản)
        
        Returns:
            True nếu có đường đi, False nếu không
        """
        if not self.start or not self.end:
            return False
        
        import collections
        
        start_node = self.get_node(self.start[0], self.start[1])
        end_node = self.get_node(self.end[0], self.end[1])
        
        if not start_node or not end_node:
            return False
        
        queue = collections.deque([start_node])
        visited = set()
        visited.add((start_node.row, start_node.col))
        
        while queue:
            current = queue.popleft()
            
            if current.row == end_node.row and current.col == end_node.col:
                return True
            
            # get_neighbors() trả về tuple (neighbor, move_cost)
            # move_cost không cần thiết cho has_path() (chỉ kiểm tra có đường đi hay không)
            for neighbor, _ in self.get_neighbors(current, allow_diagonal=False):
                pos = (neighbor.row, neighbor.col)
                if pos not in visited:
                    visited.add(pos)
                    queue.append(neighbor)
        
        return False
    
    @staticmethod
    def generate_random_map(min_size=10, max_size=30, wall_density=0.25, trap_density=0.15, road_density=0.1, max_attempts=10, energy_mode=True):
        """
        Tạo random map với đầy đủ cell types và đảm bảo có đường đi
        
        Thuật toán:
        1. Tạo kích thước ngẫu nhiên (10-30)
        2. Đặt Start và End ở 2 góc đối diện
        3. Tạo một đường đi guaranteed (L-shaped) để đảm bảo có đáp án
        4. Thêm walls, traps, roads ngẫu nhiên nhưng không chặn đường đi guaranteed
        5. Kiểm tra lại bằng BFS để đảm bảo có đường đi
        
        Args:
            min_size: Kích thước tối thiểu (mặc định 10)
            max_size: Kích thước tối đa (mặc định 30)
            wall_density: Mật độ walls (0.0-1.0, mặc định 0.25)
            trap_density: Mật độ traps (0.0-1.0, mặc định 0.15)
            road_density: Mật độ roads (0.0-1.0, mặc định 0.1)
            max_attempts: Số lần thử tối đa nếu không tìm được đường đi
        
        Returns:
            Grid object với map đã được tạo và đảm bảo có đường đi
        """
        import random
        
        for attempt in range(max_attempts):
            # Tạo kích thước ngẫu nhiên
            size = random.randint(min_size, max_size)
            grid = Grid(size, size)
            
            # Đặt Start và End ở 2 góc đối diện (tăng khoảng cách để test tốt hơn)
            # Có thể chọn: (0,0) -> (size-1, size-1) hoặc (0, size-1) -> (size-1, 0)
            corner_choice = random.random()
            if corner_choice < 0.5:
                start_pos = (0, 0)
                end_pos = (size - 1, size - 1)
            else:
                start_pos = (0, size - 1)
                end_pos = (size - 1, 0)
            
            # Đảm bảo Start và End không trùng nhau
            if start_pos == end_pos and size > 1:
                end_pos = (size - 1, size - 1)
            
            # Tạo đường đi cơ bản từ Start đến End (đảm bảo có đáp án)
            # Sử dụng L-shaped path: đi xuống rồi sang phải, hoặc sang phải rồi đi xuống
            guaranteed_path = []
            
            # Chọn một trong hai đường đi L-shaped
            if random.random() < 0.5:
                # Đi xuống trước, rồi sang phải
                for row in range(start_pos[0], end_pos[0] + 1):
                    guaranteed_path.append((row, start_pos[1]))
                for col in range(start_pos[1] + 1, end_pos[1] + 1):
                    guaranteed_path.append((end_pos[0], col))
            else:
                # Sang phải trước, rồi đi xuống
                for col in range(start_pos[1], end_pos[1] + 1):
                    guaranteed_path.append((start_pos[0], col))
                for row in range(start_pos[0] + 1, end_pos[0] + 1):
                    guaranteed_path.append((row, end_pos[1]))
            
            # Đặt Start và End
            grid.set_cell_type(start_pos[0], start_pos[1], CELL_START)
            grid.set_cell_type(end_pos[0], end_pos[1], CELL_END)
            
            # Đảm bảo đường đi guaranteed không bị chặn
            protected_cells = set(guaranteed_path)
            protected_cells.add(start_pos)
            protected_cells.add(end_pos)
            
            # Tạo danh sách tất cả các cells (trừ protected cells)
            all_cells = []
            for row in range(size):
                for col in range(size):
                    pos = (row, col)
                    if pos not in protected_cells:
                        all_cells.append(pos)
            
            # Shuffle để random
            random.shuffle(all_cells)
            
            # Tính số lượng cells cho mỗi loại
            total_cells = len(all_cells)
            num_walls = max(1, int(total_cells * wall_density))  # Đảm bảo có ít nhất 1 wall
            
            # Đặt walls
            for i in range(min(num_walls, len(all_cells))):
                row, col = all_cells[i]
                grid.set_cell_type(row, col, CELL_WALL)
            
            # Chỉ tạo traps và roads nếu energy_mode = True
            if energy_mode:
                num_traps = max(1, int(total_cells * trap_density))  # Đảm bảo có ít nhất 1 trap
                num_roads = max(1, int(total_cells * road_density))  # Đảm bảo có ít nhất 1 road
                
                # Đặt traps (sau walls) - đảm bảo có traps để test Energy vs Steps
                trap_start = num_walls
                for i in range(trap_start, min(trap_start + num_traps, len(all_cells))):
                    row, col = all_cells[i]
                    grid.set_cell_type(row, col, CELL_TRAP)
                
                # Đặt roads (sau traps) - đảm bảo có roads để test Energy optimization
                road_start = trap_start + num_traps
                for i in range(road_start, min(road_start + num_roads, len(all_cells))):
                    row, col = all_cells[i]
                    grid.set_cell_type(row, col, CELL_ROAD)
            
            # Các cells còn lại là NORMAL (đã được set mặc định)
            
            # Kiểm tra lại bằng BFS để đảm bảo có đường đi
            if grid.has_path():
                return grid
            
            # Nếu không có đường đi, giảm wall_density và thử lại
            wall_density *= 0.8
        
        # Nếu sau max_attempts vẫn không được, tạo map đơn giản nhưng vẫn có đủ cell types
        size = random.randint(min_size, max_size)
        grid = Grid(size, size)
        grid.set_cell_type(0, 0, CELL_START)
        grid.set_cell_type(size - 1, size - 1, CELL_END)
        
        # Thêm ít nhất một vài cells của mỗi loại để test
        if size > 2:
            # Thêm 1 wall
            grid.set_cell_type(size // 2, size // 2, CELL_WALL)
            # Chỉ thêm trap và road nếu energy_mode = True
            if energy_mode:
                # Thêm 1 trap
                if size > 3:
                    grid.set_cell_type(size // 3, size // 3, CELL_TRAP)
                # Thêm 1 road
                if size > 4:
                    grid.set_cell_type(size // 4, size // 4, CELL_ROAD)
        
        return grid


class PathfindingAlgorithms:
    """
    Lớp chứa các thuật toán tìm đường: BFS, DFS, Dijkstra, A*
    """
    
    def __init__(self, grid, allow_diagonal=False):
        """
        Khởi tạo với Grid
        
        Args:
            grid: Grid object
            allow_diagonal: True nếu cho phép đi chéo (8 hướng), False nếu chỉ 4 hướng
        """
        self.grid = grid
        self.allow_diagonal = allow_diagonal
    
    def manhattan_distance(self, row1, col1, row2, col2):
        """
        Tính khoảng cách Manhattan
        
        Công thức: |row1 - row2| + |col1 - col2|
        Phù hợp với di chuyển 4 hướng (không chéo)
        """
        return abs(row1 - row2) + abs(col1 - col2)
    
    def euclidean_distance(self, row1, col1, row2, col2):
        """
        Tính khoảng cách Euclidean
        
        Công thức: √((row1 - row2)² + (col1 - col2)²)
        Phù hợp với di chuyển 8 hướng (có chéo)
        """
        import math
        return math.sqrt((row1 - row2) ** 2 + (col1 - col2) ** 2)
    
    def bfs(self, callback=None):
        """
        Breadth-First Search: Tìm đường ngắn nhất về số bước, bỏ qua weights
        
        Args:
            callback: Hàm callback được gọi mỗi khi xét một node (để animation)
                      callback(node, state) với state = 'open' hoặc 'closed'
        
        Returns:
            Tuple (path, stats) với path là list các (row, col) và stats là dict
        """
        import collections
        import time
        
        start_time = time.time()
        self.grid.reset_pathfinding_data()
        
        if not self.grid.start or not self.grid.end:
            return None, {}
        
        start_node = self.grid.get_node(self.grid.start[0], self.grid.start[1])
        end_node = self.grid.get_node(self.grid.end[0], self.grid.end[1])
        
        queue = collections.deque([start_node])
        visited = set()
        visited.add((start_node.row, start_node.col))
        
        if callback:
            callback(start_node, 'open')
        
        while queue:
            current = queue.popleft()
            
            if callback:
                callback(current, 'closed')
            
            if current == end_node:
                # Truy vết đường đi
                path = []
                node = current
                while node:
                    path.append((node.row, node.col))
                    node = node.parent
                path.reverse()
                
                elapsed_time = (time.time() - start_time) * 1000
                total_steps = len(path) - 1
                total_energy = sum(self.grid.get_node(r, c).weight for r, c in path)
                
                stats = {
                    'algorithm': 'BFS',
                    'path_length': total_steps,
                    'total_energy': total_energy,
                    'time_taken': elapsed_time
                }
                return path, stats
            
            for neighbor, move_cost in self.grid.get_neighbors(current, allow_diagonal=self.allow_diagonal):
                pos = (neighbor.row, neighbor.col)
                if pos not in visited:
                    visited.add(pos)
                    neighbor.parent = current
                    queue.append(neighbor)
                    if callback:
                        callback(neighbor, 'open')
        
        elapsed_time = (time.time() - start_time) * 1000
        return None, {'algorithm': 'BFS', 'time_taken': elapsed_time, 'path_found': False}
    
    def dfs(self, callback=None):
        """
        Depth-First Search: Không đảm bảo đường ngắn nhất, bỏ qua weights
        
        Args:
            callback: Hàm callback được gọi mỗi khi xét một node
        
        Returns:
            Tuple (path, stats)
        """
        import time
        
        start_time = time.time()
        self.grid.reset_pathfinding_data()
        
        if not self.grid.start or not self.grid.end:
            return None, {}
        
        start_node = self.grid.get_node(self.grid.start[0], self.grid.start[1])
        end_node = self.grid.get_node(self.grid.end[0], self.grid.end[1])
        
        stack = [start_node]
        visited = set()
        visited.add((start_node.row, start_node.col))
        
        if callback:
            callback(start_node, 'open')
        
        while stack:
            current = stack.pop()
            
            if callback:
                callback(current, 'closed')
            
            if current == end_node:
                # Truy vết đường đi
                path = []
                node = current
                while node:
                    path.append((node.row, node.col))
                    node = node.parent
                path.reverse()
                
                elapsed_time = (time.time() - start_time) * 1000
                total_steps = len(path) - 1
                total_energy = sum(self.grid.get_node(r, c).weight for r, c in path)
                
                stats = {
                    'algorithm': 'DFS',
                    'path_length': total_steps,
                    'total_energy': total_energy,
                    'time_taken': elapsed_time
                }
                return path, stats
            
            for neighbor, move_cost in self.grid.get_neighbors(current, allow_diagonal=self.allow_diagonal):
                pos = (neighbor.row, neighbor.col)
                if pos not in visited:
                    visited.add(pos)
                    neighbor.parent = current
                    stack.append(neighbor)
                    if callback:
                        callback(neighbor, 'open')
        
        elapsed_time = (time.time() - start_time) * 1000
        return None, {'algorithm': 'DFS', 'time_taken': elapsed_time, 'path_found': False}
    
    def dijkstra(self, callback=None):
        """
        Dijkstra: Tìm đường với chi phí thấp nhất (tôn trọng weights)
        
        Args:
            callback: Hàm callback được gọi mỗi khi xét một node
        
        Returns:
            Tuple (path, stats)
        """
        import heapq
        import time
        
        start_time = time.time()
        self.grid.reset_pathfinding_data()
        
        if not self.grid.start or not self.grid.end:
            return None, {}
        
        start_node = self.grid.get_node(self.grid.start[0], self.grid.start[1])
        end_node = self.grid.get_node(self.grid.end[0], self.grid.end[1])
        
        start_node.g_score = 0
        open_set = [(0, start_node.row, start_node.col)]
        visited = set()
        
        if callback:
            callback(start_node, 'open')
        
        while open_set:
            current_g, row, col = heapq.heappop(open_set)
            current = self.grid.get_node(row, col)
            
            if (row, col) in visited:
                continue
            
            visited.add((row, col))
            
            if callback:
                callback(current, 'closed')
            
            if current == end_node:
                # Truy vết đường đi
                path = []
                node = current
                while node:
                    path.append((node.row, node.col))
                    node = node.parent
                path.reverse()
                
                elapsed_time = (time.time() - start_time) * 1000
                total_steps = len(path) - 1
                total_energy = sum(self.grid.get_node(r, c).weight for r, c in path)
                
                stats = {
                    'algorithm': 'Dijkstra',
                    'path_length': total_steps,
                    'total_energy': total_energy,
                    'time_taken': elapsed_time
                }
                return path, stats
            
            for neighbor, move_cost in self.grid.get_neighbors(current, allow_diagonal=self.allow_diagonal):
                pos = (neighbor.row, neighbor.col)
                if pos in visited:
                    continue
                
                # Tính chi phí từ current đến neighbor
                # Chi phí = move_cost (1.0 hoặc √2) * weight của neighbor
                tentative_g = current.g_score + move_cost * neighbor.weight
                
                if neighbor.g_score == 0 or tentative_g < neighbor.g_score:
                    neighbor.g_score = tentative_g
                    neighbor.parent = current
                    heapq.heappush(open_set, (tentative_g, neighbor.row, neighbor.col))
                    if callback:
                        callback(neighbor, 'open')
        
        elapsed_time = (time.time() - start_time) * 1000
        return None, {'algorithm': 'Dijkstra', 'time_taken': elapsed_time, 'path_found': False}
    
    def astar(self, callback=None):
        """
        A*: Sử dụng heuristic + cost, tối ưu cho Energy/Cost
        
        Args:
            callback: Hàm callback được gọi mỗi khi xét một node
        
        Returns:
            Tuple (path, stats)
        """
        import heapq
        import time
        
        start_time = time.time()
        self.grid.reset_pathfinding_data()
        
        if not self.grid.start or not self.grid.end:
            return None, {}
        
        start_node = self.grid.get_node(self.grid.start[0], self.grid.start[1])
        end_node = self.grid.get_node(self.grid.end[0], self.grid.end[1])
        
        start_node.g_score = 0
        # Chọn heuristic dựa trên allow_diagonal
        if self.allow_diagonal:
            start_node.h_score = self.euclidean_distance(
                start_node.row, start_node.col,
                end_node.row, end_node.col
            )
        else:
            start_node.h_score = self.manhattan_distance(
                start_node.row, start_node.col,
                end_node.row, end_node.col
            )
        start_node.f_score = start_node.g_score + start_node.h_score
        
        open_set = [(start_node.f_score, start_node.row, start_node.col)]
        visited = set()
        
        if callback:
            callback(start_node, 'open')
        
        while open_set:
            current_f, row, col = heapq.heappop(open_set)
            current = self.grid.get_node(row, col)
            
            if (row, col) in visited:
                continue
            
            visited.add((row, col))
            
            if callback:
                callback(current, 'closed')
            
            if current == end_node:
                # Truy vết đường đi
                path = []
                node = current
                while node:
                    path.append((node.row, node.col))
                    node = node.parent
                path.reverse()
                
                elapsed_time = (time.time() - start_time) * 1000
                total_steps = len(path) - 1
                total_energy = sum(self.grid.get_node(r, c).weight for r, c in path)
                
                stats = {
                    'algorithm': 'A*',
                    'path_length': total_steps,
                    'total_energy': total_energy,
                    'time_taken': elapsed_time
                }
                return path, stats
            
            for neighbor, move_cost in self.grid.get_neighbors(current, allow_diagonal=self.allow_diagonal):
                pos = (neighbor.row, neighbor.col)
                if pos in visited:
                    continue
                
                # Tính chi phí từ current đến neighbor
                # Chi phí = move_cost (1.0 hoặc √2) * weight của neighbor
                tentative_g = current.g_score + move_cost * neighbor.weight
                
                if neighbor.g_score == 0 or tentative_g < neighbor.g_score:
                    neighbor.g_score = tentative_g
                    # Chọn heuristic dựa trên allow_diagonal
                    if self.allow_diagonal:
                        neighbor.h_score = self.euclidean_distance(
                            neighbor.row, neighbor.col,
                            end_node.row, end_node.col
                        )
                    else:
                        neighbor.h_score = self.manhattan_distance(
                            neighbor.row, neighbor.col,
                            end_node.row, end_node.col
                        )
                    neighbor.f_score = neighbor.g_score + neighbor.h_score
                    neighbor.parent = current
                    heapq.heappush(open_set, (neighbor.f_score, neighbor.row, neighbor.col))
                    if callback:
                        callback(neighbor, 'open')
        
        elapsed_time = (time.time() - start_time) * 1000
        return None, {'algorithm': 'A*', 'time_taken': elapsed_time, 'path_found': False}


def print_map(room_map, path=None, start=None, goal=None):
    """
    Hiển thị bản đồ ra console với các ký tự:
        - '.' : Ô trống (đi được)
        - '█' : Vật cản (chướng ngại vật)
        - 'S' : Điểm bắt đầu (Start)
        - 'G' : Điểm đích (Goal)
        - '*' : Đường đi tìm được
    
    Args:
        room_map: Ma trận 2D đại diện cho bản đồ
        path: Danh sách các điểm trong đường đi (list of tuples)
        start: Tuple (row, col) điểm bắt đầu
        goal: Tuple (row, col) điểm đích
    """
    # Tạo bản sao bản đồ để đánh dấu đường đi
    display_map = [row[:] for row in room_map]
    
    # Đánh dấu đường đi (nếu có)
    if path:
        for row, col in path:
            # Không ghi đè Start và Goal
            if (row, col) != start and (row, col) != goal:
                display_map[row][col] = '*'
    
    # In bản đồ
    print("\n" + "="*50)
    print("BẢN ĐỒ PHÒNG (20x20)")
    print("="*50)
    
    for i in range(len(display_map)):
        for j in range(len(display_map[i])):
            if start and (i, j) == start:
                print('S', end=' ')  # Điểm bắt đầu
            elif goal and (i, j) == goal:
                print('G', end=' ')  # Điểm đích
            elif display_map[i][j] == 1:
                print('█', end=' ')  # Vật cản
            elif display_map[i][j] == '*':
                print('*', end=' ')  # Đường đi
            else:
                print('.', end=' ')  # Ô trống
        print()  # Xuống dòng
    
    print("="*50)
    print("Chú thích: S=Start, G=Goal, █=Vật cản, *=Đường đi, .=Ô trống")
    print("="*50 + "\n")


def main():
    """
    Hàm main: Chạy chương trình chính
    """
    # Bản đồ phòng 20x20 - PHIÊN BẢN PHỨC TẠP
    # 0: Ô trống (đi được), 1: Vật cản
    # Bản đồ này có nhiều vật cản tạo ra đường đi quanh co, phức tạp
    room_map = [
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
    ]
    
    # Điểm bắt đầu và đích
    start = (0, 0)
    goal = (18, 18)
    
    # In bản đồ ban đầu
    print("\n" + "="*50)
    print("BẢN ĐỒ BAN ĐẦU (TRƯỚC KHI TÌM ĐƯỜNG)")
    print("="*50)
    print_map(room_map, path=None, start=start, goal=goal)
    
    # ========== PHIÊN BẢN 1: 4 HƯỚNG (MANHATTAN) ==========
    print("\n" + "="*70)
    print("PHIÊN BẢN 1: DI CHUYỂN 4 HƯỚNG - HEURISTIC: MANHATTAN DISTANCE")
    print("="*70)
    
    robot_4dir = AStarRobot(room_map, start, goal, allow_diagonal=False)
    path_4dir = robot_4dir.find_path()
    
    if path_4dir:
        # Tính chi phí thực tế (mỗi bước = 1)
        total_steps_4dir = len(path_4dir) - 1
        total_cost_4dir = total_steps_4dir  # Mỗi bước = 1.0
        
        print(f"\n✓ Tìm thấy đường đi!")
        print(f"  - Tổng số bước: {total_steps_4dir}")
        print(f"  - Chi phí tổng: {total_cost_4dir:.2f}")
        print(f"  - Số nút: {len(path_4dir)}")
    else:
        print("\n✗ Không tìm thấy đường đi!")
        path_4dir = None
        total_steps_4dir = 0
        total_cost_4dir = 0
    
    # ========== PHIÊN BẢN 2: 8 HƯỚNG (EUCLIDEAN) ==========
    print("\n" + "="*70)
    print("PHIÊN BẢN 2: DI CHUYỂN 8 HƯỚNG (CÓ CHÉO) - HEURISTIC: EUCLIDEAN DISTANCE")
    print("="*70)
    
    # LƯU Ý: allow_diagonal được truyền rõ ràng ở đây
    robot_8dir = AStarRobot(room_map, start, goal, allow_diagonal=True)
    path_8dir = robot_8dir.find_path()
    
    if path_8dir:
        # Tính chi phí thực tế (có thể có bước chéo = √2)
        total_steps_8dir = len(path_8dir) - 1
        # Tính chi phí thực tế bằng cách cộng move_cost của từng bước
        total_cost_8dir = 0.0
        for i in range(len(path_8dir) - 1):
            r1, c1 = path_8dir[i]
            r2, c2 = path_8dir[i + 1]
            dr, dc = r2 - r1, c2 - c1
            # Xác định chi phí: chéo = √2, thẳng = 1.0
            if abs(dr) == 1 and abs(dc) == 1:
                import math
                total_cost_8dir += math.sqrt(2)
            else:
                total_cost_8dir += 1.0
        
        print(f"\n✓ Tìm thấy đường đi!")
        print(f"  - Tổng số bước: {total_steps_8dir}")
        print(f"  - Chi phí tổng: {total_cost_8dir:.2f}")
        print(f"  - Số nút: {len(path_8dir)}")
    else:
        print("\n✗ Không tìm thấy đường đi!")
        path_8dir = None
        total_steps_8dir = 0
        total_cost_8dir = 0
    
    # ========== SO SÁNH KẾT QUẢ ==========
    print("\n" + "="*70)
    print("SO SÁNH KẾT QUẢ: 4 HƯỚNG vs 8 HƯỚNG")
    print("="*70)
    
    if path_4dir and path_8dir:
        print(f"\n{'Tiêu chí':<30} {'4 Hướng':<20} {'8 Hướng':<20} {'Chênh lệch':<20}")
        print("-" * 90)
        print(f"{'Số bước đi':<30} {str(total_steps_4dir):<20} {str(total_steps_8dir):<20} {total_steps_4dir - total_steps_8dir:+.0f}")
        print(f"{'Chi phí tổng':<30} {f'{total_cost_4dir:.2f}':<20} {f'{total_cost_8dir:.2f}':<20} {total_cost_4dir - total_cost_8dir:+.2f}")
        
        improvement = ((total_cost_4dir - total_cost_8dir) / total_cost_4dir) * 100 if total_cost_4dir > 0 else 0
        print(f"\n{'Cải thiện':<30} {'':<20} {'':<20} {improvement:+.2f}%")
        
        if total_cost_8dir < total_cost_4dir:
            print(f"\n✓ KẾT LUẬN: Di chuyển 8 hướng NGẮN HƠN {improvement:.2f}% so với 4 hướng!")
            print(f"  → Đi chéo giúp robot tìm được đường đi tối ưu hơn.")
        elif total_cost_8dir == total_cost_4dir:
            print(f"\n→ KẾT LUẬN: Cả hai phương pháp cho kết quả tương đương.")
        else:
            print(f"\n→ KẾT LUẬN: Trong trường hợp này, 4 hướng cho kết quả tốt hơn.")
        
        # In bản đồ với đường đi 8 hướng (ưu tiên hiển thị)
        print("\n" + "="*70)
        print("BẢN ĐỒ VỚI ĐƯỜNG ĐI 8 HƯỚNG (TỐI ƯU HƠN)")
        print("="*70)
        print_map(room_map, path=path_8dir, start=start, goal=goal)
        
    elif path_4dir:
        print("\n→ Chỉ có phiên bản 4 hướng tìm thấy đường đi.")
        print_map(room_map, path=path_4dir, start=start, goal=goal)
    elif path_8dir:
        print("\n→ Chỉ có phiên bản 8 hướng tìm thấy đường đi.")
        print_map(room_map, path=path_8dir, start=start, goal=goal)
    else:
        print("\n✗ Cả hai phiên bản đều không tìm thấy đường đi!")
        print("Không có đường đi từ Start đến Goal trong bản đồ này.")


"""
================================================================================
GIẢI THÍCH: TẠI SAO CHỌN MANHATTAN DISTANCE THAY VÌ EUCLIDEAN?
================================================================================

1. PHÙ HỢP VỚI MÔ HÌNH DI CHUYỂN:
   - Robot chỉ được di chuyển 4 hướng: Lên, Xuống, Trái, Phải (không đi chéo)
   - Manhattan Distance = |Δx| + |Δy| chính là khoảng cách thực tế tối thiểu
     khi chỉ đi 4 hướng
   - Euclidean Distance = √(Δx² + Δy²) là khoảng cách đường thẳng, nhưng robot
     không thể đi chéo nên không phản ánh đúng chi phí thực tế

2. TÍNH ADMISSIBLE (CHẤP NHẬN ĐƯỢC):
   - Manhattan Distance luôn ≤ chi phí thực tế (vì không đi chéo)
   - Điều này đảm bảo thuật toán A* luôn tìm được đường đi tối ưu
   - Euclidean Distance cũng admissible, nhưng với di chuyển 4 hướng thì
     Manhattan chính xác hơn

3. HIỆU SUẤT TÍNH TOÁN:
   - Manhattan: |Δx| + |Δy| → chỉ cần phép cộng và trị tuyệt đối
   - Euclidean: √(Δx² + Δy²) → cần phép nhân, cộng và căn bậc 2
   - Manhattan nhanh hơn, đặc biệt quan trọng khi tính toán nhiều lần
     trong quá trình tìm kiếm

4. ĐỘ CHÍNH XÁC:
   - Với di chuyển 4 hướng, Manhattan Distance cho giá trị chính xác bằng
     chi phí thực tế tối thiểu
   - Euclidean Distance luôn đánh giá thấp hơn chi phí thực tế (vì đường
     chéo ngắn hơn), dẫn đến tìm kiếm kém hiệu quả hơn

KẾT LUẬN:
   Manhattan Distance là lựa chọn tối ưu cho bài toán này vì:
   - Phản ánh chính xác chi phí di chuyển thực tế (4 hướng)
   - Đảm bảo tính admissible → tìm được đường tối ưu
   - Tính toán nhanh hơn Euclidean
   - Phù hợp với mô hình di chuyển của robot

================================================================================
"""


if __name__ == "__main__":
    main()

