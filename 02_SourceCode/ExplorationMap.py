import numpy as np

class ExplorationMap:
    def __init__(self, x_bounds, y_bounds, resolution=0.5):
        # Limits: [min, max]
        self.x_min, self.x_max = x_bounds
        self.y_min, self.y_max = y_bounds
        self.res = resolution
        
        # How many cells do we need?
        self.width = int(round((self.x_max - self.x_min) / self.res))
        self.height = int(round((self.y_max - self.y_min) / self.res))
        
        # Matrix of 0s
        self.grid = np.zeros((self.height, self.width))

    def update(self, robot_pos, radius=10.0):
        # Position of rover to index in matrix
        cx = int(round((robot_pos[0] - self.x_min) / self.res))
        cy = int(round((robot_pos[1] - self.y_min) / self.res))
        
        # Convert radius to cells
        r_cells = int(round(radius / self.res))

        # Check cells in the radius
        for i in range(max(0, cy - r_cells), min(self.height, cy + r_cells)):
            for j in range(max(0, cx - r_cells), min(self.width, cx + r_cells)):
                # Distance between robots (in cells)
                dist = np.sqrt((i - cy)**2 + (j - cx)**2)
                if dist <= r_cells:
                    self.grid[i, j] = 1 

    def get_completion_percentage(self):
        total_cells = self.grid.size
        explored_cells = np.sum(self.grid)
        return (explored_cells / total_cells) * 100

    def expand(self, new_x_bounds, new_y_bounds):
        # Save previous data
        old_x_min = self.x_min
        old_y_min = self.y_min
        old_width = self.width
        old_height = self.height
        old_grid = self.grid.copy() # Backup

        # New limits
        self.x_min, self.x_max = new_x_bounds
        self.y_min, self.y_max = new_y_bounds

        # New size
        self.width = int(round((self.x_max - self.x_min) / self.res))
        self.height = int(round((self.y_max - self.y_min) / self.res))
        self.grid = np.zeros((self.height, self.width))

        # Growth (offset)
        shift_x = int(round((old_x_min - self.x_min) / self.res))
        shift_y = int(round((old_y_min - self.y_min) / self.res))

        if shift_x >= 0 and shift_y >= 0:
            self.grid[shift_y : shift_y + old_height, shift_x : shift_x + old_width] = old_grid