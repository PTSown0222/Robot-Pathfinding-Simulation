# -*- coding: utf-8 -*-
"""
Robot Pathfinding Simulation - Pygame UI
Mô tả: Giao diện Pygame để demo các thuật toán tìm đường với visualization
"""
import sys
import io
import pygame
import time

# Thiết lập encoding UTF-8 cho console (hỗ trợ tiếng Việt)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Import các class từ file robot_astar.py
import importlib.util
spec = importlib.util.spec_from_file_location("robot_astar", "robot_astar.py")
robot_astar_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(robot_astar_module)

# Import các class và constants
Grid = robot_astar_module.Grid
PathfindingAlgorithms = robot_astar_module.PathfindingAlgorithms
Node = robot_astar_module.Node
CELL_NORMAL = robot_astar_module.CELL_NORMAL
CELL_WALL = robot_astar_module.CELL_WALL
CELL_START = robot_astar_module.CELL_START
CELL_END = robot_astar_module.CELL_END
CELL_TRAP = robot_astar_module.CELL_TRAP
CELL_ROAD = robot_astar_module.CELL_ROAD

# Màu sắc - Cải thiện độ tương phản và dễ nhìn
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GRAY = (220, 220, 220)  # Sáng hơn cho grid lines
COLOR_GREEN = (50, 200, 50)  # Start - xanh lá đậm hơn
COLOR_RED = (255, 50, 50)  # End - đỏ đậm hơn
COLOR_YELLOW = (255, 220, 0)  # Path - vàng đậm hơn, dễ nhìn
COLOR_YELLOW_DARK = (200, 150, 0)  # Border cho path
COLOR_BLUE = (80, 130, 255)  # Open Set - xanh dương đậm hơn
COLOR_DARK_RED = (180, 30, 30)  # Closed Set - đỏ đậm hơn
COLOR_BROWN = (139, 69, 19)  # Trap/High Cost
COLOR_LIGHT_BLUE = (173, 216, 230)  # Road/Low Cost
COLOR_DARK_GRAY = (40, 40, 40)  # Background sidebar đậm hơn
COLOR_DARK_BLUE = (40, 80, 150)  # Button active
COLOR_GRID_BG = (245, 245, 245)  # Background grid sáng hơn


def darken_color(color, factor=0.6):
    """
    Làm đậm màu bằng cách giảm độ sáng
    
    Args:
        color: Tuple (R, G, B) màu gốc
        factor: Hệ số làm đậm (0.0-1.0), càng nhỏ càng đậm. Mặc định 0.6
    
    Returns:
        Tuple (R, G, B) màu đậm hơn
    """
    r, g, b = color
    return (int(r * factor), int(g * factor), int(b * factor))


class Button:
    """Lớp Button đơn giản"""
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.active = False
    
    def draw(self, screen):
        color = COLOR_DARK_BLUE if self.active else COLOR_GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLOR_BLACK, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, COLOR_WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Dropdown:
    """Lớp Dropdown đơn giản"""
    def __init__(self, x, y, width, height, options, font, default_index=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.font = font
        self.selected_index = default_index
        self.is_open = False
        self.height = height
    
    def get_selected(self):
        return self.options[self.selected_index]
    
    def draw(self, screen):
        # Vẽ dropdown chính
        color = COLOR_DARK_BLUE if self.is_open else COLOR_GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLOR_BLACK, self.rect, 2)
        
        # Vẽ mũi tên
        arrow_x = self.rect.right - 20
        arrow_y = self.rect.centery
        if self.is_open:
            # Mũi tên lên
            pygame.draw.polygon(screen, COLOR_WHITE, [
                (arrow_x, arrow_y - 5),
                (arrow_x - 5, arrow_y + 5),
                (arrow_x + 5, arrow_y + 5)
            ])
        else:
            # Mũi tên xuống
            pygame.draw.polygon(screen, COLOR_WHITE, [
                (arrow_x, arrow_y + 5),
                (arrow_x - 5, arrow_y - 5),
                (arrow_x + 5, arrow_y - 5)
            ])
        
        # Vẽ text đã chọn - đảm bảo không bị cắt
        selected_text_str = self.get_selected()
        # Tính toán width cần thiết (trừ đi 30px cho arrow và padding)
        max_text_width = self.rect.width - 30
        selected_text = self.font.render(selected_text_str, True, COLOR_WHITE)
        text_width = selected_text.get_width()
        
        # Nếu text quá dài, cắt bớt
        if text_width > max_text_width:
            # Thử cắt text và thêm "..."
            for i in range(len(selected_text_str), 0, -1):
                truncated = selected_text_str[:i] + "..."
                test_text = self.font.render(truncated, True, COLOR_WHITE)
                if test_text.get_width() <= max_text_width:
                    selected_text_str = truncated
                    selected_text = test_text
                    break
        
        text_rect = selected_text.get_rect(midleft=(self.rect.left + 5, self.rect.centery))
        screen.blit(selected_text, text_rect)
        
        # Vẽ dropdown menu nếu mở - VẼ SAU CÙNG để không bị che
        if self.is_open:
            dropdown_height = len(self.options) * self.height
            dropdown_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, dropdown_height)
            # Vẽ với màu sáng hơn và border rõ ràng
            pygame.draw.rect(screen, COLOR_WHITE, dropdown_rect)
            pygame.draw.rect(screen, COLOR_BLACK, dropdown_rect, 3)
            
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.height, 
                                         self.rect.width, self.height)
                if i == self.selected_index:
                    pygame.draw.rect(screen, COLOR_DARK_BLUE, option_rect)
                else:
                    # Hover effect
                    mouse_pos = pygame.mouse.get_pos()
                    if option_rect.collidepoint(mouse_pos):
                        pygame.draw.rect(screen, COLOR_LIGHT_GRAY, option_rect)
                
                option_text = self.font.render(option, True, COLOR_BLACK if i != self.selected_index else COLOR_WHITE)
                text_rect = option_text.get_rect(midleft=(option_rect.left + 5, option_rect.centery))
                screen.blit(option_text, text_rect)
    
    def is_clicked(self, pos):
        """Xử lý click vào dropdown, trả về True nếu selection thay đổi"""
        old_index = self.selected_index  # Lưu index cũ
        
        if self.rect.collidepoint(pos):
            self.is_open = not self.is_open
            return False  # Chỉ mở/đóng, chưa thay đổi selection
        
        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.height,
                                        self.rect.width, self.height)
                if option_rect.collidepoint(pos):
                    selection_changed = (old_index != i)
                    self.selected_index = i
                    self.is_open = False
                    # Trả về True nếu selection thay đổi
                    return selection_changed
        
        return False
    
    def handle_click_outside(self, pos):
        if self.is_open:
            dropdown_height = len(self.options) * self.height
            dropdown_rect = pygame.Rect(self.rect.x, self.rect.bottom, 
                                      self.rect.width, dropdown_height)
            if not (self.rect.collidepoint(pos) or dropdown_rect.collidepoint(pos)):
                self.is_open = False
                return True
        return False


class PathfindingSimulation:
    """
    Lớp chính cho Robot Pathfinding Simulation
    """
    
    def __init__(self):
        """Khởi tạo simulation"""
        pygame.init()
        
        # Kích thước cửa sổ - Có thể resize được
        self.WINDOW_WIDTH = 1200
        self.WINDOW_HEIGHT = 900
        self.MIN_WINDOW_WIDTH = 1000
        self.MIN_WINDOW_HEIGHT = 700
        self.GRID_SIZE = 20  # Default 20x20
        
        # Kích thước grid area (bên trái) - sẽ tính lại khi resize
        self.GRID_AREA_WIDTH = 800
        self.GRID_AREA_HEIGHT = 800
        self.SIDEBAR_WIDTH = 450  # Tăng width để chứa đầy đủ thông tin
        
        # Tạo cửa sổ với khả năng resize
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Robot Pathfinding Simulation")
        
        # Font - Hệ thống font chuẩn hóa cho menu chuyên nghiệp
        import sys
        try:
            # Thử dùng font hệ thống hỗ trợ Unicode (Arial, Tahoma, etc.)
            if sys.platform == 'win32':
                self.title_font = pygame.font.SysFont('arial', 20, bold=True)  # Tiêu đề section
                self.menu_font = pygame.font.SysFont('arial', 16)  # Text trong buttons/dropdowns
                self.label_font = pygame.font.SysFont('arial', 14)  # Labels nhỏ
                self.stats_font = pygame.font.SysFont('arial', 15)  # Statistics
            else:
                self.title_font = pygame.font.SysFont('dejavusans', 20, bold=True)
                self.menu_font = pygame.font.SysFont('dejavusans', 16)
                self.label_font = pygame.font.SysFont('dejavusans', 14)
                self.stats_font = pygame.font.SysFont('dejavusans', 15)
        except:
            # Fallback về font mặc định nếu không tìm thấy
            self.title_font = pygame.font.Font(None, 20)
            self.menu_font = pygame.font.Font(None, 16)
            self.label_font = pygame.font.Font(None, 14)
            self.stats_font = pygame.font.Font(None, 15)
        
        # Giữ font cũ để tương thích
        self.font = self.menu_font
        self.small_font = self.label_font
        
        # Tạo Grid
        self.grid = Grid(self.GRID_SIZE, self.GRID_SIZE)
        
        # Đặt Start và End mặc định
        self.grid.set_cell_type(0, 0, CELL_START)
        self.grid.set_cell_type(self.GRID_SIZE - 1, self.GRID_SIZE - 1, CELL_END)
        
        # Pathfinding
        self.allow_diagonal = False  # Mặc định 4 hướng
        self.pathfinder = PathfindingAlgorithms(self.grid, allow_diagonal=self.allow_diagonal)
        self.path = None
        self.stats = {}
        
        # Energy mode: True = có tính năng lượng (TRAP/ROAD), False = chỉ trắng đen (WALL/NORMAL)
        self.energy_mode = True  # Mặc định có energy
        
        # Drawing mode
        self.drawing_mode = 'WALL'  # WALL, TRAP, ROAD, START, END, NORMAL
        self.is_drawing = False
        self.last_draw_pos = None
        
        # Animation
        self.animation_nodes = {'open': set(), 'closed': set()}
        self.is_animating = False
        self.animation_queue = []  # Queue để lưu các animation steps
        self.animation_speed = 8  # Số frame giữa mỗi bước animation (chậm hơn để nhìn rõ)
        self.animation_frame_count = 0
        self.pathfinding_result = None  # Kết quả từ pathfinding
        self.pathfinding_running = False  # Flag để biết pathfinding đang chạy
        self.animation_paused = False  # Tạm dừng animation
        self.skip_animation = False  # Bỏ qua animation, hiển thị kết quả ngay
        
        # Robot animation
        self.robot_path = None  # Path để robot di chuyển
        self.robot_path_index = 0  # Vị trí hiện tại trong path
        self.robot_animating = False  # Flag để biết robot đang di chuyển
        self.robot_speed = 15  # Số frame giữa mỗi bước robot (chậm hơn để nhìn rõ)
        self.robot_frame_count = 0
        self.robot_visited_path = []  # Danh sách các ô robot đã đi qua (để đánh dấu)
        
        # Lưu algorithm hiện tại để detect thay đổi
        self.previous_algorithm = None
        
        # Load robot icon
        try:
            self.robot_icon = pygame.image.load('assets/images/robot.png')
            # Scale icon to fit cell size (will be resized dynamically in draw_grid)
            self.robot_icon_original = self.robot_icon
        except:
            self.robot_icon = None
            self.robot_icon_original = None
        
        # Tạo buttons
        self.create_buttons()
        
        # Clock
        self.clock = pygame.time.Clock()
    
    def create_buttons(self):
        """Tạo các buttons và dropdown với bố cục chuyên nghiệp, font size đều nhau"""
        x_start = self.GRID_AREA_WIDTH + 10
        y_start = 10
        button_width = 88  # Chuẩn hóa kích thước
        button_height = 30  # Tăng chiều cao để dễ nhìn
        spacing = 6  # Spacing đều nhau
        section_spacing = 16  # Khoảng cách giữa các section rõ ràng hơn
        
        # ========== SECTION 1: Algorithm Selection ==========
        algorithms = ['BFS', 'DFS', 'Dijkstra', 'A*']
        default_index = 3  # A* mặc định
        # Tính toán width dropdown để chứa text dài nhất
        # "Dijkstra" là text dài nhất, cần khoảng 100px + 30px cho arrow và padding
        dropdown_width = min(230, self.SIDEBAR_WIDTH - 20)
        self.algorithm_dropdown = Dropdown(x_start, y_start + 20, dropdown_width, button_height, 
                                          algorithms, self.menu_font, default_index=default_index)
        # Khởi tạo previous_algorithm với giá trị mặc định
        if not hasattr(self, 'previous_algorithm') or self.previous_algorithm is None:
            self.previous_algorithm = algorithms[default_index]
        y_start += button_height + spacing + 20  # 20px cho label + spacing
        
        # ========== SECTION 1.5: Movement Direction ==========
        movement_options = ['4 Directions', '8 Directions']
        default_movement_index = 0  # 4 hướng mặc định
        # "8 Directions" là text dài nhất, cần khoảng 120px + 30px
        self.movement_dropdown = Dropdown(x_start, y_start + 20, dropdown_width, button_height,
                                         movement_options, self.menu_font, default_index=default_movement_index)
        y_start += button_height + spacing + 20
        
        # ========== SECTION 1.6: Energy Mode ==========
        energy_options = ['Energy Mode', 'Simple Mode']
        default_energy_index = 0  # Energy mode mặc định
        # "Energy Mode" là text dài nhất, cần khoảng 120px + 30px
        self.energy_dropdown = Dropdown(x_start, y_start + 20, dropdown_width, button_height,
                                        energy_options, self.menu_font, default_index=default_energy_index)
        y_start += button_height + spacing + section_spacing
        
        # ========== SECTION 2: Pathfinding Actions (2 cột) ==========
        self.find_path_button = Button(x_start, y_start, button_width, button_height, 'Find Path', self.menu_font)
        self.clear_path_button = Button(x_start + button_width + spacing, y_start, 
                                       button_width, button_height, 'Clear Path', self.menu_font)
        y_start += button_height + spacing
        
        # Animation Controls (2 cột)
        self.skip_animation_button = Button(x_start, y_start, button_width, button_height, 'Skip', self.menu_font)
        self.fast_forward_button = Button(x_start + button_width + spacing, y_start, 
                                         button_width, button_height, 'Fast', self.menu_font)
        y_start += button_height + spacing + section_spacing
        
        # ========== SECTION 3: Map Management (2 cột) ==========
        self.reset_button = Button(x_start, y_start, button_width, button_height, 'Reset', self.menu_font)
        
        # Random Map Size Dropdown (bên cạnh Reset)
        map_sizes = ['10x10', '20x20', '30x30']
        self.random_map_size_dropdown = Dropdown(x_start + button_width + spacing, y_start, 
                                                 button_width, button_height, 
                                                 map_sizes, self.menu_font, default_index=1)
        y_start += button_height + spacing
        # Random Map và Create Map buttons (2 cột)
        self.random_map_button = Button(x_start, y_start, button_width, button_height, 'Random Map', self.menu_font)
        self.create_map_button = Button(x_start + button_width + spacing, y_start, 
                                       button_width, button_height, 'Create Map', self.menu_font)
        y_start += button_height + spacing + section_spacing
        
        # ========== SECTION 4: Drawing Modes (3 cột để tối ưu) ==========
        self.drawing_buttons = {}
        # Tạo buttons cho tất cả modes (sẽ ẩn/hiện dựa trên energy_mode)
        modes = [
            ('WALL', 'Wall (W)'),
            ('TRAP', 'Trap (T)'),
            ('ROAD', 'Road (R)'),
            ('START', 'Start (S)'),
            ('END', 'End (E)'),
            ('NORMAL', 'Normal (N)')
        ]
        # Vẽ 3 cột để tận dụng không gian ngang
        cols = 3
        for i, (mode, label) in enumerate(modes):
            col = i % cols
            row = i // cols
            x = x_start + col * (button_width + spacing)
            y = y_start + row * (button_height + spacing)
            btn = Button(x, y, button_width, button_height, label, self.menu_font)
            self.drawing_buttons[mode] = btn
            if mode == 'WALL':
                btn.active = True
    
    def update_energy_mode(self):
        """
        Cập nhật energy_mode và tự động thêm/xóa TRAP/ROAD
        
        - Khi chuyển từ Simple Mode → Energy Mode: Tự động thêm TRAP/ROAD vào các ô NORMAL nếu chưa có
        - Khi chuyển từ Energy Mode → Simple Mode: Chuyển tất cả TRAP/ROAD thành NORMAL
        """
        import random
        
        energy_selected = self.energy_dropdown.get_selected()
        new_energy_mode = (energy_selected == 'Energy Mode')
        
        # Nếu chuyển từ Energy Mode sang Simple Mode, chuyển tất cả TRAP/ROAD thành NORMAL
        if self.energy_mode and not new_energy_mode:
            for row in range(self.GRID_SIZE):
                for col in range(self.GRID_SIZE):
                    node = self.grid.get_node(row, col)
                    if node and (node.cell_type == CELL_TRAP or node.cell_type == CELL_ROAD):
                        self.grid.set_cell_type(row, col, CELL_NORMAL)
            
            # Nếu đang ở chế độ TRAP hoặc ROAD, chuyển về WALL
            if self.drawing_mode == 'TRAP' or self.drawing_mode == 'ROAD':
                self.drawing_mode = 'WALL'
        
        # Nếu chuyển từ Simple Mode sang Energy Mode, tự động thêm TRAP/ROAD nếu chưa có
        elif not self.energy_mode and new_energy_mode:
            # Kiểm tra xem đã có TRAP/ROAD chưa
            has_trap = False
            has_road = False
            
            for row in range(self.GRID_SIZE):
                for col in range(self.GRID_SIZE):
                    node = self.grid.get_node(row, col)
                    if node:
                        if node.cell_type == CELL_TRAP:
                            has_trap = True
                        elif node.cell_type == CELL_ROAD:
                            has_road = True
                        if has_trap and has_road:
                            break
                if has_trap and has_road:
                    break
            
            # Nếu chưa có TRAP hoặc ROAD, tự động thêm vào
            if not has_trap or not has_road:
                # Thu thập danh sách các ô NORMAL có thể thêm TRAP/ROAD
                # (không phải START, END, WALL)
                available_cells = []
                for row in range(self.GRID_SIZE):
                    for col in range(self.GRID_SIZE):
                        node = self.grid.get_node(row, col)
                        if node and node.cell_type == CELL_NORMAL:
                            available_cells.append((row, col))
                
                # Shuffle để random
                random.shuffle(available_cells)
                
                # Tính số lượng TRAP và ROAD cần thêm (khoảng 5-8% số ô NORMAL)
                total_normal = len(available_cells)
                if total_normal > 0:
                    num_to_add = max(2, min(10, int(total_normal * 0.06)))  # 6% hoặc ít nhất 2, tối đa 10
                    
                    # Phân bố đều giữa TRAP và ROAD
                    num_traps = num_to_add // 2
                    num_roads = num_to_add - num_traps
                    
                    # Thêm TRAP nếu chưa có
                    if not has_trap and num_traps > 0:
                        for i in range(min(num_traps, len(available_cells))):
                            row, col = available_cells[i]
                            self.grid.set_cell_type(row, col, CELL_TRAP)
                    
                    # Thêm ROAD nếu chưa có
                    # Cập nhật lại danh sách available_cells để loại bỏ các ô đã có TRAP
                    if not has_road and num_roads > 0:
                        # Thu thập lại danh sách các ô NORMAL (có thể đã thay đổi sau khi thêm TRAP)
                        available_cells_for_road = []
                        for row in range(self.GRID_SIZE):
                            for col in range(self.GRID_SIZE):
                                node = self.grid.get_node(row, col)
                                if node and node.cell_type == CELL_NORMAL:
                                    available_cells_for_road.append((row, col))
                        
                        # Shuffle lại để random
                        random.shuffle(available_cells_for_road)
                        
                        # Thêm ROAD vào các ô NORMAL
                        for i in range(min(num_roads, len(available_cells_for_road))):
                            row, col = available_cells_for_road[i]
                            self.grid.set_cell_type(row, col, CELL_ROAD)
        
        self.energy_mode = new_energy_mode
    
    def get_cell_from_pos(self, pos):
        """Chuyển đổi vị trí pixel thành (row, col)"""
        x, y = pos
        if x < 0 or x >= self.GRID_AREA_WIDTH or y < 0 or y >= self.GRID_AREA_HEIGHT:
            return None
        
        cell_width = self.GRID_AREA_WIDTH / self.GRID_SIZE
        cell_height = self.GRID_AREA_HEIGHT / self.GRID_SIZE
        
        col = int(x / cell_width)
        row = int(y / cell_height)
        
        if 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE:
            return (row, col)
        return None
    
    def handle_mouse_click(self, pos, button):
        """Xử lý click chuột"""
        cell = self.get_cell_from_pos(pos)
        if cell is None:
            return
        
        row, col = cell
        
        if button == 1:  # Left click
            if self.drawing_mode == 'START':
                self.grid.set_cell_type(row, col, CELL_START)
            elif self.drawing_mode == 'END':
                self.grid.set_cell_type(row, col, CELL_END)
            elif self.drawing_mode == 'WALL':
                self.grid.set_cell_type(row, col, CELL_WALL)
            elif self.drawing_mode == 'TRAP':
                # Chỉ cho phép nếu energy_mode = True
                if self.energy_mode:
                    self.grid.set_cell_type(row, col, CELL_TRAP)
                else:
                    self.grid.set_cell_type(row, col, CELL_NORMAL)
            elif self.drawing_mode == 'ROAD':
                # Chỉ cho phép nếu energy_mode = True
                if self.energy_mode:
                    self.grid.set_cell_type(row, col, CELL_ROAD)
                else:
                    self.grid.set_cell_type(row, col, CELL_NORMAL)
            elif self.drawing_mode == 'NORMAL':
                self.grid.set_cell_type(row, col, CELL_NORMAL)
            self.last_draw_pos = (row, col)
            self.is_drawing = True
        
        elif button == 3:  # Right click - Draw Traps (chỉ khi energy_mode)
            if self.energy_mode:
                self.grid.set_cell_type(row, col, CELL_TRAP)
            else:
                self.grid.set_cell_type(row, col, CELL_NORMAL)
            self.last_draw_pos = (row, col)
            self.is_drawing = True
        
        elif button == 2:  # Middle click - Draw Roads (chỉ khi energy_mode)
            if self.energy_mode:
                self.grid.set_cell_type(row, col, CELL_ROAD)
            else:
                self.grid.set_cell_type(row, col, CELL_NORMAL)
            self.last_draw_pos = (row, col)
            self.is_drawing = True
    
    def handle_mouse_drag(self, pos, button):
        """Xử lý kéo chuột"""
        if not self.is_drawing:
            return
        
        cell = self.get_cell_from_pos(pos)
        if cell is None:
            return
        
        row, col = cell
        if self.last_draw_pos == (row, col):
            return
        
        if button == 1:  # Left drag
            if self.drawing_mode == 'WALL':
                self.grid.set_cell_type(row, col, CELL_WALL)
            elif self.drawing_mode == 'TRAP':
                if self.energy_mode:
                    self.grid.set_cell_type(row, col, CELL_TRAP)
                else:
                    self.grid.set_cell_type(row, col, CELL_NORMAL)
            elif self.drawing_mode == 'ROAD':
                if self.energy_mode:
                    self.grid.set_cell_type(row, col, CELL_ROAD)
                else:
                    self.grid.set_cell_type(row, col, CELL_NORMAL)
        
        elif button == 3:  # Right drag - Traps (chỉ khi energy_mode)
            if self.energy_mode:
                self.grid.set_cell_type(row, col, CELL_TRAP)
            else:
                self.grid.set_cell_type(row, col, CELL_NORMAL)
        
        elif button == 2:  # Middle drag - Roads (chỉ khi energy_mode)
            if self.energy_mode:
                self.grid.set_cell_type(row, col, CELL_ROAD)
            else:
                self.grid.set_cell_type(row, col, CELL_NORMAL)
        
        self.last_draw_pos = (row, col)
    
    def find_path(self):
        """Tìm đường đi với thuật toán đã chọn - với animation step-by-step"""
        if not self.grid.start or not self.grid.end:
            return
        
        if self.pathfinding_running:
            return  # Đang chạy rồi, không chạy lại
        
        # Cập nhật allow_diagonal từ dropdown
        movement_selected = self.movement_dropdown.get_selected()
        self.allow_diagonal = (movement_selected == '8 Directions')
        
        # Cập nhật pathfinder với allow_diagonal mới
        self.pathfinder = PathfindingAlgorithms(self.grid, allow_diagonal=self.allow_diagonal)
        
        # Reset animation
        self.animation_nodes = {'open': set(), 'closed': set()}
        self.path = None
        self.stats = {}
        self.is_animating = True
        self.animation_frame_count = 0
        self.animation_queue = []
        self.pathfinding_result = None
        self.pathfinding_running = True
        self.animation_paused = False
        self.skip_animation = False
        # Reset animation speed về mặc định
        self.animation_speed = 8
        self.robot_speed = 15
        
        # Reset robot animation
        self.robot_path = None
        self.robot_path_index = 0
        self.robot_animating = False
        self.robot_frame_count = 0
        
        # Lấy algorithm từ dropdown
        current_algorithm = self.algorithm_dropdown.get_selected()
        
        # Callback để thêm animation steps vào queue
        def animation_callback(node, state):
            """Callback để thêm animation steps vào queue"""
            self.animation_queue.append((node, state))
        
        # Chạy thuật toán trong thread riêng để không block UI
        import threading
        
        def run_algorithm():
            """Chạy thuật toán trong thread riêng"""
            try:
                if current_algorithm == 'BFS':
                    path, stats = self.pathfinder.bfs(animation_callback)
                elif current_algorithm == 'DFS':
                    path, stats = self.pathfinder.dfs(animation_callback)
                elif current_algorithm == 'Dijkstra':
                    path, stats = self.pathfinder.dijkstra(animation_callback)
                elif current_algorithm == 'A*':
                    path, stats = self.pathfinder.astar(animation_callback)
                else:
                    path, stats = None, {}
                
                # Lưu kết quả
                self.pathfinding_result = (path, stats)
            finally:
                self.pathfinding_running = False
        
        # Bắt đầu thread
        thread = threading.Thread(target=run_algorithm, daemon=True)
        thread.start()
    
    def clear_path(self):
        """Xóa đường đi và animation nhưng giữ lại walls và map"""
        self.path = None
        self.animation_nodes = {'open': set(), 'closed': set()}
        self.stats = {}
        self.grid.reset_pathfinding_data()
        # Reset robot animation
        self.robot_path = None
        self.robot_path_index = 0
        self.robot_animating = False
        self.robot_frame_count = 0
        self.robot_visited_path = []
        self.is_animating = False
        self.animation_queue = []
        self.pathfinding_result = None
        self.pathfinding_running = False
        self.animation_paused = False
        self.skip_animation = False
        # Reset animation speed về mặc định
        self.animation_speed = 8
        self.robot_speed = 15
        # Note: Walls, traps, roads, start, end vẫn được giữ nguyên
        # Đảm bảo Start và End vẫn hiển thị màu đặc biệt
    
    def reset_grid(self):
        """Reset grid về trạng thái ban đầu"""
        self.grid = Grid(self.GRID_SIZE, self.GRID_SIZE)
        self.grid.set_cell_type(0, 0, CELL_START)
        self.grid.set_cell_type(self.GRID_SIZE - 1, self.GRID_SIZE - 1, CELL_END)
        # Cập nhật allow_diagonal từ dropdown
        movement_selected = self.movement_dropdown.get_selected()
        self.allow_diagonal = (movement_selected == '8 Directions')
        self.pathfinder = PathfindingAlgorithms(self.grid, allow_diagonal=self.allow_diagonal)
        self.clear_path()
    
    def generate_random_map(self):
        """Tạo random map với đầy đủ cell types và đảm bảo có đường đi"""
        # Lấy kích thước từ dropdown
        size_str = self.random_map_size_dropdown.get_selected()
        size = int(size_str.split('x')[0])  # Lấy số đầu tiên từ "10x10", "20x20", etc.
        
        # Lấy energy_mode từ dropdown
        energy_selected = self.energy_dropdown.get_selected()
        energy_mode = (energy_selected == 'Energy Mode')
        
        # Tạo random map với kích thước và energy_mode đã chọn
        new_grid = Grid.generate_random_map(min_size=size, max_size=size, energy_mode=energy_mode)
        
        # Cập nhật energy_mode
        self.energy_mode = energy_mode
        
        # Cập nhật grid size
        self.GRID_SIZE = new_grid.rows
        
        # Cập nhật grid
        self.grid = new_grid
        # Cập nhật allow_diagonal từ dropdown
        movement_selected = self.movement_dropdown.get_selected()
        self.allow_diagonal = (movement_selected == '8 Directions')
        self.pathfinder = PathfindingAlgorithms(self.grid, allow_diagonal=self.allow_diagonal)
        self.clear_path()
    
    def load_map_from_file(self):
        """Load map từ file trong assets/map dựa vào size dropdown"""
        # Lấy kích thước từ dropdown
        size_str = self.random_map_size_dropdown.get_selected()
        
        # Kiểm tra xem có numpy không trước khi thử import module
        has_numpy = False
        try:
            import numpy as np
            has_numpy = True
        except ImportError:
            has_numpy = False
        
        # Nếu có numpy, thử import module
        if has_numpy:
            try:
                import importlib
                import sys
                
                # Map size to module name
                module_name = f"assets.map.{size_str}"
                
                # Reload module nếu đã import trước đó để đảm bảo có dữ liệu mới nhất
                if module_name in sys.modules:
                    module = importlib.reload(sys.modules[module_name])
                else:
                    module = importlib.import_module(module_name)
                
                # Lấy classroom_map từ module
                if not hasattr(module, 'classroom_map'):
                    raise AttributeError(f"Module {module_name} không có attribute 'classroom_map'")
                
                classroom_map = module.classroom_map
                
                # Kiểm tra xem có phải numpy array không
                try:
                    # Nếu là numpy array, lấy shape
                    rows, cols = classroom_map.shape
                    # Convert numpy array sang list để xử lý
                    map_data = classroom_map.tolist()
                except AttributeError:
                    # Nếu không phải numpy array, giả sử là list of lists
                    rows = len(classroom_map)
                    cols = len(classroom_map[0]) if rows > 0 else 0
                    map_data = classroom_map
                
                # Tạo Grid mới với kích thước từ map
                new_grid = Grid(rows, cols)
                
                # Convert map data sang Grid
                # Mapping: 0 -> CELL_NORMAL, 1 -> CELL_WALL, 2 -> CELL_START, 3 -> CELL_END
                start_pos = None
                end_pos = None
                
                for row in range(rows):
                    for col in range(cols):
                        cell_value = int(map_data[row][col])
                        
                        if cell_value == 0:  # Trống
                            new_grid.set_cell_type(row, col, CELL_NORMAL)
                        elif cell_value == 1:  # Vật cản
                            new_grid.set_cell_type(row, col, CELL_WALL)
                        elif cell_value == 2:  # Start
                            new_grid.set_cell_type(row, col, CELL_START)
                            start_pos = (row, col)
                        elif cell_value == 3:  # Goal/End
                            new_grid.set_cell_type(row, col, CELL_END)
                            end_pos = (row, col)
                
                # Kiểm tra xem có Start và End không
                if start_pos is None or end_pos is None:
                    # Không in warning để tránh lỗi I/O
                    pass
                
                # Cập nhật grid size
                self.GRID_SIZE = rows
                
                # Cập nhật grid
                self.grid = new_grid
                
                # Cập nhật allow_diagonal từ dropdown
                movement_selected = self.movement_dropdown.get_selected()
                self.allow_diagonal = (movement_selected == '8 Directions')
                self.pathfinder = PathfindingAlgorithms(self.grid, allow_diagonal=self.allow_diagonal)
                
                # Clear path
                self.clear_path()
                return  # Thành công, return ngay
                
            except Exception as e:
                # Nếu import module fail, chuyển sang fallback
                pass
        
        # Fallback: Load trực tiếp từ file (không cần numpy)
        try:
            self._load_map_from_file_direct(size_str)
        except Exception as e:
            # Không in error để tránh lỗi I/O, chỉ pass
            pass
    
    def _load_map_from_file_direct(self, size_str):
        """Load map trực tiếp từ file Python (fallback method)"""
        import os
        import re
        
        # Đường dẫn đến file map
        map_file = os.path.join('assets', 'map', f'{size_str}.py')
        
        if not os.path.exists(map_file):
            raise FileNotFoundError(f"Map file not found: {map_file}")
        
        # Đọc file và parse
        with open(map_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tìm phần np.array([...]) và extract list
        # Pattern: np.array([...]) hoặc chỉ [...]
        pattern = r'classroom_map\s*=\s*np\.array\s*\(\s*\[(.*?)\]\s*\)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            # Thử tìm pattern khác: classroom_map = [...]
            pattern2 = r'classroom_map\s*=\s*\[(.*?)\]'
            match = re.search(pattern2, content, re.DOTALL)
        
        if match:
            # Parse list of lists từ string
            array_str = match.group(1)
            # Chuyển đổi string thành list of lists
            # Loại bỏ whitespace và parse
            lines = [line.strip() for line in array_str.split('],') if line.strip()]
            map_data = []
            for line in lines:
                # Loại bỏ [ và ]
                line = line.strip('[],')
                # Split by comma và convert to int
                row = [int(x.strip()) for x in line.split(',') if x.strip()]
                if row:
                    map_data.append(row)
        else:
            # Fallback: exec file trong namespace riêng với mock numpy
            # Tạo mock numpy để không cần cài đặt
            class MockNumpy:
                def array(self, data):
                    return data
            
            namespace = {'np': MockNumpy(), '__builtins__': __builtins__}
            try:
                exec(compile(content, map_file, 'exec'), namespace)
                if 'classroom_map' not in namespace:
                    raise ValueError(f"File {map_file} không có biến 'classroom_map'")
                map_data = namespace['classroom_map']
                # Nếu là list, giữ nguyên; nếu là numpy array (mock), cũng là list
            except Exception as e:
                raise ValueError(f"Không thể parse file {map_file}: {e}")
        
        # Kiểm tra dữ liệu
        if not map_data or len(map_data) == 0:
            raise ValueError(f"Map data rỗng trong file {map_file}")
        
        rows = len(map_data)
        cols = len(map_data[0]) if rows > 0 else 0
        
        # Tạo Grid
        new_grid = Grid(rows, cols)
        
        for row in range(rows):
            for col in range(cols):
                cell_value = int(map_data[row][col])
                
                if cell_value == 0:
                    new_grid.set_cell_type(row, col, CELL_NORMAL)
                elif cell_value == 1:
                    new_grid.set_cell_type(row, col, CELL_WALL)
                elif cell_value == 2:
                    new_grid.set_cell_type(row, col, CELL_START)
                elif cell_value == 3:
                    new_grid.set_cell_type(row, col, CELL_END)
        
        self.GRID_SIZE = rows
        self.grid = new_grid
        
        movement_selected = self.movement_dropdown.get_selected()
        self.allow_diagonal = (movement_selected == '8 Directions')
        self.pathfinder = PathfindingAlgorithms(self.grid, allow_diagonal=self.allow_diagonal)
        self.clear_path()
    
    def draw_grid(self):
        """Vẽ grid lên màn hình với màu sắc cải thiện"""
        # Vẽ background cho grid area
        pygame.draw.rect(self.screen, COLOR_GRID_BG, 
                        (0, 0, self.GRID_AREA_WIDTH, self.GRID_AREA_HEIGHT))
        
        cell_width = self.GRID_AREA_WIDTH / self.GRID_SIZE
        cell_height = self.GRID_AREA_HEIGHT / self.GRID_SIZE
        
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                node = self.grid.get_node(row, col)
                if not node:
                    continue
                
                x = col * cell_width
                y = row * cell_height
                rect = pygame.Rect(x, y, cell_width, cell_height)
                
                # Priority: Start/End > Cell types (giữ nguyên màu) > Robot visited > Animation markers > Path line
                is_start = node.cell_type == CELL_START
                is_end = node.cell_type == CELL_END
                is_path = self.path and (row, col) in self.path
                is_open = (row, col) in self.animation_nodes['open']
                is_closed = (row, col) in self.animation_nodes['closed']
                is_robot_visited = (row, col) in self.robot_visited_path
                is_robot_current = (self.robot_animating and self.robot_path and 
                                   self.robot_path_index < len(self.robot_path) and
                                   (row, col) == self.robot_path[self.robot_path_index])
                
                # Xác định màu nền dựa trên cell type
                # Viền sẽ là màu đậm hơn của chính màu đó để dễ nhận biết
                if is_start:
                    color = COLOR_GREEN
                    border_color = darken_color(COLOR_GREEN, 0.5)  # Xanh lá đậm hơn
                    border_width = 3
                elif is_end:
                    color = COLOR_RED
                    border_color = darken_color(COLOR_RED, 0.5)  # Đỏ đậm hơn
                    border_width = 3
                elif node.cell_type == CELL_WALL:
                    color = COLOR_BLACK
                    border_color = COLOR_DARK_GRAY  # Giữ nguyên vì đã là màu đen
                    border_width = 2
                elif node.cell_type == CELL_TRAP:
                    # Nếu không có energy_mode, hiển thị như NORMAL
                    if not self.energy_mode:
                        color = COLOR_WHITE
                        border_color = (180, 180, 180)
                        border_width = 1
                    else:
                        color = COLOR_BROWN
                        border_color = darken_color(COLOR_BROWN, 0.4)  # Nâu đậm hơn
                        border_width = 2
                elif node.cell_type == CELL_ROAD:
                    # Nếu không có energy_mode, hiển thị như NORMAL
                    if not self.energy_mode:
                        color = COLOR_WHITE
                        border_color = (180, 180, 180)
                        border_width = 1
                    else:
                        color = COLOR_LIGHT_BLUE
                        border_color = darken_color(COLOR_LIGHT_BLUE, 0.6)  # Xanh nhạt đậm hơn
                        border_width = 2
                else:  # NORMAL
                    color = COLOR_WHITE
                    # Với màu trắng, viền xám đậm tạo contrast tốt hơn
                    border_color = (180, 180, 180)  # Xám đậm vừa phải
                    border_width = 1
                
                # Vẽ cell với màu nền gốc (GIỮ NGUYÊN thông tin vật cản)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, border_color, rect, border_width)
                
                # Vẽ robot icon tại ô bắt đầu (nếu không đang di chuyển)
                if is_start and not self.robot_animating and self.robot_icon:
                    # Scale icon để vừa với cell
                    icon_size = int(min(cell_width, cell_height) * 0.7)
                    scaled_icon = pygame.transform.scale(self.robot_icon_original, (icon_size, icon_size))
                    icon_rect = scaled_icon.get_rect(center=(x + cell_width/2, y + cell_height/2))
                    self.screen.blit(scaled_icon, icon_rect)
                
                # Vẽ marker cho Open/Closed Set và Robot visited trên nền gốc
                if is_robot_visited and not is_start and not is_end and not is_robot_current:
                    # Vẽ robot nhỏ đánh dấu ô đã đi qua (thay thế X)
                    robot_marker_radius = min(cell_width, cell_height) * 0.2
                    center_x = x + cell_width / 2
                    center_y = y + cell_height / 2
                    pygame.draw.circle(self.screen, COLOR_YELLOW, (int(center_x), int(center_y)), int(robot_marker_radius))
                    pygame.draw.circle(self.screen, COLOR_BLACK, (int(center_x), int(center_y)), int(robot_marker_radius), 1)
                elif is_open and not is_start and not is_end and not is_robot_visited and not is_robot_current:
                    # Vẽ chữ O (Open Set) màu xanh dương trên nền gốc
                    font_size = max(12, int(min(cell_width, cell_height) * 0.6))
                    try:
                        import sys
                        marker_font = pygame.font.SysFont('arial', font_size) if sys.platform == 'win32' else pygame.font.Font(None, font_size)
                    except:
                        marker_font = pygame.font.Font(None, font_size)
                    marker_text = marker_font.render('O', True, COLOR_BLUE)
                    marker_rect = marker_text.get_rect(center=(x + cell_width/2, y + cell_height/2))
                    self.screen.blit(marker_text, marker_rect)
                elif is_closed and not is_start and not is_end and not is_robot_visited and not is_robot_current:
                    # Vẽ chữ X (Closed Set) màu đỏ đậm trên nền gốc (chỉ khi robot chưa đi qua)
                    font_size = max(12, int(min(cell_width, cell_height) * 0.6))
                    try:
                        import sys
                        marker_font = pygame.font.SysFont('arial', font_size) if sys.platform == 'win32' else pygame.font.Font(None, font_size)
                    except:
                        marker_font = pygame.font.Font(None, font_size)
                    marker_text = marker_font.render('X', True, COLOR_DARK_RED)
                    marker_rect = marker_text.get_rect(center=(x + cell_width/2, y + cell_height/2))
                    self.screen.blit(marker_text, marker_rect)
        
        # Vẽ border cho grid area
        pygame.draw.rect(self.screen, COLOR_BLACK, 
                        (0, 0, self.GRID_AREA_WIDTH, self.GRID_AREA_HEIGHT), 3)
        
        # Vẽ robot nếu đang di chuyển
        if self.robot_animating and self.robot_path and self.robot_path_index < len(self.robot_path):
            cell_width = self.GRID_AREA_WIDTH / self.GRID_SIZE
            cell_height = self.GRID_AREA_HEIGHT / self.GRID_SIZE
            
            # Lấy vị trí hiện tại của robot
            r, c = self.robot_path[self.robot_path_index]
            x = c * cell_width + cell_width / 2
            y = r * cell_height + cell_height / 2
            
            # Vẽ robot đơn giản (hình tròn với mũi tên)
            robot_radius = min(cell_width, cell_height) * 0.3
            pygame.draw.circle(self.screen, COLOR_YELLOW, (int(x), int(y)), int(robot_radius))
            pygame.draw.circle(self.screen, COLOR_BLACK, (int(x), int(y)), int(robot_radius), 2)
            
            # Vẽ mũi tên chỉ hướng đi (nếu có bước tiếp theo)
            if self.robot_path_index < len(self.robot_path) - 1:
                next_r, next_c = self.robot_path[self.robot_path_index + 1]
                next_x = next_c * cell_width + cell_width / 2
                next_y = next_r * cell_height + cell_height / 2
                
                # Tính góc
                import math
                angle = math.atan2(next_y - y, next_x - x)
                arrow_length = robot_radius * 0.6
                arrow_x = x + math.cos(angle) * arrow_length
                arrow_y = y + math.sin(angle) * arrow_length
                
                # Vẽ mũi tên
                pygame.draw.line(self.screen, COLOR_BLACK, (int(x), int(y)), 
                                (int(arrow_x), int(arrow_y)), 2)
                # Vẽ đầu mũi tên
                arrow_size = 5
                pygame.draw.polygon(self.screen, COLOR_BLACK, [
                    (int(arrow_x), int(arrow_y)),
                    (int(arrow_x - arrow_size * math.cos(angle - 0.5)), 
                     int(arrow_y - arrow_size * math.sin(angle - 0.5))),
                    (int(arrow_x - arrow_size * math.cos(angle + 0.5)), 
                     int(arrow_y - arrow_size * math.sin(angle + 0.5)))
                ])
        
        # Vẽ đường path (đường thẳng đỏ) nếu có (chỉ hiển thị sau khi robot đi hết)
        # Path sẽ hiển thị sau khi robot hoàn thành, nhưng robot markers vẫn hiển thị
        if self.path and len(self.path) > 1 and not self.robot_animating:
            cell_width = self.GRID_AREA_WIDTH / self.GRID_SIZE
            cell_height = self.GRID_AREA_HEIGHT / self.GRID_SIZE
            path_color = COLOR_RED  # Đường thẳng đỏ
            
            for i in range(len(self.path) - 1):
                r1, c1 = self.path[i]
                r2, c2 = self.path[i + 1]
                
                # Tọa độ trung tâm của các cell
                x1 = c1 * cell_width + cell_width / 2
                y1 = r1 * cell_height + cell_height / 2
                x2 = c2 * cell_width + cell_width / 2
                y2 = r2 * cell_height + cell_height / 2
                
                # Vẽ đường thẳng đỏ với độ dày 3px
                pygame.draw.line(self.screen, path_color, (x1, y1), (x2, y2), 3)
    
    def draw_sidebar(self):
        """Vẽ sidebar với buttons và stats"""
        # Vẽ background cho sidebar
        sidebar_rect = pygame.Rect(self.GRID_AREA_WIDTH, 0, 
                                   self.SIDEBAR_WIDTH, self.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_DARK_GRAY, sidebar_rect)
        
        # Vẽ border cho sidebar
        pygame.draw.line(self.screen, COLOR_BLACK, 
                        (self.GRID_AREA_WIDTH, 0), 
                        (self.GRID_AREA_WIDTH, self.WINDOW_HEIGHT), 3)
        
        # ========== SECTION 1: Algorithm Selection ==========
        x_start = self.GRID_AREA_WIDTH + 10
        y_pos = 10
        
        # Algorithm dropdown với label
        label_text = self.label_font.render("Algorithm:", True, COLOR_WHITE)
        self.screen.blit(label_text, (x_start, y_pos))
        y_pos += 20  # Khoảng cách giữa label và dropdown
        
        # Cập nhật vị trí và width dropdown
        dropdown_width = min(230, self.SIDEBAR_WIDTH - 20)
        self.algorithm_dropdown.rect.x = x_start
        self.algorithm_dropdown.rect.y = y_pos
        self.algorithm_dropdown.rect.width = dropdown_width
        
        # Vẽ algorithm dropdown button
        color = COLOR_DARK_BLUE if self.algorithm_dropdown.is_open else COLOR_GRAY
        pygame.draw.rect(self.screen, color, self.algorithm_dropdown.rect)
        pygame.draw.rect(self.screen, COLOR_BLACK, self.algorithm_dropdown.rect, 2)
        
        arrow_x = self.algorithm_dropdown.rect.right - 20
        arrow_y = self.algorithm_dropdown.rect.centery
        if self.algorithm_dropdown.is_open:
            pygame.draw.polygon(self.screen, COLOR_WHITE, [
                (arrow_x, arrow_y - 5), (arrow_x - 5, arrow_y + 5), (arrow_x + 5, arrow_y + 5)
            ])
        else:
            pygame.draw.polygon(self.screen, COLOR_WHITE, [
                (arrow_x, arrow_y + 5), (arrow_x - 5, arrow_y - 5), (arrow_x + 5, arrow_y - 5)
            ])
        
        # Vẽ text với kiểm tra độ dài
        selected_text_str = self.algorithm_dropdown.get_selected()
        max_text_width = dropdown_width - 30
        selected_text = self.menu_font.render(selected_text_str, True, COLOR_WHITE)
        if selected_text.get_width() > max_text_width:
            # Cắt text nếu quá dài
            for i in range(len(selected_text_str), 0, -1):
                truncated = selected_text_str[:i] + "..."
                test_text = self.menu_font.render(truncated, True, COLOR_WHITE)
                if test_text.get_width() <= max_text_width:
                    selected_text = test_text
                    break
        text_rect = selected_text.get_rect(midleft=(self.algorithm_dropdown.rect.left + 5, 
                                                    self.algorithm_dropdown.rect.centery))
        self.screen.blit(selected_text, text_rect)
        
        # ========== SECTION 1.5: Movement Direction ==========
        y_pos = self.algorithm_dropdown.rect.bottom + 8
        label_text = self.label_font.render("Movement:", True, COLOR_WHITE)
        self.screen.blit(label_text, (x_start, y_pos))
        y_pos += 20
        
        # Cập nhật vị trí và width dropdown
        self.movement_dropdown.rect.x = x_start
        self.movement_dropdown.rect.y = y_pos
        self.movement_dropdown.rect.width = dropdown_width
        
        # Vẽ movement dropdown button
        color = COLOR_DARK_BLUE if self.movement_dropdown.is_open else COLOR_GRAY
        pygame.draw.rect(self.screen, color, self.movement_dropdown.rect)
        pygame.draw.rect(self.screen, COLOR_BLACK, self.movement_dropdown.rect, 2)
        
        arrow_x = self.movement_dropdown.rect.right - 20
        arrow_y = self.movement_dropdown.rect.centery
        if self.movement_dropdown.is_open:
            pygame.draw.polygon(self.screen, COLOR_WHITE, [
                (arrow_x, arrow_y - 5), (arrow_x - 5, arrow_y + 5), (arrow_x + 5, arrow_y + 5)
            ])
        else:
            pygame.draw.polygon(self.screen, COLOR_WHITE, [
                (arrow_x, arrow_y + 5), (arrow_x - 5, arrow_y - 5), (arrow_x + 5, arrow_y - 5)
            ])
        
        # Vẽ text với kiểm tra độ dài
        selected_text_str = self.movement_dropdown.get_selected()
        selected_text = self.menu_font.render(selected_text_str, True, COLOR_WHITE)
        if selected_text.get_width() > max_text_width:
            for i in range(len(selected_text_str), 0, -1):
                truncated = selected_text_str[:i] + "..."
                test_text = self.menu_font.render(truncated, True, COLOR_WHITE)
                if test_text.get_width() <= max_text_width:
                    selected_text = test_text
                    break
        text_rect = selected_text.get_rect(midleft=(self.movement_dropdown.rect.left + 5, 
                                                    self.movement_dropdown.rect.centery))
        self.screen.blit(selected_text, text_rect)
        
        # ========== SECTION 1.6: Energy Mode ==========
        y_pos = self.movement_dropdown.rect.bottom + 8
        label_text = self.label_font.render("Mode:", True, COLOR_WHITE)
        self.screen.blit(label_text, (x_start, y_pos))
        y_pos += 20
        
        # Cập nhật vị trí và width dropdown
        self.energy_dropdown.rect.x = x_start
        self.energy_dropdown.rect.y = y_pos
        self.energy_dropdown.rect.width = dropdown_width
        
        # Vẽ energy dropdown button
        color = COLOR_DARK_BLUE if self.energy_dropdown.is_open else COLOR_GRAY
        pygame.draw.rect(self.screen, color, self.energy_dropdown.rect)
        pygame.draw.rect(self.screen, COLOR_BLACK, self.energy_dropdown.rect, 2)
        
        arrow_x = self.energy_dropdown.rect.right - 20
        arrow_y = self.energy_dropdown.rect.centery
        if self.energy_dropdown.is_open:
            pygame.draw.polygon(self.screen, COLOR_WHITE, [
                (arrow_x, arrow_y - 5), (arrow_x - 5, arrow_y + 5), (arrow_x + 5, arrow_y + 5)
            ])
        else:
            pygame.draw.polygon(self.screen, COLOR_WHITE, [
                (arrow_x, arrow_y + 5), (arrow_x - 5, arrow_y - 5), (arrow_x + 5, arrow_y - 5)
            ])
        
        # Vẽ text với kiểm tra độ dài
        selected_text_str = self.energy_dropdown.get_selected()
        selected_text = self.menu_font.render(selected_text_str, True, COLOR_WHITE)
        if selected_text.get_width() > max_text_width:
            for i in range(len(selected_text_str), 0, -1):
                truncated = selected_text_str[:i] + "..."
                test_text = self.menu_font.render(truncated, True, COLOR_WHITE)
                if test_text.get_width() <= max_text_width:
                    selected_text = test_text
                    break
        text_rect = selected_text.get_rect(midleft=(self.energy_dropdown.rect.left + 5, 
                                                    self.energy_dropdown.rect.centery))
        self.screen.blit(selected_text, text_rect)
        
        # ========== SECTION 2: Pathfinding Actions (2 cột) ==========
        self.find_path_button.draw(self.screen)
        self.clear_path_button.draw(self.screen)
        
        # Animation Controls
        self.skip_animation_button.draw(self.screen)
        self.fast_forward_button.draw(self.screen)
        
        # ========== SECTION 3: Map Management (2 cột) ==========
        self.reset_button.draw(self.screen)
        
        # Random Map Size Dropdown
        y_pos = self.reset_button.rect.top
        label_text = self.label_font.render("Size:", True, COLOR_WHITE)
        self.screen.blit(label_text, (self.random_map_size_dropdown.rect.left, y_pos - 18))
        
        color = COLOR_DARK_BLUE if self.random_map_size_dropdown.is_open else COLOR_GRAY
        pygame.draw.rect(self.screen, color, self.random_map_size_dropdown.rect)
        pygame.draw.rect(self.screen, COLOR_BLACK, self.random_map_size_dropdown.rect, 2)
        
        arrow_x = self.random_map_size_dropdown.rect.right - 20
        arrow_y = self.random_map_size_dropdown.rect.centery
        if self.random_map_size_dropdown.is_open:
            pygame.draw.polygon(self.screen, COLOR_WHITE, [
                (arrow_x, arrow_y - 5), (arrow_x - 5, arrow_y + 5), (arrow_x + 5, arrow_y + 5)
            ])
        else:
            pygame.draw.polygon(self.screen, COLOR_WHITE, [
                (arrow_x, arrow_y + 5), (arrow_x - 5, arrow_y - 5), (arrow_x + 5, arrow_y - 5)
            ])
        
        selected_text = self.menu_font.render(self.random_map_size_dropdown.get_selected(), True, COLOR_WHITE)
        text_rect = selected_text.get_rect(midleft=(self.random_map_size_dropdown.rect.left + 5, 
                                                    self.random_map_size_dropdown.rect.centery))
        self.screen.blit(selected_text, text_rect)
        
        self.random_map_button.draw(self.screen)
        self.create_map_button.draw(self.screen)
        
        # Vẽ drawing mode buttons (ẩn TRAP/ROAD nếu không có energy_mode)
        for mode, btn in self.drawing_buttons.items():
            # Ẩn TRAP và ROAD buttons nếu không có energy_mode
            if mode in ['TRAP', 'ROAD'] and not self.energy_mode:
                continue  # Không vẽ button
            btn.active = (mode == self.drawing_mode)
            btn.draw(self.screen)
        
        # ========== SECTION 5: Algorithm Explanation ==========
        # Tính y_pos dựa trên vị trí của drawing buttons
        last_drawing_button = max(btn.rect.bottom for btn in self.drawing_buttons.values()) if self.drawing_buttons else self.random_map_button.rect.bottom
        y_pos = last_drawing_button + 14
        
        # Hiển thị giải thích thuật toán
        algo_name = self.algorithm_dropdown.get_selected()
        algo_explanation = self.get_algorithm_explanation(algo_name)
        
        explanation_title = self.title_font.render("Algorithm:", True, COLOR_WHITE)
        self.screen.blit(explanation_title, (x_start, y_pos))
        y_pos += 22
        
        # Vẽ giải thích (tối đa 4 dòng để hiển thị đầy đủ thông tin)
        explanation_lines = algo_explanation.split('\n')[:4]
        for line in explanation_lines:
            # Đảm bảo không vượt quá phần instructions
            if y_pos < self.WINDOW_HEIGHT - 300:  # Để lại không gian cho stats, legend, và instructions
                text = self.label_font.render(line, True, COLOR_WHITE)
                self.screen.blit(text, (x_start, y_pos))
                y_pos += 16
        
        y_pos += 10
        
        # ========== SECTION 6: Statistics ==========
        stats_title = self.title_font.render("Statistics:", True, COLOR_WHITE)
        self.screen.blit(stats_title, (x_start, y_pos))
        
        y_pos += 22
        if self.stats and 'algorithm' in self.stats:
            # Hiển thị algorithm hiện tại từ stats
            algorithm_name = self.stats.get('algorithm', self.algorithm_dropdown.get_selected())
            path_found = self.stats.get('path_found', True)  # Mặc định là True nếu không có key
            
            if not path_found:
                # Không tìm thấy path
                stats_lines = [
                    f"Algorithm: {algorithm_name}",
                    "Status: No Path Found",
                    "Explored all reachable nodes",
                    f"Time Taken: {self.stats.get('time_taken', '-'):.2f} ms"
                ]
            else:
                # Tìm thấy path
                path_length = self.stats.get('path_length', '-')
                total_energy = self.stats.get('total_energy', '-')
                stats_lines = [
                    f"Algorithm: {algorithm_name}",
                    f"Steps: {path_length}" if path_length != '-' else "Steps: -",
                    f"Energy Cost: {total_energy:.2f}" if isinstance(total_energy, (int, float)) else f"Energy Cost: {total_energy}",
                    f"Time Taken: {self.stats.get('time_taken', '-'):.2f} ms"
                ]
        else:
            # Hiển thị algorithm đang được chọn
            stats_lines = [
                f"Algorithm: {self.algorithm_dropdown.get_selected()}",
                "Steps: -",
                "Energy Cost: -",
                "Time Taken: -"
            ]
        
        for line in stats_lines:
            text = self.stats_font.render(line, True, COLOR_WHITE)
            self.screen.blit(text, (x_start, y_pos))
            y_pos += 18
        
        # ========== SECTION 7: Color Legend (2 cột để tiết kiệm) ==========
        y_pos += 16
        legend_title = self.title_font.render("Legend:", True, COLOR_WHITE)
        self.screen.blit(legend_title, (x_start, y_pos))
        
        y_pos += 22
        # Legend items - 2 cột để tiết kiệm không gian
        legend_items = [
            (COLOR_GREEN, "Start", None),
            (COLOR_RED, "End", None),
            (COLOR_RED, "Path", None),  # Đường thẳng đỏ
            (COLOR_WHITE, "O=Open", 'O'),  # Chữ O trên nền gốc
            (COLOR_WHITE, "X=Closed", 'X'),  # Chữ X trên nền gốc
            (COLOR_BLACK, "Wall", None),
            (COLOR_BROWN, "Trap(5)", None),
            (COLOR_LIGHT_BLUE, "Road(0.5)", None),
            (COLOR_WHITE, "Normal(1)", None)
        ]
        
        # Tính toán chiều cao legend: 9 items / 2 cột = 5 hàng, mỗi hàng 18px
        legend_height = ((len(legend_items) + 1) // 2) * 18
        instructions_start = self.WINDOW_HEIGHT - 85  # Vị trí bắt đầu instructions
        
        # Vẽ legend 2 cột, đảm bảo không chồng lên instructions
        for i, (color, label, marker) in enumerate(legend_items):
            col = i % 2
            row = i // 2
            x = x_start + col * 95  # 2 cột
            y = y_pos + row * 18
            
            # Chỉ vẽ nếu còn chỗ trên màn hình và không chồng lên instructions
            if y < instructions_start - 20:
                # Vẽ ô màu nhỏ
                color_rect = pygame.Rect(x, y, 15, 15)
                pygame.draw.rect(self.screen, color, color_rect)
                pygame.draw.rect(self.screen, COLOR_BLACK, color_rect, 1)
                
                # Vẽ marker nếu có (O hoặc X)
                if marker:
                    try:
                        import sys
                        marker_font = pygame.font.SysFont('arial', 12) if sys.platform == 'win32' else pygame.font.Font(None, 12)
                    except:
                        marker_font = pygame.font.Font(None, 12)
                    marker_color = COLOR_BLUE if marker == 'O' else COLOR_DARK_RED
                    marker_text = marker_font.render(marker, True, marker_color)
                    marker_rect = marker_text.get_rect(center=color_rect.center)
                    self.screen.blit(marker_text, marker_rect)
                
                # Vẽ text
                text = self.small_font.render(label, True, COLOR_WHITE)
                self.screen.blit(text, (x + 18, y))
        
        # ========== SECTION 8: Instructions (ngắn gọn) ==========
        # Tính toán vị trí để đảm bảo instructions hiển thị đầy đủ
        # Ước tính chiều cao cần thiết: 5 dòng * 15px = 75px
        instructions_height = 75
        y_pos = self.WINDOW_HEIGHT - instructions_height - 10  # Để lại 10px margin dưới
        
        instructions = [
            "Instructions:",
            "L-Click+Drag: Walls",
            "R-Click+Drag: Traps",
            "M-Click+Drag: Roads",
            "Keys: W/T/R/S/E/N"
        ]
        for line in instructions:
            if y_pos < self.WINDOW_HEIGHT - 5:  # Chỉ vẽ nếu còn chỗ
                text = self.small_font.render(line, True, COLOR_WHITE)
                self.screen.blit(text, (x_start, y_pos))
                y_pos += 15
    
    def get_algorithm_explanation(self, algo_name):
        """Trả về giải thích ngắn gọn về thuật toán"""
        explanations = {
            'BFS': 'BFS: Expand evenly (level by level).\nNodes may appear non-adjacent.\nAfter finding goal, backtrack\nfor shortest steps path.',
            'DFS': 'DFS: Go deep in one direction.\nNodes may appear far apart.\nAfter finding goal, backtrack\nfor path (may not be optimal).',
            'Dijkstra': 'Dijkstra: Prioritize low cost.\nNodes may jump by cost.\nAfter finding goal, backtrack\nfor lowest energy path.',
            'A*': 'A*: Prioritize f=g+h score.\nNodes may jump by priority.\nAfter finding goal, backtrack\nfor optimal path (steps+energy).'
        }
        return explanations.get(algo_name, 'Select algorithm to see explanation.')
    
    def handle_event(self, event):
        """Xử lý events"""
        # Mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            # Kiểm tra dropdowns trước
            # Kiểm tra algorithm dropdown - kiểm tra cả button và dropdown menu
            dropdown_clicked = False
            if self.algorithm_dropdown.rect.collidepoint(pos):
                dropdown_clicked = True
            elif self.algorithm_dropdown.is_open:
                # Kiểm tra xem có click vào option nào không
                for i in range(len(self.algorithm_dropdown.options)):
                    option_rect = pygame.Rect(self.algorithm_dropdown.rect.x, 
                                            self.algorithm_dropdown.rect.bottom + i * self.algorithm_dropdown.height,
                                            self.algorithm_dropdown.rect.width, 
                                            self.algorithm_dropdown.height)
                    if option_rect.collidepoint(pos):
                        dropdown_clicked = True
                        break
            
            if dropdown_clicked:
                algorithm_changed = self.algorithm_dropdown.is_clicked(pos)
                if algorithm_changed:
                    # Algorithm đã thay đổi, clear path
                    self.clear_path()
                    self.previous_algorithm = self.algorithm_dropdown.get_selected()
                return
            
            # Kiểm tra movement dropdown
            movement_dropdown_clicked = False
            if self.movement_dropdown.rect.collidepoint(pos):
                movement_dropdown_clicked = True
            elif self.movement_dropdown.is_open:
                for i in range(len(self.movement_dropdown.options)):
                    option_rect = pygame.Rect(self.movement_dropdown.rect.x,
                                            self.movement_dropdown.rect.bottom + i * self.movement_dropdown.height,
                                            self.movement_dropdown.rect.width,
                                            self.movement_dropdown.height)
                    if option_rect.collidepoint(pos):
                        movement_dropdown_clicked = True
                        break
            
            if movement_dropdown_clicked:
                movement_changed = self.movement_dropdown.is_clicked(pos)
                if movement_changed:
                    # Movement đã thay đổi, clear path và cập nhật pathfinder
                    self.clear_path()
                    movement_selected = self.movement_dropdown.get_selected()
                    self.allow_diagonal = (movement_selected == '8 Directions')
                    self.pathfinder = PathfindingAlgorithms(self.grid, allow_diagonal=self.allow_diagonal)
                return
            
            # Kiểm tra energy dropdown
            energy_dropdown_clicked = False
            if self.energy_dropdown.rect.collidepoint(pos):
                energy_dropdown_clicked = True
            elif self.energy_dropdown.is_open:
                for i in range(len(self.energy_dropdown.options)):
                    option_rect = pygame.Rect(self.energy_dropdown.rect.x,
                                            self.energy_dropdown.rect.bottom + i * self.energy_dropdown.height,
                                            self.energy_dropdown.rect.width,
                                            self.energy_dropdown.height)
                    if option_rect.collidepoint(pos):
                        energy_dropdown_clicked = True
                        break
            
            if energy_dropdown_clicked:
                energy_changed = self.energy_dropdown.is_clicked(pos)
                if energy_changed:
                    # Energy mode đã thay đổi, cập nhật và clear path
                    self.update_energy_mode()
                    self.clear_path()
                return
            
            if self.random_map_size_dropdown.is_clicked(pos):
                return
            
            # Kiểm tra buttons
            if self.find_path_button.is_clicked(pos):
                self.find_path()
                return
            elif self.clear_path_button.is_clicked(pos):
                self.clear_path()
                return
            elif self.skip_animation_button.is_clicked(pos):
                self.skip_animation = True
                return
            elif self.fast_forward_button.is_clicked(pos):
                self.fast_forward()
                return
            elif self.reset_button.is_clicked(pos):
                self.reset_grid()
                return
            elif self.random_map_button.is_clicked(pos):
                self.generate_random_map()
                return
            elif self.create_map_button.is_clicked(pos):
                self.load_map_from_file()
                return
            
            # Đóng dropdowns nếu click bên ngoài
            self.algorithm_dropdown.handle_click_outside(pos)
            self.movement_dropdown.handle_click_outside(pos)
            self.energy_dropdown.handle_click_outside(pos)
            self.random_map_size_dropdown.handle_click_outside(pos)
            
            # Kiểm tra drawing mode buttons (chỉ cho phép click nếu button hiển thị)
            for mode, btn in self.drawing_buttons.items():
                # Ẩn TRAP và ROAD buttons nếu không có energy_mode
                if mode in ['TRAP', 'ROAD'] and not self.energy_mode:
                    continue
                if btn.is_clicked(pos):
                    self.drawing_mode = mode
                    return
            
            # Xử lý click trên grid
            if pos[0] < self.GRID_AREA_WIDTH:
                self.handle_mouse_click(pos, event.button)
        
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0] or event.buttons[2] or event.buttons[1]:
                if event.pos[0] < self.GRID_AREA_WIDTH:
                    self.handle_mouse_drag(event.pos, 
                                         1 if event.buttons[0] else (3 if event.buttons[2] else 2))
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_drawing = False
            self.last_draw_pos = None
        
        # Keyboard shortcuts
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.drawing_mode = 'WALL'
            elif event.key == pygame.K_t:
                # Chỉ cho phép nếu energy_mode = True
                if self.energy_mode:
                    self.drawing_mode = 'TRAP'
            elif event.key == pygame.K_r:
                # Chỉ cho phép nếu energy_mode = True
                if self.energy_mode:
                    self.drawing_mode = 'ROAD'
            elif event.key == pygame.K_s:
                self.drawing_mode = 'START'
            elif event.key == pygame.K_e:
                self.drawing_mode = 'END'
            elif event.key == pygame.K_n:
                self.drawing_mode = 'NORMAL'
    
    def handle_resize(self, new_width, new_height):
        """Xử lý khi window được resize"""
        # Giới hạn kích thước tối thiểu
        new_width = max(self.MIN_WINDOW_WIDTH, new_width)
        new_height = max(self.MIN_WINDOW_HEIGHT, new_height)
        
        self.WINDOW_WIDTH = new_width
        self.WINDOW_HEIGHT = new_height
        
        # Tính lại kích thước grid area và sidebar
        self.SIDEBAR_WIDTH = min(450, max(350, new_width - 800))  # Tăng min width
        self.GRID_AREA_WIDTH = new_width - self.SIDEBAR_WIDTH
        self.GRID_AREA_HEIGHT = new_height
        
        # Tạo lại screen với kích thước mới
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.RESIZABLE)
        
        # Tạo lại buttons với vị trí mới (dựa trên GRID_AREA_WIDTH mới)
        self.create_buttons()
    
    def skip_to_end(self):
        """Bỏ qua animation, hiển thị kết quả ngay"""
        # Xử lý tất cả animation queue còn lại
        while self.animation_queue:
            node, state = self.animation_queue.pop(0)
            if state == 'open':
                self.animation_nodes['open'].add((node.row, node.col))
            elif state == 'closed':
                self.animation_nodes['closed'].add((node.row, node.col))
                self.animation_nodes['open'].discard((node.row, node.col))
        
        # Nếu pathfinding đã hoàn thành, hiển thị kết quả ngay
        if self.pathfinding_result is not None and not self.pathfinding_running:
            path, stats = self.pathfinding_result
            self.stats = stats
            if path:
                self.path = path
                # Đánh dấu tất cả các ô trong path là đã đi qua
                self.robot_visited_path = list(path)
                self.robot_path = None
                self.robot_animating = False
            self.is_animating = False
            self.pathfinding_result = None
        elif self.robot_animating and self.robot_path:
            # Robot đang di chuyển, cho robot đến đích ngay
            self.robot_path_index = len(self.robot_path) - 1
            # Đánh dấu tất cả các ô trong path là đã đi qua
            self.robot_visited_path = list(self.robot_path)
            self.path = self.robot_path
            self.robot_animating = False
    
    def fast_forward(self):
        """Tua nhanh animation"""
        # Giảm animation speed xuống 1/4
        self.animation_speed = max(1, self.animation_speed // 4)
        self.robot_speed = max(1, self.robot_speed // 4)
    
    def update_animation(self):
        """Cập nhật animation từng bước"""
        if self.skip_animation:
            self.skip_to_end()
            self.skip_animation = False
            return
        
        if self.animation_paused:
            return
        
        # Xử lý animation queue - xử lý từng bước để thấy rõ quá trình
        if self.is_animating and self.animation_queue:
            self.animation_frame_count += 1
            if self.animation_frame_count >= self.animation_speed:
                self.animation_frame_count = 0
                # Xử lý một animation step mỗi lần để thấy rõ quá trình
                node, state = self.animation_queue.pop(0)
                if state == 'open':
                    self.animation_nodes['open'].add((node.row, node.col))
                elif state == 'closed':
                    self.animation_nodes['closed'].add((node.row, node.col))
                    self.animation_nodes['open'].discard((node.row, node.col))
        
        # Kiểm tra xem pathfinding đã hoàn thành chưa
        if self.pathfinding_result is not None and not self.pathfinding_running:
            path, stats = self.pathfinding_result
            self.stats = stats
            
            # Xử lý các animation steps còn lại từng bước (không xử lý hết ngay)
            if self.animation_queue:
                # Vẫn còn animation steps, tiếp tục xử lý từng bước
                # Điều này đảm bảo animation hiển thị đầy đủ ngay cả khi không tìm thấy path
                pass
            else:
                # Đã xử lý hết animation, bắt đầu robot animation hoặc kết thúc
                if path:
                    # Tìm thấy path, bắt đầu robot animation
                    self.robot_path = path
                    self.robot_path_index = 0
                    self.robot_animating = True
                    self.robot_frame_count = 0
                    self.robot_visited_path = []  # Reset danh sách đã đi qua
                    # Path sẽ được hiển thị sau khi robot đi hết
                    self.path = None
                    self.is_animating = False  # Kết thúc animation O/X
                    self.pathfinding_result = None  # Clear result để không xử lý lại
                else:
                    # Không tìm thấy path - vẫn giữ animation để người dùng thấy quá trình khám phá
                    # Animation O/X sẽ hiển thị tất cả các node đã khám phá
                    self.path = None
                    self.is_animating = False  # Kết thúc animation nhưng giữ lại O/X markers
                    self.pathfinding_result = None
                    # Thêm thông báo vào stats
                    if 'algorithm' in self.stats:
                        self.stats['path_found'] = False
        
        # Cập nhật robot animation
        if self.robot_animating and self.robot_path:
            self.robot_frame_count += 1
            if self.robot_frame_count >= self.robot_speed:
                self.robot_frame_count = 0
                
                # Thêm ô hiện tại vào danh sách đã đi qua (trước khi di chuyển)
                if self.robot_path_index < len(self.robot_path):
                    current_pos = self.robot_path[self.robot_path_index]
                    if current_pos not in self.robot_visited_path:
                        self.robot_visited_path.append(current_pos)
                
                self.robot_path_index += 1
                
                # Nếu robot đã đi hết path, hiển thị path và kết thúc
                if self.robot_path_index >= len(self.robot_path):
                    # Thêm ô cuối cùng vào danh sách đã đi qua
                    if self.robot_path:
                        last_pos = self.robot_path[-1]
                        if last_pos not in self.robot_visited_path:
                            self.robot_visited_path.append(last_pos)
                    self.path = self.robot_path  # Hiển thị path sau khi robot đi hết
                    self.robot_animating = False
                    self.is_animating = False
    
    def run(self):
        """Vòng lặp chính"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    # Xử lý resize window
                    self.handle_resize(event.w, event.h)
                
                self.handle_event(event)
            
            # Cập nhật animation
            self.update_animation()
            
            # Draw - Thứ tự vẽ quan trọng để dropdown hiển thị đúng
            self.screen.fill(COLOR_DARK_GRAY)
            self.draw_grid()
            self.draw_sidebar()
            
            # Vẽ dropdown menus SAU CÙNG để không bị che bởi các elements khác
            # Algorithm dropdown
            if self.algorithm_dropdown.is_open:
                dropdown_height = len(self.algorithm_dropdown.options) * self.algorithm_dropdown.height
                dropdown_rect = pygame.Rect(self.algorithm_dropdown.rect.x, 
                                            self.algorithm_dropdown.rect.bottom, 
                                            self.algorithm_dropdown.rect.width, 
                                            dropdown_height)
                pygame.draw.rect(self.screen, COLOR_WHITE, dropdown_rect)
                pygame.draw.rect(self.screen, COLOR_BLACK, dropdown_rect, 3)
                
                for i, option in enumerate(self.algorithm_dropdown.options):
                    option_rect = pygame.Rect(self.algorithm_dropdown.rect.x, 
                                            self.algorithm_dropdown.rect.bottom + i * self.algorithm_dropdown.height, 
                                            self.algorithm_dropdown.rect.width, 
                                            self.algorithm_dropdown.height)
                    if i == self.algorithm_dropdown.selected_index:
                        pygame.draw.rect(self.screen, COLOR_DARK_BLUE, option_rect)
                    else:
                        mouse_pos = pygame.mouse.get_pos()
                        if option_rect.collidepoint(mouse_pos):
                            pygame.draw.rect(self.screen, COLOR_LIGHT_GRAY, option_rect)
                    
                    option_text = self.menu_font.render(option, True, 
                                                  COLOR_BLACK if i != self.algorithm_dropdown.selected_index else COLOR_WHITE)
                    text_rect = option_text.get_rect(midleft=(option_rect.left + 5, option_rect.centery))
                    self.screen.blit(option_text, text_rect)
            
            # Movement dropdown
            if self.movement_dropdown.is_open:
                dropdown_height = len(self.movement_dropdown.options) * self.movement_dropdown.height
                dropdown_rect = pygame.Rect(self.movement_dropdown.rect.x,
                                            self.movement_dropdown.rect.bottom,
                                            self.movement_dropdown.rect.width,
                                            dropdown_height)
                pygame.draw.rect(self.screen, COLOR_WHITE, dropdown_rect)
                pygame.draw.rect(self.screen, COLOR_BLACK, dropdown_rect, 3)
                
                for i, option in enumerate(self.movement_dropdown.options):
                    option_rect = pygame.Rect(self.movement_dropdown.rect.x,
                                            self.movement_dropdown.rect.bottom + i * self.movement_dropdown.height,
                                            self.movement_dropdown.rect.width,
                                            self.movement_dropdown.height)
                    if i == self.movement_dropdown.selected_index:
                        pygame.draw.rect(self.screen, COLOR_DARK_BLUE, option_rect)
                    else:
                        mouse_pos = pygame.mouse.get_pos()
                        if option_rect.collidepoint(mouse_pos):
                            pygame.draw.rect(self.screen, COLOR_LIGHT_GRAY, option_rect)
                    
                    option_text = self.menu_font.render(option, True,
                                                  COLOR_BLACK if i != self.movement_dropdown.selected_index else COLOR_WHITE)
                    text_rect = option_text.get_rect(midleft=(option_rect.left + 5, option_rect.centery))
                    self.screen.blit(option_text, text_rect)
            
            # Energy dropdown
            if self.energy_dropdown.is_open:
                dropdown_height = len(self.energy_dropdown.options) * self.energy_dropdown.height
                dropdown_rect = pygame.Rect(self.energy_dropdown.rect.x,
                                            self.energy_dropdown.rect.bottom,
                                            self.energy_dropdown.rect.width,
                                            dropdown_height)
                pygame.draw.rect(self.screen, COLOR_WHITE, dropdown_rect)
                pygame.draw.rect(self.screen, COLOR_BLACK, dropdown_rect, 3)
                
                for i, option in enumerate(self.energy_dropdown.options):
                    option_rect = pygame.Rect(self.energy_dropdown.rect.x,
                                            self.energy_dropdown.rect.bottom + i * self.energy_dropdown.height,
                                            self.energy_dropdown.rect.width,
                                            self.energy_dropdown.height)
                    if i == self.energy_dropdown.selected_index:
                        pygame.draw.rect(self.screen, COLOR_DARK_BLUE, option_rect)
                    else:
                        mouse_pos = pygame.mouse.get_pos()
                        if option_rect.collidepoint(mouse_pos):
                            pygame.draw.rect(self.screen, COLOR_LIGHT_GRAY, option_rect)
                    
                    option_text = self.menu_font.render(option, True,
                                                  COLOR_BLACK if i != self.energy_dropdown.selected_index else COLOR_WHITE)
                    text_rect = option_text.get_rect(midleft=(option_rect.left + 5, option_rect.centery))
                    self.screen.blit(option_text, text_rect)
            
            # Random Map Size dropdown
            if self.random_map_size_dropdown.is_open:
                dropdown_height = len(self.random_map_size_dropdown.options) * self.random_map_size_dropdown.height
                dropdown_rect = pygame.Rect(self.random_map_size_dropdown.rect.x, 
                                            self.random_map_size_dropdown.rect.bottom, 
                                            self.random_map_size_dropdown.rect.width, 
                                            dropdown_height)
                pygame.draw.rect(self.screen, COLOR_WHITE, dropdown_rect)
                pygame.draw.rect(self.screen, COLOR_BLACK, dropdown_rect, 3)
                
                for i, option in enumerate(self.random_map_size_dropdown.options):
                    option_rect = pygame.Rect(self.random_map_size_dropdown.rect.x, 
                                            self.random_map_size_dropdown.rect.bottom + i * self.random_map_size_dropdown.height, 
                                            self.random_map_size_dropdown.rect.width, 
                                            self.random_map_size_dropdown.height)
                    if i == self.random_map_size_dropdown.selected_index:
                        pygame.draw.rect(self.screen, COLOR_DARK_BLUE, option_rect)
                    else:
                        mouse_pos = pygame.mouse.get_pos()
                        if option_rect.collidepoint(mouse_pos):
                            pygame.draw.rect(self.screen, COLOR_LIGHT_GRAY, option_rect)
                    
                    option_text = self.menu_font.render(option, True, 
                                                  COLOR_BLACK if i != self.random_map_size_dropdown.selected_index else COLOR_WHITE)
                    text_rect = option_text.get_rect(midleft=(option_rect.left + 5, option_rect.centery))
                    self.screen.blit(option_text, text_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()


def main():
    """Hàm main"""
    app = PathfindingSimulation()
    app.run()


if __name__ == "__main__":
    main()
