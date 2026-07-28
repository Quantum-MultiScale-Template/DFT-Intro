#!/usr/bin/env python3
"""
Interactive animation for a one-dimensional tight-binding model.

The model is a chain of atoms with one s-like orbital per atom and nearest-neighbor
hopping. The script visualizes the time evolution of either:

1. A single Bloch eigenstate.
2. A coherent superposition of two Bloch eigenstates.

It displays:
- The real and imaginary parts of the wavefunction on each atomic site.
- The probability density |psi_n(t)|^2.
- The modulus |psi_n(t)|.
- The unwrapped phase arg[psi_n(t)].
- The trajectory of psi at one selected atomic site in the complex plane.

Natural tight-binding units are used by default:
    hbar = 1, a = 1
so energies are measured in units of the hopping parameter.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, RadioButtons


# ============================================================
#  Initial configuration
# ============================================================
INIT = {
    "N": 60,                    # Number of atoms/sites used for visualization
    "epsilon": 0.0,             # On-site energy
    "hopping": -1.0,            # Nearest-neighbor hopping t
    "a": 1.0,                   # Lattice constant
    "hbar": 1.0,                # Reduced Planck constant in natural units
    "mode": "Bloch state",      # "Bloch state" or "Superposition"
    "k1_frac": 0.25,            # k1 = k1_frac * pi / a
    "k2_frac": 0.65,            # k2 = k2_frac * pi / a
    "super_phase": 0.0,         # Relative phase phi of the second coefficient
    "speed": 1.0,               # Multiplies the time step
    "site0_frac": 0.37,         # Selected site: n0 = site0_frac * (N - 1)
}


# ============================================================
#  Tight-binding physics
# ============================================================
def dispersion(k, epsilon, hopping, a):
    """Return the 1D nearest-neighbor tight-binding energy E(k)."""
    return epsilon + 2.0 * hopping * np.cos(k * a)


def atomic_positions(N, a):
    """Return atomic indices n and positions R_n = n a."""
    n = np.arange(N)
    Rn = n * a
    return n, Rn


def bloch_spatial_part(k, N, a):
    """
    Return the normalized spatial part of a Bloch wave on a finite chain.

    psi_k(n) = exp(i k R_n) / sqrt(N)
    """
    _, Rn = atomic_positions(N, a)
    return np.exp(1j * k * Rn) / np.sqrt(N)


def bloch_state(k, time, state):
    """Return the full time-dependent Bloch eigenstate."""
    N = int(state["N"])
    epsilon = state["epsilon"]
    hopping = state["hopping"]
    a = state["a"]
    hbar = state["hbar"]

    E = dispersion(k, epsilon, hopping, a)
    psi0 = bloch_spatial_part(k, N, a)
    return psi0 * np.exp(-1j * E * time / hbar)


def superposition_state(k1, k2, phase2, time, state):
    """Return an equal-weight superposition of two Bloch eigenstates."""
    c1 = 1.0 / np.sqrt(2.0)
    c2 = np.exp(1j * phase2) / np.sqrt(2.0)
    return c1 * bloch_state(k1, time, state) + c2 * bloch_state(k2, time, state)


def k_from_fraction(k_frac, a):
    """Convert the slider variable k_frac into k = k_frac * pi / a."""
    return k_frac * np.pi / a


def characteristic_period(state):
    """Return a reference period used to choose a visually useful time step."""
    epsilon = state["epsilon"]
    hopping = state["hopping"]
    a = state["a"]
    hbar = state["hbar"]

    k1 = k_from_fraction(state["k1_frac"], a)
    k2 = k_from_fraction(state["k2_frac"], a)

    if state["mode"] == "Bloch state":
        E = abs(dispersion(k1, epsilon, hopping, a))
    else:
        E1 = dispersion(k1, epsilon, hopping, a)
        E2 = dispersion(k2, epsilon, hopping, a)
        E = abs(E2 - E1)

    omega = E / hbar
    if omega < 1e-12:
        return 1.0
    return 2.0 * np.pi / omega


# ============================================================
#  User interface and animation
# ============================================================
def main():
    state = dict(INIT)

    # Initial grid and time scale
    n, Rn = atomic_positions(int(state["N"]), state["a"])
    Tref = characteristic_period(state)
    dt_base = (2.0 * Tref) / 240.0
    time = 0.0

    # Figure layout
    fig = plt.figure(figsize=(13, 8))
    fig.suptitle(
        "1D tight-binding model: Bloch wave, probability, modulus, phase and complex plane",
        fontsize=13,
    )

    # Main axes
    ax_wave = fig.add_axes([0.06, 0.60, 0.58, 0.32])      # Re/Im versus atomic position
    ax_prob = fig.add_axes([0.06, 0.39, 0.58, 0.15])      # |psi|^2 versus atomic position
    ax_mod = fig.add_axes([0.06, 0.22, 0.27, 0.12])       # |psi| versus atomic position
    ax_phase = fig.add_axes([0.37, 0.22, 0.27, 0.12])     # phase versus atomic position
    ax_complex = fig.add_axes([0.70, 0.42, 0.27, 0.48])   # complex plane at selected site
    ax_info = fig.add_axes([0.70, 0.20, 0.27, 0.16])      # text information
    ax_info.axis("off")

    # Initial vertical scale
    amp_max = np.sqrt(2.0 / state["N"])

    ax_wave.set_xlim(Rn[0], Rn[-1])
    ax_wave.set_ylim(-1.35 * amp_max, 1.35 * amp_max)
    ax_wave.set_xlabel(r"Atomic position $R_n = n a$")
    ax_wave.set_ylabel(r"Wavefunction amplitude")
    ax_wave.grid(True)

    ax_prob.set_xlim(Rn[0], Rn[-1])
    ax_prob.set_ylim(0.0, 2.5 / state["N"])
    ax_prob.set_xlabel(r"Atomic position $R_n = n a$")
    ax_prob.set_ylabel(r"$|\psi_n(t)|^2$")
    ax_prob.grid(True)

    ax_mod.set_xlim(Rn[0], Rn[-1])
    ax_mod.set_ylim(0.0, 1.35 * amp_max)
    ax_mod.set_xlabel(r"$R_n$")
    ax_mod.set_ylabel(r"$|\psi_n(t)|$")
    ax_mod.grid(True)

    ax_phase.set_xlim(Rn[0], Rn[-1])
    ax_phase.set_xlabel(r"$R_n$")
    ax_phase.set_ylabel(r"unwrapped phase")
    ax_phase.grid(True)

    ax_complex.set_xlabel(r"Re[$\psi_{n_0}(t)$]")
    ax_complex.set_ylabel(r"Im[$\psi_{n_0}(t)$]")
    ax_complex.grid(True)
    ax_complex.set_aspect("equal", adjustable="box")

    # Curves
    line_re, = ax_wave.plot([], [], "o-", markersize=3, label=r"Re[$\psi_n(t)$]")
    line_im, = ax_wave.plot([], [], "s-", markersize=3, label=r"Im[$\psi_n(t)$]")
    ax_wave.legend(loc="upper right")

    line_prob, = ax_prob.plot([], [], "o-", markersize=3, label=r"$|\psi_n(t)|^2$")
    ax_prob.legend(loc="upper right")

    line_mod, = ax_mod.plot([], [], "o-", markersize=3)
    line_phase, = ax_phase.plot([], [], "o-", markersize=3)

    # Selected site marker
    site0 = int(round(state["site0_frac"] * (state["N"] - 1)))
    R0 = Rn[site0]
    vline_site0 = ax_wave.axvline(R0, linestyle="--")
    vline_site0_prob = ax_prob.axvline(R0, linestyle="--")
    vline_site0_mod = ax_mod.axvline(R0, linestyle="--")
    vline_site0_phase = ax_phase.axvline(R0, linestyle="--")

    # Complex-plane trajectory
    trail_len = 220
    trail = np.zeros(trail_len, dtype=complex)
    line_trail, = ax_complex.plot([], [], linewidth=1.2)
    point_now, = ax_complex.plot([], [], marker="o", markersize=6)

    # Information text
    info_text = ax_info.text(0.02, 0.98, "", va="top", fontsize=9.5)

    # -------------------------
    # Widgets
    # -------------------------
    ax_radio = fig.add_axes([0.70, 0.08, 0.13, 0.08])
    radio_mode = RadioButtons(ax_radio, ("Bloch state", "Superposition"), active=0)

    ax_N = fig.add_axes([0.06, 0.14, 0.26, 0.025])
    s_N = Slider(ax_N, "N sites", 10, 160, valinit=state["N"], valstep=1)

    ax_k1 = fig.add_axes([0.06, 0.10, 0.26, 0.025])
    s_k1 = Slider(ax_k1, r"$k_1 a / \pi$", -1.0, 1.0, valinit=state["k1_frac"])

    ax_k2 = fig.add_axes([0.06, 0.06, 0.26, 0.025])
    s_k2 = Slider(ax_k2, r"$k_2 a / \pi$", -1.0, 1.0, valinit=state["k2_frac"])

    ax_phi = fig.add_axes([0.06, 0.02, 0.26, 0.025])
    s_phi = Slider(ax_phi, r"relative phase $\phi$", -np.pi, np.pi, valinit=state["super_phase"])

    ax_eps = fig.add_axes([0.39, 0.14, 0.25, 0.025])
    s_eps = Slider(ax_eps, r"on-site $\epsilon$", -3.0, 3.0, valinit=state["epsilon"])

    ax_t = fig.add_axes([0.39, 0.10, 0.25, 0.025])
    s_t = Slider(ax_t, r"hopping $t$", -3.0, 3.0, valinit=state["hopping"])

    ax_speed = fig.add_axes([0.39, 0.06, 0.25, 0.025])
    s_speed = Slider(ax_speed, "speed", 0.05, 5.0, valinit=state["speed"])

    ax_site0 = fig.add_axes([0.39, 0.02, 0.25, 0.025])
    s_site0 = Slider(ax_site0, r"selected site $n_0/(N-1)$", 0.0, 1.0, valinit=state["site0_frac"])

    def current_wavefunction(t_now):
        a = state["a"]
        k1 = k_from_fraction(state["k1_frac"], a)
        k2 = k_from_fraction(state["k2_frac"], a)

        if state["mode"] == "Bloch state":
            return bloch_state(k1, t_now, state)
        return superposition_state(k1, k2, state["super_phase"], t_now, state)

    def autoscale_complex():
        scale = 1.35 * np.sqrt(2.0 / state["N"])
        if scale < 1e-12:
            scale = 1.0
        ax_complex.set_xlim(-scale, scale)
        ax_complex.set_ylim(-scale, scale)

    def update_grid_and_limits(reset_trail=True):
        nonlocal n, Rn, Tref, dt_base, trail

        n, Rn = atomic_positions(int(state["N"]), state["a"])
        amp_max_local = np.sqrt(2.0 / state["N"])

        ax_wave.set_xlim(Rn[0], Rn[-1])
        ax_wave.set_ylim(-1.35 * amp_max_local, 1.35 * amp_max_local)

        ax_prob.set_xlim(Rn[0], Rn[-1])
        ax_prob.set_ylim(0.0, 2.5 / state["N"])

        ax_mod.set_xlim(Rn[0], Rn[-1])
        ax_mod.set_ylim(0.0, 1.35 * amp_max_local)

        ax_phase.set_xlim(Rn[0], Rn[-1])

        site = int(round(state["site0_frac"] * (state["N"] - 1)))
        R_selected = Rn[site]
        vline_site0.set_xdata([R_selected, R_selected])
        vline_site0_prob.set_xdata([R_selected, R_selected])
        vline_site0_mod.set_xdata([R_selected, R_selected])
        vline_site0_phase.set_xdata([R_selected, R_selected])

        Tref = characteristic_period(state)
        dt_base = (2.0 * Tref) / 240.0

        autoscale_complex()

        if reset_trail:
            trail = np.zeros(trail_len, dtype=complex)

    def update_info(t_now):
        a = state["a"]
        epsilon = state["epsilon"]
        hopping = state["hopping"]
        hbar = state["hbar"]
        k1 = k_from_fraction(state["k1_frac"], a)
        k2 = k_from_fraction(state["k2_frac"], a)
        E1 = dispersion(k1, epsilon, hopping, a)
        E2 = dispersion(k2, epsilon, hopping, a)
        site = int(round(state["site0_frac"] * (state["N"] - 1)))

        if state["mode"] == "Bloch state":
            text = (
                f"Mode: Bloch eigenstate\n"
                f"N = {int(state['N'])}, selected site n0 = {site}\n"
                f"k a / pi = {state['k1_frac']:.3f}\n"
                f"E(k) = {E1:.4f}\n"
                f"omega = E/hbar = {E1 / hbar:.4f}\n"
                f"time = {t_now:.4f}\n"
                f"Note: |psi|^2 is constant in time\n"
                f"for a single Bloch state."
            )
        else:
            text = (
                f"Mode: two-state superposition\n"
                f"N = {int(state['N'])}, selected site n0 = {site}\n"
                f"k1 a / pi = {state['k1_frac']:.3f}\n"
                f"k2 a / pi = {state['k2_frac']:.3f}\n"
                f"E1 = {E1:.4f}, E2 = {E2:.4f}\n"
                f"Delta omega = {(E2 - E1) / hbar:.4f}\n"
                f"relative phase = {state['super_phase']:.3f} rad\n"
                f"time = {t_now:.4f}"
            )
        info_text.set_text(text)

    # -------------------------
    # Widget callbacks
    # -------------------------
    def on_mode(label):
        state["mode"] = label
        update_grid_and_limits(reset_trail=True)

    def on_N(value):
        state["N"] = int(value)
        update_grid_and_limits(reset_trail=True)

    def on_k1(value):
        state["k1_frac"] = float(value)
        update_grid_and_limits(reset_trail=True)

    def on_k2(value):
        state["k2_frac"] = float(value)
        update_grid_and_limits(reset_trail=True)

    def on_phi(value):
        state["super_phase"] = float(value)
        update_grid_and_limits(reset_trail=True)

    def on_epsilon(value):
        state["epsilon"] = float(value)
        update_grid_and_limits(reset_trail=True)

    def on_hopping(value):
        state["hopping"] = float(value)
        update_grid_and_limits(reset_trail=True)

    def on_speed(value):
        state["speed"] = float(value)

    def on_site0(value):
        state["site0_frac"] = float(value)
        update_grid_and_limits(reset_trail=True)

    radio_mode.on_clicked(on_mode)
    s_N.on_changed(on_N)
    s_k1.on_changed(on_k1)
    s_k2.on_changed(on_k2)
    s_phi.on_changed(on_phi)
    s_eps.on_changed(on_epsilon)
    s_t.on_changed(on_hopping)
    s_speed.on_changed(on_speed)
    s_site0.on_changed(on_site0)

    autoscale_complex()

    # -------------------------
    # Animation
    # -------------------------
    def init_anim():
        line_re.set_data([], [])
        line_im.set_data([], [])
        line_prob.set_data([], [])
        line_mod.set_data([], [])
        line_phase.set_data([], [])
        line_trail.set_data([], [])
        point_now.set_data([], [])
        update_info(0.0)
        return (
            line_re,
            line_im,
            line_prob,
            line_mod,
            line_phase,
            line_trail,
            point_now,
            info_text,
        )

    def update(_frame):
        nonlocal time, trail

        time += dt_base * state["speed"]
        psi = current_wavefunction(time)

        # Real and imaginary parts
        line_re.set_data(Rn, psi.real)
        line_im.set_data(Rn, psi.imag)

        # Probability density
        probability = np.abs(psi) ** 2
        line_prob.set_data(Rn, probability)

        # Modulus
        modulus = np.abs(psi)
        line_mod.set_data(Rn, modulus)

        # Phase. Unwrapping avoids artificial jumps by 2*pi.
        phase = np.unwrap(np.angle(psi))
        line_phase.set_data(Rn, phase)
        p_min = np.min(phase)
        p_max = np.max(phase)
        if abs(p_max - p_min) < 1e-12:
            ax_phase.set_ylim(p_min - np.pi, p_max + np.pi)
        else:
            margin = 0.12 * (p_max - p_min)
            ax_phase.set_ylim(p_min - margin, p_max + margin)

        # Complex plane at the selected atomic site
        site = int(round(state["site0_frac"] * (state["N"] - 1)))
        z0 = psi[site]
        trail[:-1] = trail[1:]
        trail[-1] = z0
        line_trail.set_data(trail.real, trail.imag)
        point_now.set_data([z0.real], [z0.imag])

        update_info(time)

        return (
            line_re,
            line_im,
            line_prob,
            line_mod,
            line_phase,
            line_trail,
            point_now,
            info_text,
        )

    # blit=False is more robust when axes limits are updated by sliders.
    _animation = FuncAnimation(
        fig,
        update,
        init_func=init_anim,
        interval=25,
        blit=False,
    )

    plt.show()


if __name__ == "__main__":
    main()
