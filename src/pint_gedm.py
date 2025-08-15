from typing import Union
from pint.models import get_model, AstrometryEcliptic, AstrometryEquatorial
from pint.logging import setup as setup_log
import pygedm
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import astropy.units as u

setup_log(level="ERROR")

def parse_args(argv):
    parser = ArgumentParser(
        prog="pint-gedm",
        description="Evaluate electron density computations on a par file.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("parfile", help="Pulsar ephemeris file")
    parser.add_argument(
        "-m",
        choices=["ymw16", "ne2001"],
        default="ymw16",
        help="Electron density model",
    )

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    m = get_model(args.parfile, allow_T2=True, allow_tcb=True)

    astrometry: Union[AstrometryEcliptic, AstrometryEquatorial] = (
        m.components["AstrometryEcliptic"]
        if "AstrometryEcliptic" in m.components
        else m.components["AstrometryEquatorial"]
    )
    gal_coords = astrometry.coords_as_GAL()

    print(f"Pulsar: {m['PSR'].value}")
    print(f"Galactic coordinates (l, b): ({gal_coords.l}, {gal_coords.b})")

    if "DM" in m:
        dm = m["DM"].quantity
        dist = pygedm.dm_to_dist(gal_coords.l, gal_coords.b, dm.value, method=args.m)[0]
        px = (u.AU / dist).to("mas", equivalencies=u.dimensionless_angles())

        print("\nDM to Distance:")
        print(f"\tDM = {dm}")
        print(f"\tDistance = {dist}")
        print(f"\tParallax = {px}")

    if "PX" in m:
        px = m["PX"].quantity
        dist = (u.AU / px).to("pc", equivalencies=u.dimensionless_angles())
        dm = pygedm.dist_to_dm(gal_coords.l, gal_coords.b, dist, method=args.m)[0]

        print("\nParallax to DM:")
        print(f"\tParallax = {px}")
        print(f"\tDistance = {dist}")
        print(f"\tDM = {dm}")
