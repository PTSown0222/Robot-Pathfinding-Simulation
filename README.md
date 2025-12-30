<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=auto&height=200&section=header&text=Robot%20Pathfinding&fontSize=70" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Pygame-ed1c24?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Algorithms-A%20*%20|%20Dijkstra-blue?style=for-the-badge" />
</p>

<p align="center">
  <b>Robot Pathfinding Simulation</b>
</p>
## 🎬 Demo
![Robot Pathfinding Demo](assets/Demo.gif)

## ✨ Tính năng chính

### 🗺️ Grid System
- **Lưới động**: Từ 10x10 đến 30x30 (mặc định 20x20)
- **Hỗ trợ 2 chế độ di chuyển**:
  - **4 Directions**: Chỉ đi Lên, Xuống, Trái, Phải (chi phí = 1.0)
  - **8 Directions**: Bao gồm cả 4 hướng chéo (chi phí chéo = √2 ≈ 1.414)

### 🎨 Cell Types
- **Normal Cell** (Trắng): Chi phí = 1 Energy
- **Wall** (Đen): Không thể đi qua
- **Trap/High Cost** (Nâu): Chi phí = 5 Energy
- **Road/Low Cost** (Xanh nhạt): Chi phí = 0.5 Energy
- **Start** (Xanh lá): Điểm bắt đầu
- **End** (Đỏ): Điểm kết thúc

### ⚡ Energy Mode vs Simple Mode
- **Energy Mode** (Mặc định):
  - Đầy đủ tính năng với TRAP và ROAD
  - Tính toán chi phí năng lượng
  - Tự động thêm TRAP/ROAD khi chuyển từ Simple Mode
  
- **Simple Mode**:
  - Chỉ có WALL và NORMAL (trắng đen)
  - Ẩn buttons TRAP/ROAD
  - Tự động chuyển TRAP/ROAD thành NORMAL khi chuyển mode

### 🔍 Thuật toán Pathfinding
- **BFS** (Breadth-First Search): Tìm đường ngắn nhất về số bước, bỏ qua weights
- **DFS** (Depth-First Search): Không đảm bảo đường ngắn nhất, bỏ qua weights
- **Dijkstra**: Tìm đường với chi phí thấp nhất (tôn trọng weights)
- **A***: Sử dụng heuristic + cost, tối ưu cho cả số bước và chi phí

**Heuristic tự động**:
- 4 Directions: Manhattan Distance
- 8 Directions: Euclidean Distance

### 🎬 Visualization
- **Open Set** (Chữ O màu xanh): Các node đang được xét
- **Closed Set** (Chữ X màu đỏ): Các node đã xét
- **Robot Animation**: Robot di chuyển từng bước trên đường đi
- **Final Path** (Đường thẳng đỏ): Đường đi cuối cùng sau khi robot hoàn thành

### 🎲 Random Map Generator
- Tự động tạo map ngẫu nhiên (10x10 đến 30x30)
- Đảm bảo có đầy đủ cell types (Walls, Traps, Roads, Normal) - tùy theo Energy Mode
- Đảm bảo có đường đi từ Start đến End (có đáp án)
- Chất lượng tốt để test các thuật toán và so sánh Energy vs Steps

### 🎨 Giao diện
- **Viền màu đậm**: Mỗi loại cell có viền màu đậm hơn của chính màu đó để dễ nhận biết
- **Animation mượt mà**: Hiển thị từng bước quá trình tìm đường
- **Statistics real-time**: Hiển thị Path Length, Total Energy, Time Taken

## 📦 Cài đặt

### Yêu cầu
- Python 3.7 trở lên
- Pygame

### Cài đặt dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Sử dụng

### Chạy chương trình
```bash
python robot_astar_ui.py
```

### Giao diện
- **Bên trái**: Grid hiển thị map
- **Bên phải**: Control Panel với các tùy chọn

### Các bước cơ bản
1. **Chọn chế độ**:
   - **Movement**: 4 Directions hoặc 8 Directions
   - **Mode**: Energy Mode hoặc Simple Mode
   
2. **Tạo map**:
   - Click "Random Map" để tạo map tự động
   - Hoặc vẽ thủ công bằng chuột
   
3. **Chọn thuật toán**: BFS, DFS, Dijkstra, hoặc A*
   
4. **Tìm đường**: Click "Find Path"

5. **Xem kết quả**: Statistics hiển thị Path Length, Total Energy, Time Taken

## 🎮 Điều khiển

### Chuột
- **Left Click + Drag**: Vẽ Walls (hoặc cell type đã chọn)
- **Right Click + Drag**: Vẽ Traps (chỉ khi Energy Mode)
- **Middle Click + Drag**: Vẽ Roads (chỉ khi Energy Mode)
- **Click đơn**: Đặt Start/End

### Bàn phím
- **W**: Chế độ Wall
- **T**: Chế độ Trap (chỉ khi Energy Mode)
- **R**: Chế độ Road (chỉ khi Energy Mode)
- **S**: Chế độ Start
- **E**: Chế độ End
- **N**: Chế độ Normal

### Buttons
- **Find Path**: Chạy thuật toán đã chọn
- **Clear Path**: Xóa đường đi và animation, giữ lại map
- **Reset Grid**: Reset về grid trống
- **Random Map**: Tạo map ngẫu nhiên mới
- **Skip**: Bỏ qua animation, hiển thị kết quả ngay
- **Fast**: Tua nhanh animation

## 📊 So sánh thuật toán

### BFS vs Dijkstra
- **BFS**: Có thể tìm đường với ít bước hơn nhưng chi phí cao hơn (nếu đi qua traps)
- **Dijkstra**: Tìm đường với chi phí thấp nhất (tránh traps) nhưng có thể có nhiều bước hơn

### A*
- Kết hợp heuristic và cost để tối ưu cả số bước và chi phí
- Nhanh hơn Dijkstra nhờ có heuristic hướng về đích

### 4 Directions vs 8 Directions
- **4 Directions**: Chỉ đi thẳng, chi phí mỗi bước = 1.0
- **8 Directions**: Có thể đi chéo, chi phí chéo = √2 ≈ 1.414
- 8 Directions thường tìm được đường ngắn hơn về số bước

## 📁 Cấu trúc code

```
robot_astar.py          # Backend logic: Node, Grid, PathfindingAlgorithms
robot_astar_ui.py       # Frontend UI: Pygame interface
requirements.txt        # Dependencies
README.md              # Tài liệu tổng quan

```

## 🔧 Các class chính

### robot_astar.py
- **Node**: Đại diện một ô trong bản đồ
- **Grid**: Quản lý lưới 2D các Node
- **PathfindingAlgorithms**: Triển khai 4 thuật toán (BFS, DFS, Dijkstra, A*)
- **AStarRobot**: Thuật toán A* cơ bản (dùng trong main())

### robot_astar_ui.py
- **Button**: Nút bấm đơn giản
- **Dropdown**: Menu dropdown
- **PathfindingSimulation**: Giao diện Pygame chính

## 💡 Mẹo sử dụng

1. **Test với Random Map trước**: Sử dụng nút "Random Map" để có map đầy đủ và có đáp án ngay

2. **So sánh 4 vs 8 Directions**:
   - Tạo map có nhiều obstacles
   - Chạy với 4 Directions và 8 Directions
   - Quan sát sự khác biệt về số bước và chi phí

3. **So sánh BFS vs Dijkstra**:
   - Tạo map có nhiều traps
   - Chạy BFS: sẽ đi thẳng qua traps (ít steps, nhiều energy)
   - Chạy Dijkstra: sẽ tránh traps (nhiều steps, ít energy)

4. **Quan sát Animation**:
   - Xem cách mỗi thuật toán "khám phá" map
   - BFS mở rộng đều theo mọi hướng
   - A* hướng về End nhanh hơn

5. **Energy Mode vs Simple Mode**:
   - Simple Mode: Tập trung vào logic tìm đường cơ bản (chỉ WALL/NORMAL)
   - Energy Mode: Test tối ưu hóa chi phí với TRAP/ROAD

## ⚠️ Lưu ý

1. **Start và End phải có đường đi**: Nếu không có đường đi, thuật toán sẽ không tìm được path

2. **Walls không thể đi qua**: Đảm bảo có ít nhất một đường đi từ Start đến End

3. **Random Map đảm bảo có đáp án**: Map được tạo tự động luôn có đường đi

4. **Grid size tự động thay đổi**: Khi dùng Random Map, grid size có thể thay đổi (10x10 đến 30x30)

5. **Energy Mode**: Khi chuyển từ Simple Mode sang Energy Mode, TRAP/ROAD sẽ tự động được thêm vào nếu chưa có

## 🐛 Xử lý lỗi

### Không tìm thấy đường đi
- Kiểm tra xem có đường đi từ Start đến End không
- Sử dụng "Random Map" để tạo map mới có đáp án

### Statistics hiển thị sai
- Click "Clear Path" và chạy lại "Find Path"
- Đảm bảo đã chọn thuật toán trước khi click "Find Path"

### Button không hoạt động
- Đảm bảo click đúng vào button (không phải text)
- Thử click lại hoặc restart chương trình

### 📊 Bảng so sánh đặc điểm
| Thuật toán | Ưu điểm | Nhược điểm | Đảm bảo ngắn nhất? |
| :--- | :--- | :--- | :---: |
| **BFS** | Tìm đường ít bước nhất | Chạy chậm trên map lớn | ✅ |
| **DFS** | Tốn ít bộ nhớ | Đường đi thường rất dài | ❌ |
| **Dijkstra** | Luôn tìm đường rẻ nhất | Khám phá mù quáng mọi hướng | ✅ |
| **A\*** | Nhanh và hiệu quả nhất | Cần hàm Heuristic tốt | ✅ |

## 👨‍💻 Tác giả
Phương Thế Sơn

## 📄 License
Dự án học tập - Sử dụng tự do cho mục đích giáo dục
# robot-pathffinding-project-CS106

