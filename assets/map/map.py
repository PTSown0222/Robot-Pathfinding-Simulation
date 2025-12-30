import importlib

def get_map(size="small"):
    """
    Trả về ma trận bản đồ numpy ứng với kích thước:
    - size: 'small' → 10x10
           'medium' → 20x20
           'large' → 30x30
    """
    module_map = {
        "small": "assets.map.10x10",
        "medium": "assets.map.20x20",
        "large": "assets.map.30x30",
    }
    if size not in module_map:
        raise ValueError("Kích thước bản đồ phải là 'small', 'medium', hoặc 'large'.")

    module_name = module_map[size]
    module = importlib.import_module(module_name)
    # Tên biến chuẩn trong từng file: classroom_map
    return module.classroom_map
