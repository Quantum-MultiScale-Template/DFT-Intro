import numpy as np
import matplotlib.pyplot as plt


class Vector2D:
    def __init__(self, length=None, angle_deg=None, components=None):
        if components is not None:
            self.components = np.array(components, dtype=float)
        else:
            angle_rad = np.deg2rad(angle_deg)
            self.components = np.array([
                length * np.cos(angle_rad),
                length * np.sin(angle_rad)
            ])

    @property
    def length(self):
        return np.linalg.norm(self.components)

    @property
    def angle_rad(self):
        angle = np.arctan2(self.components[1], self.components[0])
        if angle < 0:
            angle += 2 * np.pi
        return angle

    @property
    def angle_deg(self):
        return np.rad2deg(self.angle_rad)

    @property
    def end_point(self):
        return self.components


class OperatorDemo:
    def __init__(self):
        self.original_vector = None
        self.modified_vector = None
        self.operator_matrix = None

    @staticmethod
    def ask_float(message, default):
        value = input(f"{message} [{default}]: ")
        return float(value) if value.strip() else float(default)

    def get_user_input(self):
        length = self.ask_float("Length of Vector", 4)
        angle = self.ask_float("Angle (deg) of Vector", 45)

        self.original_vector = Vector2D(length=length, angle_deg=angle)

        m11 = self.ask_float("M11", 2)
        m12 = self.ask_float("M12", -1)
        m21 = self.ask_float("M21", 1)
        m22 = self.ask_float("M22", 3)

        self.operator_matrix = np.array([
            [m11, m12],
            [m21, m22]
        ])

    def apply_operator(self):
        modified_components = self.operator_matrix @ self.original_vector.components
        self.modified_vector = Vector2D(components=modified_components)

    @staticmethod
    def draw_vector(ax, vector, label, max_head_size=0.5):
        ax.quiver(
            0, 0,
            vector.components[0],
            vector.components[1],
            angles="xy",
            scale_units="xy",
            scale=1,
            color="k"
        )

        ax.text(
            vector.end_point[0],
            vector.end_point[1],
            label
        )

    def plot_before_operator(self):
        fig, ax = plt.subplots()

        plotlim = np.ceil(1.5 * self.original_vector.length)

        self.draw_vector(ax, self.original_vector, r"   $V_{orig}$")

        ax.text(
            0.2 * plotlim,
            0.9 * plotlim,
            f"V_orig length = {self.original_vector.length:.3g}"
        )

        ax.text(
            0.2 * plotlim,
            0.8 * plotlim,
            f"V_orig angle = {self.original_vector.angle_deg:.3g} deg"
        )

        ax.set_xlim(-plotlim, plotlim)
        ax.set_ylim(-plotlim, plotlim)
        ax.set_aspect("equal")
        ax.grid(True)
        ax.set_title("Vector Before Operator Applied")

        plt.pause(2)
        return fig, ax

    def plot_after_operator(self, fig, ax):
        ax.clear()

        bigger_vector = max(
            self.original_vector.length,
            self.modified_vector.length
        )

        plotlim = np.ceil(2 * bigger_vector)

        self.draw_vector(ax, self.original_vector, r"$V_{orig}$")
        self.draw_vector(ax, self.modified_vector, r"$V_{mod}$")

        ax.text(
            -0.8 * plotlim,
            0.9 * plotlim,
            f"V_orig length = {self.original_vector.length:.3g}"
        )

        ax.text(
            -0.8 * plotlim,
            0.8 * plotlim,
            f"V_orig angle = {self.original_vector.angle_deg:.3g} deg"
        )

        ax.text(
            0.2 * plotlim,
            0.9 * plotlim,
            f"V_mod length = {self.modified_vector.length:.3g}"
        )

        ax.text(
            0.2 * plotlim,
            0.8 * plotlim,
            f"V_mod angle = {self.modified_vector.angle_deg:.3g} deg"
        )

        length_change = (
            self.modified_vector.length - self.original_vector.length
        )

        angle_change = (
            self.modified_vector.angle_rad - self.original_vector.angle_rad
        )

        if abs(angle_change) <= 1e-15:
            angle_change = 0.0

        ax.text(
            -0.8 * plotlim,
            -0.7 * plotlim,
            "For this vector, applying this operator changes"
        )

        ax.text(
            -0.8 * plotlim,
            -0.8 * plotlim,
            f"length by {length_change:.3g} units and "
            f"angle by {np.rad2deg(angle_change):.3g} deg"
        )

        if angle_change == 0:
            ax.text(
                -0.8 * plotlim,
                -0.9 * plotlim,
                "This is an eigenvector of this operator"
            )

        ax.text(
            -0.95 * plotlim,
            0.5 * plotlim,
            "Operator Matrix"
        )

        matrix_text = (
            f"[{self.operator_matrix[0, 0]:.3g}  {self.operator_matrix[0, 1]:.3g}]\n"
            f"[{self.operator_matrix[1, 0]:.3g}  {self.operator_matrix[1, 1]:.3g}]"
        )

        ax.text(
            -0.8 * plotlim,
            0.3 * plotlim,
            matrix_text
        )

        ax.set_xlim(-plotlim, plotlim)
        ax.set_ylim(-plotlim, plotlim)
        ax.set_aspect("equal")
        ax.grid(True)
        ax.set_title("Vectors Before and After Operator Applied")

        fig.canvas.draw()

    def run(self):
        self.get_user_input()
        fig, ax = self.plot_before_operator()
        self.apply_operator()
        self.plot_after_operator(fig, ax)
        plt.show()


if __name__ == "__main__":
    demo = OperatorDemo()
    demo.run()
