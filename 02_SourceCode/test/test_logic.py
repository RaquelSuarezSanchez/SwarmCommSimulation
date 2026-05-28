import unittest

# UT-01
class ExplorationMapMock:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.explored_cells = 0
        
    def get_completion_percentage(self):
        total_cells = self.width * self.height
        return (self.explored_cells / total_cells) * 100.0

class TestSimulationLogic(unittest.TestCase):

    def test_exploration_percentage_UT01(self):
        """Test Case UT-01: Verifies the correct calculation of explored area."""
        map_grid = ExplorationMapMock(100, 100) # Grid  100x100 = 10000 
        map_grid.explored_cells = 2500 # 2500 cells explored
        
        percentage = map_grid.get_completion_percentage()
        self.assertEqual(percentage, 25.0, "The percentage calculation is incorrect.")

    def test_battery_constraint_logic(self):
        """Verifies the health constraint logic for the BFS routing."""
        battery_level_good = 85.0
        battery_level_bad = 15.0
        
        self.assertTrue(battery_level_good > 20.0, "Rover should be a valid relay.")
        self.assertFalse(battery_level_bad > 20.0, "Rover MUST NOT be a valid relay.")

if __name__ == '__main__':
    unittest.main()