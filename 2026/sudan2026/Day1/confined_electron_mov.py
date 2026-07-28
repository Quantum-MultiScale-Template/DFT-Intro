#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, RadioButtons, CheckButtons

# ============================================================
#  Particle in a 1D box: Re/Im, |Psi|^2 and complex-plane animation
# ============================================================

# ---- SI constants (used only if "Natural units" = OFF) ----
HBAR_SI = 1.054_571_817e-34  # J·s
M_ELECTRON = 9.109_383_7015e-31  # kg

# -------------------------
# Initial configuration
# -------------------------
INIT = {
    "use_natural_units": False,  # True: ħ=1, 2m=1, L=1
    "L": 1e-9,                   # m (SI only)
    "m": M_ELECTRON,             # kg (SI only)
    "Nx": 1200,
    "n_stationary": 3,           # n for stationary mode
    "mode": "Stationary",        # "Stationary" or "Superposition"
    "super_ns": (1, 2),          # n1, n2 for superposition
    "super_phase": 0.0,          # relative phase φ (rad) of the second coefficient
    "speed": 1.0,                # multiplies dt
    "x0_frac": 0.37,             # x0 = x0_frac * L
}

# -------------------------
# Physical/mathematical utilities
# -------------------------
def get_params(state):
    """Return (ħ, m, L) depending on whether natural or SI units are used."""
    if state["use_natural_units"]:
        # Natural units: ħ=1, 2m=1 => m=1/2, L=1
        hbar = 1.0
        m = 0.5
        L = 1.0
    else:
        hbar = HBAR_SI
        m = state["m"]
        L = state["L"]
    return hbar, m, L

def energy(n, hbar, m, L):
    return (n**2 * np.pi**2 * hbar**2) / (2.0 * m * L**2)

def psi_spatial(n, x, L):
    return np.sqrt(2.0 / L) * np.sin(n * np.pi * x / L)

def psi_stationary(n, x, t, hbar, m, L):
    En = energy(n, hbar, m, L)
    return psi_spatial(n, x, L) * np.exp(-1j * En * t / hbar)

def psi_superposition(n1, n2, phase2, x, t, hbar, m, L):
    # c1 = 1/sqrt(2), c2 = exp(i*phase2)/sqrt(2)
    c1 = 1.0 / np.sqrt(2.0)
    c2 = np.exp(1j * phase2) / np.sqrt(2.0)
    return c1 * psi_stationary(n1, x, t, hbar, m, L) + c2 * psi_stationary(n2, x, t, hbar, m, L)

def characteristic_period(state):
    """Reference period used to set a visual time scale."""
    hbar, m, L = get_params(state)
    if state["mode"] == "Stationary":
        n = int(state["n_stationary"])
        E = energy(n, hbar, m, L)
    else:
        n1, n2 = state["super_ns"]
        # Use the energy difference to see beats in |Psi|^2
        E = abs(energy(n2, hbar, m, L) - energy(n1, hbar, m, L))
        if E == 0:
            E = energy(n1, hbar, m, L)
    omega = E / hbar
    if omega == 0:
        return 1.0
    return 2.0 * np.pi / omega

# ============================================================
#  UI construction
# ============================================================
def main():
    state = dict(INIT)

    # Initial grid
    hbar, m, L = get_params(state)
    x = np.linspace(0.0, L, state["Nx"])
    x0 = state["x0_frac"] * L

    # Time
    Tref = characteristic_period(state)
    dt_base = (2.0 * Tref) / 240.0  # ~240 frames per 2Tref
    t = 0.0

    # --------- Figure with 3 panels + controls ---------
    fig = plt.figure(figsize=(12, 7))
    fig.suptitle("Particle in a 1D box: Re/Im, |Ψ|² and complex plane", fontsize=13)

    # Main axes (manual layout to leave space for controls)
    ax_wave = fig.add_axes([0.06, 0.36, 0.58, 0.56])   # Re/Im vs x
    ax_prob = fig.add_axes([0.06, 0.08, 0.58, 0.22])   # |Psi|^2 vs x
    ax_complex = fig.add_axes([0.70, 0.36, 0.28, 0.56])# complex plane
    ax_info = fig.add_axes([0.70, 0.08, 0.28, 0.22])   # text

    ax_info.axis("off")

    # Limits and styles
    Amax = np.sqrt(2.0 / L)
    ax_wave.set_xlim(0.0, L)
    ax_wave.set_ylim(-1.25 * Amax, 1.25 * Amax)
    ax_wave.set_xlabel("x")
    ax_wave.set_ylabel("Amplitude")
    ax_wave.grid(True)

    ax_prob.set_xlim(0.0, L)
    # Typical |psi|^2 ~ 2/L; add some margin
    ax_prob.set_ylim(0.0, 2.5 / L)
    ax_prob.set_xlabel("x")
    ax_prob.set_ylabel(r"$|\Psi(x,t)|^2$")
    ax_prob.grid(True)

    ax_complex.set_xlabel(r"Re[$\Psi(x_0,t)$]")
    ax_complex.set_ylabel(r"Im[$\Psi(x_0,t)$]")
    ax_complex.grid(True)

    # Initial curves
    line_re, = ax_wave.plot([], [], label="Re[Ψ(x,t)]")
    line_im, = ax_wave.plot([], [], label="Im[Ψ(x,t)]")
    ax_wave.legend(loc="upper right")

    line_prob, = ax_prob.plot([], [], label=r"$|\Psi(x,t)|^2$")
    ax_prob.legend(loc="upper right")

    # x0 marker
    vline_x0 = ax_wave.axvline(x0, linestyle="--")
    vline_x0_prob = ax_prob.axvline(x0, linestyle="--")

    # Complex plane: history trail + current point
    trail_len = 200
    trail = np.zeros(trail_len, dtype=complex)
    line_trail, = ax_complex.plot([], [], linewidth=1.2)
    point_now, = ax_complex.plot([], [], marker="o", markersize=6)

    # Informational text
    info_text = ax_info.text(0.02, 0.95, "", va="top", fontsize=10)

    # --------- Controls (widgets) ---------
    # Radio buttons: mode
    ax_radio = fig.add_axes([0.70, 0.01, 0.14, 0.06])
    radio_mode = RadioButtons(ax_radio, ("Stationary", "Superposition"), active=0)

    # Check button: natural units
    ax_check = fig.add_axes([0.86, 0.01, 0.12, 0.06])
    check_units = CheckButtons(ax_check, ["Natural units"], [state["use_natural_units"]])

    # Sliders
    ax_sn = fig.add_axes([0.70, 0.30, 0.28, 0.03])  # n (stationary)
    s_n = Slider(ax_sn, "n", 1, 10, valinit=state["n_stationary"], valstep=1)

    ax_sphi = fig.add_axes([0.70, 0.26, 0.28, 0.03])  # superposition phase
    s_phi = Slider(ax_sphi, "phase φ (rad)", -np.pi, np.pi, valinit=state["super_phase"])

    ax_speed = fig.add_axes([0.70, 0.22, 0.28, 0.03])
    s_speed = Slider(ax_speed, "speed", 0.1, 4.0, valinit=state["speed"])

    ax_x0 = fig.add_axes([0.70, 0.18, 0.28, 0.03])
    s_x0 = Slider(ax_x0, "x0/L", 0.0, 1.0, valinit=state["x0_frac"])

    # For superposition: n1 and n2 (two discrete sliders)
    ax_n1 = fig.add_axes([0.70, 0.14, 0.28, 0.03])
    s_n1 = Slider(ax_n1, "n1", 1, 10, valinit=state["super_ns"][0], valstep=1)

    ax_n2 = fig.add_axes([0.70, 0.10, 0.28, 0.03])
    s_n2 = Slider(ax_n2, "n2", 1, 10, valinit=state["super_ns"][1], valstep=1)

    def recompute_grid_and_limits():
        nonlocal x, L, Amax, x0, trail, dt_base, Tref

        hbar, m, L = get_params(state)
        x = np.linspace(0.0, L, state["Nx"])
        x0 = state["x0_frac"] * L

        # L-dependent limits
        Amax = np.sqrt(2.0 / L)
        ax_wave.set_xlim(0.0, L)
        ax_wave.set_ylim(-1.25 * Amax, 1.25 * Amax)

        ax_prob.set_xlim(0.0, L)
        ax_prob.set_ylim(0.0, 2.5 / L)

        vline_x0.set_xdata([x0, x0])
        vline_x0_prob.set_xdata([x0, x0])

        # Recompute time scale
        Tref = characteristic_period(state)
        dt_base = (2.0 * Tref) / 240.0

        # Reset trail
        trail = np.zeros(trail_len, dtype=complex)

    def current_psi(t_now):
        hbar, m, L = get_params(state)
        if state["mode"] == "Stationary":
            n = int(state["n_stationary"])
            return psi_stationary(n, x, t_now, hbar, m, L)
        else:
            n1, n2 = state["super_ns"]
            return psi_superposition(int(n1), int(n2), state["super_phase"], x, t_now, hbar, m, L)

    def update_info(t_now):
        hbar, m, L = get_params(state)
        if state["mode"] == "Stationary":
            n = int(state["n_stationary"])
            En = energy(n, hbar, m, L)
            omega = En / hbar
            txt = (
                f"Mode: Stationary (n={n})\n"
                f"t = {t_now:.3e}\n"
                f"ω = E/ħ = {omega:.3e}\n"
                f"L = {L:.3e} {'(natural)' if state['use_natural_units'] else 'm'}\n"
                f"x0/L = {state['x0_frac']:.2f}\n"
                f"Note: |Ψ|² does NOT change with time\n"
                f"(only the global phase rotates)."
            )
        else:
            n1, n2 = state["super_ns"]
            E1 = energy(int(n1), hbar, m, L)
            E2 = energy(int(n2), hbar, m, L)
            domega = abs(E2 - E1) / hbar
            txt = (
                f"Mode: Superposition (n1={int(n1)}, n2={int(n2)})\n"
                f"t = {t_now:.3e}\n"
                f"Δω = |E2−E1|/ħ = {domega:.3e}\n"
                f"φ (phase) = {state['super_phase']:.2f} rad\n"
                f"L = {L:.3e} {'(natural)' if state['use_natural_units'] else 'm'}\n"
                f"x0/L = {state['x0_frac']:.2f}\n"
                f"Note: here |Ψ|² CAN vary\n"
                f"(interference/beats)."
            )
        info_text.set_text(txt)

    # Control callbacks
    def on_mode(label):
        state["mode"] = label
        recompute_grid_and_limits()

    def on_units(_label):
        state["use_natural_units"] = not state["use_natural_units"]
        recompute_grid_and_limits()

    def on_n(val):
        state["n_stationary"] = int(val)

    def on_phi(val):
        state["super_phase"] = float(val)

    def on_speed(val):
        state["speed"] = float(val)

    def on_x0(val):
        state["x0_frac"] = float(val)
        recompute_grid_and_limits()

    def on_n1(val):
        n2 = int(state["super_ns"][1])
        state["super_ns"] = (int(val), n2)

    def on_n2(val):
        n1 = int(state["super_ns"][0])
        state["super_ns"] = (n1, int(val))

    radio_mode.on_clicked(on_mode)
    check_units.on_clicked(on_units)

    s_n.on_changed(on_n)
    s_phi.on_changed(on_phi)
    s_speed.on_changed(on_speed)
    s_x0.on_changed(on_x0)
    s_n1.on_changed(on_n1)
    s_n2.on_changed(on_n2)

    # Initialize with reasonable complex-plane limits
    def autoscale_complex():
        # Typical amplitude ~ sqrt(2/L)
        ax_complex.set_xlim(-1.3 * Amax, 1.3 * Amax)
        ax_complex.set_ylim(-1.3 * Amax, 1.3 * Amax)

    autoscale_complex()

    # Animation
    def init_anim():
        line_re.set_data([], [])
        line_im.set_data([], [])
        line_prob.set_data([], [])
        line_trail.set_data([], [])
        point_now.set_data([], [])
        update_info(0.0)
        return line_re, line_im, line_prob, line_trail, point_now, info_text

    def update(_frame):
        nonlocal t, trail

        dt = dt_base * state["speed"]
        t += dt

        Psi = current_psi(t)

        # Re/Im vs x
        line_re.set_data(x, Psi.real)
        line_im.set_data(x, Psi.imag)

        # Probability
        prob = np.abs(Psi)**2
        line_prob.set_data(x, prob)

        # Complex plane at x0
        # Choose the nearest index
        idx0 = int(round(state["x0_frac"] * (len(x) - 1)))
        z0 = Psi[idx0]

        trail[:-1] = trail[1:]
        trail[-1] = z0

        line_trail.set_data(trail.real, trail.imag)
        point_now.set_data([z0.real], [z0.imag])

        # Rescale the complex plane if L changed because of the units
        autoscale_complex()

        # Info
        update_info(t)

        return line_re, line_im, line_prob, line_trail, point_now, info_text

    ani = FuncAnimation(fig, update, init_func=init_anim, interval=25, blit=True)
    plt.show()

if __name__ == "__main__":
    main()
