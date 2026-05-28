import matplotlib.pyplot as plt
import argparse

from config import HOST, BASE_PORT, UMBRAL, SIM_TIME, DT, EXPLORATION_RADIUS, MAP_FILE
from ExplorationMap import ExplorationMap
from ExplorationStrategy import FreeExploration, FixedExploration
from utils.maps_util import load_map
from utils.visualization import show_map, updateLargeMap, draw_network_connections, setup_window_closing, add_info_text, add_pause_button, setup_simulation_graphics
from utils.simulation_utils import get_user_inputs, create_robots, build_routing_tree, update_network_relays, update_robots_movement, process_network_turn


def main(config_file=None, gui_data=None):
    plt.close('all')

    # --- MAP LOADING ---
    print(f"Loading map {MAP_FILE}...")
    try:
        Z_interp, xGrid, yGrid, cx, cy = load_map(f"./maps/{MAP_FILE}")
        print(f"Map loaded. X={cx:.1f}, Y={cy:.1f}")
    except Exception as e:
        print(f"Error loading map: {e}")
        return
    # ----------------------------------------

    # --- USER INTERFACE ---
    if gui_data is not None:
        N, off_x, off_y, play_area_size, mode = gui_data
        sv_x = cx + off_x
        sv_y = cy + off_y
    else:
        N, sv_x, sv_y, play_area_size, mode = get_user_inputs(cx, cy, config_file)
    # ----------------------------------------

    # --- VARIABLE INITIALIZATION ---
    if mode == 1:
        current_strategy = FreeExploration()
        print("-> Starting mode FREE EXPLORATION")
    else:
        current_strategy = FixedExploration()
        print("-> Starting mode FIXED EXPLORATION")
    
    robots = create_robots(N, sv_x, sv_y)
    x_lims = [sv_x - play_area_size/2, sv_x + play_area_size/2]
    y_lims = [sv_y - play_area_size/2, sv_y + play_area_size/2]
    exp_map = ExplorationMap(x_lims, y_lims, resolution=1)
    # ----------------------------------------

    # --- WINDOW SETUP ---
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8)) 
    fig.tight_layout(pad=3.0)
    manager = plt.get_current_fig_manager()
    manager.window.state('zoomed')
    simulation_state = {"active": True, "paused": False}
    setup_window_closing(fig, manager, simulation_state)
    show_map(fig, ax1, Z_interp, xGrid, yGrid, x_lims, y_lims)
    add_info_text(fig, N, sv_x - cx, sv_y - cy, play_area_size, mode)
    boton_stop = add_pause_button(fig, simulation_state)
    # ----------------------------------------

    assigned_relays = {r.name: "SV" for r in robots if not r.is_sv}
    graphics_actors = setup_simulation_graphics(
        ax2, robots, exp_map, Z_interp, xGrid, yGrid, x_lims, y_lims)

    # --- SIMULATION ---
    final_status = ("UNKNOWN", "Simulation finished.")
    for t in range(int(SIM_TIME / DT)):
        fig.canvas.flush_events()

        if not simulation_state["active"]:
            print("\n[!] Simulation canceled by user.")
            final_status = ("CANCELED", "Simulation canceled by user.") 
            break
        
        while simulation_state["paused"] and simulation_state["active"]:
            plt.pause(0.1) 

        # Prepare display
        percentage = exp_map.get_completion_percentage()
        sv = robots[0]
        active_relays = set(assigned_relays.values()) 
        
        graphics_actors["title"].set_text(f'Explored: {percentage:.1f}% | t={t*DT:.1f}s')        
        graphics_actors["layer"].set_data(exp_map.grid) 
        
        # Movements
        map_expanded = update_robots_movement(
            robots, current_strategy, exp_map, x_lims, y_lims, DT, EXPLORATION_RADIUS, active_relays
        )

        # Positions of the rovers
        for r in robots:
            graphics_actors["plots"][r.name].set_xdata([r.pos[0]])
            graphics_actors["plots"][r.name].set_ydata([r.pos[1]])
            graphics_actors["texts"][r.name].set_position((r.pos[0] + 1.0, r.pos[1] + 1.0))

        # Exploration finished?
        if current_strategy.check_end(percentage):
            draw_network_connections(ax2, robots, assigned_relays, graphics_actors["net_lines"])
            plt.pause(0.1) 
            mensaje_exito = f"Simulation ended successfully at t={t*DT:.1f}s.\nArea explored to {percentage:.1f}%."
            print(f"\n[!] {mensaje_exito}")
            final_status = ("SUCCESS", mensaje_exito)
            break

        # Map has grown?
        if map_expanded:
            updateLargeMap(ax1, x_lims, y_lims)
            graphics_actors["layer"].set_extent([x_lims[0], x_lims[1], y_lims[0], y_lims[1]])
            ax2.set_xlim([x_lims[0], x_lims[1]])
            ax2.set_ylim([y_lims[0], y_lims[1]])

        # Network logic
        someone_disconected, mensaje_error = process_network_turn(robots, sv, assigned_relays, UMBRAL, HOST)
        
        if someone_disconected:
            draw_network_connections(ax2, robots, assigned_relays, graphics_actors["net_lines"])
            plt.pause(0.1)
            mensaje_desc = f"Simulation ended at t={t*DT:.1f}s.\n{mensaje_error}"
            print(f"\n[!] {mensaje_desc}")
            final_status = ("DISCONNECTED", mensaje_desc)
            break
            
        draw_network_connections(ax2, robots, assigned_relays, graphics_actors["net_lines"])

    # Closing up
    print(f"[!] Exiting simulation...")
    for r in robots:
        r.stop()
        
    plt.close('all') 
    plt.ioff()
    return final_status

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulation of lunar rovers.")
    parser.add_argument("--config", type=str, help="Path to JSON configuration file.", default=None)
    args = parser.parse_args()

    main(args.config)