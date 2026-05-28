from abc import ABC, abstractmethod
import numpy as np

class ExplorationStrategy(ABC):
    """
    Base interface for the strategy pattern used for the exploration mode
    """
    @abstractmethod
    def manageMove(self, robot, exp_map, x_lims, y_lims, dt, margin):
        pass

    @abstractmethod
    def check_end(self, porcentaje):
        pass


class FreeExploration(ExplorationStrategy):
    """
    Strategy 1: Map grows when a robot touches one of the sides.
    """
    def manageMove(self, robot, exp_map, x_lims, y_lims, dt, margin):
        robot.pos += robot.vel * dt
        x, y = robot.pos
        map_expanded = False
        step = 50.0
        
        # Check sides
        if (x - x_lims[0] < margin) or (x_lims[1] - x < margin) or \
           (y - y_lims[0] < margin) or (y_lims[1] - y < margin):
            x_lims[0] -= step # Grow
            x_lims[1] += step
            y_lims[0] -= step
            y_lims[1] += step
            
            # Update map
            exp_map.expand(x_lims, y_lims)
            map_expanded = True
            
        return map_expanded

    def check_end(self, porcentaje):
        return False # In free exploration, the area is never finished


class FixedExploration(ExplorationStrategy):
    """
    Strategy 2: Map is fixed, robots bounce against the walls.
    """
    def manageMove(self, robot, exp_map, x_lims, y_lims, dt, margin):
        next_pos = robot.pos + robot.vel * dt # Where will the robot be next?
        hit_wall = False
        
        if next_pos[0] - margin <= x_lims[0] or next_pos[0] + margin >= x_lims[1]:
            robot.vel[0] *= -1 
            hit_wall = True
            
        if next_pos[1] - margin <= y_lims[0] or next_pos[1] + margin >= y_lims[1]:
            robot.vel[1] *= -1
            hit_wall = True
            
        # Add random rotation
        if hit_wall:
            # Random angle between -pi/6 (-30 degrees) and pi/6 (30 degrees)
            angle_noise = np.random.uniform(-np.pi/6, np.pi/6)
            cos_a = np.cos(angle_noise)
            sin_a = np.sin(angle_noise)
            
            vx, vy = robot.vel
            robot.vel[0] = vx * cos_a - vy * sin_a
            robot.vel[1] = vx * sin_a + vy * cos_a

        robot.pos += robot.vel * dt # Move robot
        return False # Never expand map
    
    def check_end(self, porcentaje):
        return porcentaje >= 99.0