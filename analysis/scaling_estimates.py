"""Order-of-magnitude bounds on how much drought hydraulics can warm the Solimões.

Two pathways for a well-mixed column, dT/dt = K (Te - T) / (rho cp d):
  (A) advection: slower flow means a longer exposure over a reach, N = K L W / (rho cp Q)
  (B) thermal inertia: shallower water tracks an equilibrium-temperature anomaly more closely

Numbers are illustrative; replace the inputs with reach values from the gauges.
See context/02_agu26_idea_feasibility.md.
"""
import numpy as np

RHO_CP = 4.18e6  # J m-3 K-1
SIGMA = 5.67e-8


def exchange_coefficient(wind, tw_k=303.0):
    """Linearised surface heat-exchange coefficient K (W m-2 K-1) near 30 C."""
    radiative = 4 * 0.97 * SIGMA * tw_k**3
    rho_a, lv, cp_a, c_bulk = 1.15, 2.43e6, 1005.0, 1.3e-3
    dqs_dt = 0.0016  # d(q_sat)/dT at 30 C, kg/kg/K
    return radiative + rho_a * lv * c_bulk * wind * dqs_dt + rho_a * cp_a * c_bulk * wind


def main():
    for u_a in (1.5, 3.0):
        print(f"wind {u_a} m/s -> K = {exchange_coefficient(u_a):.1f} W m-2 K-1")
    k = exchange_coefficient(2.5)

    print(f"\nThermal memory (K = {k:.0f})")
    for d, u in [(15, 1.0), (10, 0.7), (3, 0.3)]:
        tau = RHO_CP * d / k
        print(f"  depth {d:>2} m, u {u} m/s: relaxation {tau / 86400:5.1f} d, length {u * tau / 1e3:6.0f} km")

    print("\n(A) Advection over a 500 km reach")
    length = 5e5
    n_clim = k * length * 2500 / (RHO_CP * 5e4)  # W 2.5 km, Q 50,000 m3/s
    n_drought = k * length * 2100 / (RHO_CP * 3e4)  # W 2.1 km, Q 30,000 m3/s
    print(f"  N normal {n_clim:.2f}, drought {n_drought:.2f}")
    for gap in (1, 2, 4):
        print(f"  Te - Tin = {gap} C -> extra warming {gap * (np.exp(-n_clim) - np.exp(-n_drought)):.2f} C")

    print("\n(B) Damped response to an equilibrium-temperature anomaly")
    for period_days in (20, 60, 120):
        w = 2 * np.pi / (period_days * 86400)

        def ratio(d):
            return 1 / np.sqrt(1 + (w * RHO_CP * d / k) ** 2)

        for dte in (2, 3):
            print(f"  period {period_days:>3} d, Te +{dte} C: 15 m {dte * ratio(15):.2f}, 10 m {dte * ratio(10):.2f}, "
                  f"hydraulic share {dte * (ratio(10) - ratio(15)):.2f}, 2 m side channel {dte * ratio(2):.2f}")


if __name__ == "__main__":
    main()
