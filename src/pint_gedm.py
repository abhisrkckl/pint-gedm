from typing import Union
from pint.models import get_model, AstrometryEcliptic, AstrometryEquatorial
import pygedm
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import astropy.units as u


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

    m = get_model(args.parfile)

    astrometry: Union[AstrometryEcliptic, AstrometryEquatorial] = (
        m.components["AstrometryEcliptic"]
        if "AstrometryEcliptic" in m.components
        else m.components["AstrometryEquatorial"]
    )
    gal_coords = astrometry.coords_as_GAL()

    print(f"Pulsar: {m['PSR'].value}")
    print(f"Galactic coordinates (l, b): ({gal_coords.l}, {gal_coords.b}) deg")

    if "DM" in m:
        dm = m["DM"].value
        dist = pygedm.dm_to_dist(gal_coords.l, gal_coords.b, dm, method=args.m)[0]
        px = (u.AU / dist).to("mas", equivalencies=u.dimensionless_angles())

        print("DM to distance:")
        print(f"\tDM = {dm} pc/cm^3")
        print(f"\tDistance = {dist.value} pc")
        print(f"\tParallax = {px.value} pc")

    if "PX" in m:
        px = m["PX"].value
        dist = (u.AU / px).to("pc", equivalencies=u.dimensionless_angles())
        dm = pygedm.dist_to_dm(gal_coords.l, gal_coords.b, dist, method=args.m)[0]

        print("DM to distance:")
        print(f"\tParallax = {px} pc/cm^3")
        print(f"\tDistance = {dist} pc")
        print(f"\tDM = {dm.value} pc")
