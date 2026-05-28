import numpy as np
from tkinter import messagebox
from matplotlib.widgets import Button

def show_map(fig, ax1, Z_interp, xGrid, yGrid, x_lims, y_lims):
    ax1.clear() 
    mapa = ax1.imshow(
                Z_interp,
                extent=[np.nanmin(xGrid), np.nanmax(xGrid), np.nanmin(yGrid), np.nanmax(yGrid)],
                origin='lower',
                cmap='viridis',
                zorder=1,
                aspect='auto'
            )
    
    ax1.set_title("Global Map")
    fig.colorbar(mapa, ax=ax1, label='Elevation', fraction=0.046, pad=0.04)
    
    ax1.plot([x_lims[0], x_lims[1], x_lims[1], x_lims[0], x_lims[0]],
             [y_lims[0], y_lims[0], y_lims[1], y_lims[1], y_lims[0]],
             color='red', linewidth=2, zorder=5)    
    ax1.set_xticks([])
    ax1.set_yticks([])

def updateLargeMap(ax1, x_lims, y_lims):
    for line in ax1.lines:
        line.remove()

    ax1.plot([x_lims[0], x_lims[1], x_lims[1], x_lims[0], x_lims[0]],
             [y_lims[0], y_lims[0], y_lims[1], y_lims[1], y_lims[0]],
             color='red', linewidth=2, zorder=5)

def draw_network_connections(ax, robots, assigned_relays, old_lines):
    for line in old_lines:
        try:
            line.remove()
        except ValueError:
            pass 
    old_lines.clear()

    robots_dict = {r.name: r for r in robots}
    
    for r_name, target_name in assigned_relays.items():
        r_obj = robots_dict[r_name]
        t_obj = robots_dict[target_name]
        
        # Draw lines
        style = '-' if target_name == "SV" else '--'
        color = 'gray' if target_name == "SV" else r_obj.color
        alpha = 0.5 if target_name == "SV" else 1.0
        
        r_x, r_y = r_obj.pos[0], r_obj.pos[1]
        t_x, t_y = t_obj.pos[0], t_obj.pos[1]
        
        linea, = ax.plot([r_x, t_x], [r_y, t_y], style, 
                         color=color, alpha=alpha, linewidth=1.5, zorder=5)
        old_lines.append(linea)
        

def setup_window_closing(fig, manager, simulation_state):
    def al_cerrar_ventana():
        respuesta = messagebox.askyesno("Warning", "The simulation will stop and you will lose all data. Do you want to exit?")
        if respuesta:
            simulation_state["active"] = False


    try:
        manager.window.protocol("WM_DELETE_WINDOW", al_cerrar_ventana)
    except AttributeError:
        def cierre_forzado(evento):
            simulation_state["activa"] = False
        fig.canvas.mpl_connect('close_event', cierre_forzado)


def add_info_text(fig, num_robots, sv_x, sv_y, area, modo):
    modo_texto = "Free" if modo == 1 else "Fixed"

    texto_info = (
        f"--- CONFIGURATION DATA ---\n"
        f"Rovers in swarm: {num_robots}\n"
        f"Position of SV: X={sv_x:.1f}, Y={sv_y:.1f}\n"
        f"Initial area: {area} m\n"
        f"Exploration mode: {modo_texto}"
    )

    fig.text(0.02, 0.95, texto_info, 
             fontsize=10, 
             fontweight='bold',
             verticalalignment='top',
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5'))


def add_pause_button(fig, simulation_state):
    ax_boton = fig.add_axes([0.85, 0.05, 0.1, 0.05]) 
    boton_pausa = Button(ax_boton, 'Stop', color='lightgray', hovercolor='white')

    # Event
    def alternar_pausa(evento):
        # Change state
        simulation_state["paused"] = not simulation_state["paused"]
        
        # Change state
        if simulation_state["paused"]:
            boton_pausa.label.set_text('Resume')
            boton_pausa.color = 'lightgreen'
        else:
            boton_pausa.label.set_text('Stop')
            boton_pausa.color = 'lightgray'
            
        fig.canvas.draw_idle()

    boton_pausa.on_clicked(alternar_pausa)
    return boton_pausa

def setup_simulation_graphics(ax2, robots, exp_map, Z_interp, xGrid, yGrid, x_lims, y_lims):
    """Initialize elements for simulation."""
    ax2.set_xlim([x_lims[0], x_lims[1]])
    ax2.set_ylim([y_lims[0], y_lims[1]])
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.pcolormesh(xGrid, yGrid, Z_interp, cmap='viridis', shading='auto', zorder=1)

    exploration_layer = ax2.imshow(
        exp_map.grid, 
        extent=[x_lims[0], x_lims[1], y_lims[0], y_lims[1]], 
        origin='lower', cmap='Blues', alpha=0.3, zorder=2,
        vmin=0, vmax=1, aspect='auto'
    )

    robot_plots = {}
    robot_texts = {}
    for r in robots:
        plot_obj, = ax2.plot(r.pos[0], r.pos[1], 's' if r.is_sv else 'o', 
                             markersize=10, markerfacecolor=r.color, 
                             markeredgecolor='k', zorder=10)
        text_obj = ax2.text(r.pos[0] + 1.0, r.pos[1] + 1.0, r.name, 
                            fontweight='bold', color='white', zorder=10)
        
        robot_plots[r.name] = plot_obj
        robot_texts[r.name] = text_obj

    title_text = ax2.set_title('Explored: 0.0% | t=0.0s')
    network_lines = []

    return {
        "layer": exploration_layer,
        "plots": robot_plots,
        "texts": robot_texts,
        "title": title_text,
        "net_lines": network_lines
    }