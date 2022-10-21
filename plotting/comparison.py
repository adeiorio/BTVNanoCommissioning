import numpy as np
import argparse, sys, os, arrow, glob
from coffea.util import load
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import mplhep as hep
import hist
from hist.intervals import ratio_uncertainty

plt.style.use(hep.style.ROOT)
from BTVNanoCommissioning.utils.xs_scaler import getSumW, collate, scaleSumW

markers = [".", "o", "^", "s", "+", "x", "D", "*"]
parser = argparse.ArgumentParser(description="make comparison for different campaigns")
parser.add_argument(
    "-p",
    "--phase",
    required=True,
    choices=[
        "dilep_sf",
        "ttsemilep_sf",
        "ctag_Wc_sf",
        "ctag_DY_sf",
        "ctag_ttsemilep_sf",
        "ctag_ttdilep_sf",
    ],
    dest="phase",
    help="which phase space",
)
parser.add_argument(
    "-i",
    "--input",
    required=True,
    type=str,
    help="input coffea files (str), splitted different files with ','. Wildcard option * available as well.",
)
parser.add_argument("-r", "--ref", required=True, help="referance dataset")
parser.add_argument(
    "-c",
    "--compared",
    required=True,
    type=str,
    help="compared datasets, splitted by ,",
)
parser.add_argument(
    "--sepflav", default=False, type=bool, help="seperate flavour(b/c/light)"
)
parser.add_argument("--log", action="store_true", help="log on y axis")
parser.add_argument(
    "-v",
    "--variable",
    type=str,
    help="variables to plot, splitted by ,",
)
parser.add_argument("--ext", type=str, default="data", help="prefix name")
parser.add_argument("--com", default="13", type=str, help="sqrt(s) in TeV")
parser.add_argument(
    "--shortref",
    default="",
    type=str,
    help="short name for reference dataset for legend",
)
parser.add_argument(
    "--shortcomp",
    default="",
    type=str,
    help="short names for compared datasets for legend, split by ','",
)

args = parser.parse_args()
output = {}
if len(args.input.split(",")) > 1:
    output = {i: load(i) for i in args.input.split(",")}
elif "*" in args.input:
    files = glob.glob(args.input)
    output = {i: load(i) for i in files}
else:
    output = load(args.input)
mergemap = {}
time = arrow.now().format("YY_MM_DD")
if not os.path.isdir(f"plot/BTV/{args.phase}_{args.ext}_{time}/"):
    os.makedirs(f"plot/BTV/{args.phase}_{args.ext}_{time}/")
if not any(".coffea" in o for o in output.keys()):
    mergemap[args.ref] = [m for m in output.keys() if args.ref == m]
    for c in args.compared.split(","):
        mergemap[c] = [m for m in output.keys() if c == m]
else:
    reflist = []
    comparelist = []
    for f in output.keys():
        reflist.extend([m for m in output[f].keys() if args.ref == m])
        for c in args.compared.split(","):
            comparelist.extend([m for m in output[f].keys() if c == m])
    mergemap[args.ref] = reflist
    mergemap[c] = comparelist
collated = collate(output, mergemap)
### style settings
if "Run" in args.ref:
    hist_type = "errorbar"
    label = "Preliminary"
else:
    hist_type = "step"
    label = "Simulation Preliminary"

if "ttdilep" in args.phase:
    input_txt = "dilepton ttbar"
    nj = 2
elif "ttsemilep" in args.phase:
    input_txt = "semileptonic ttbar"
    nj = 4
else:
    if "Wc" in args.phase:
        input_txt = "W+c"
    elif "DY" in args.phase:
        input_txt = "DY+jets"
    nj = 1
print(mergemap)

if args.shortref == "":
    args.shortref = args.ref

if args.shortcomp == "":
    args.shortcomp = args.compared

for discr in args.variable.split(","):
    if args.sepflav:  # split into 3 panels for different flavor
        fig, (ax, rax, rax2, rax3) = plt.subplots(
            4,
            1,
            figsize=(8, 8),
            gridspec_kw={"height_ratios": (3, 1, 1, 1)},
            sharex=True,
        )
        fig.subplots_adjust(hspace=0.07)
        ax.set_xlabel(None)
        ax.set_xticklabels(ax.get_xticklabels(), fontsize=0)
        hep.cms.label(
            label,
            com=args.com,
            data=True,
            loc=0,
            ax=ax,
        )
        laxis = {"flav": 0}
        puaxis = {"flav": 1}
        caxis = {"flav": 2}
        baxis = {"flav": 3}

        if "syst" in collated[args.ref][discr].axes.name:
            laxis["syst"] = "noSF"
            puaxis["syst"] = "noSF"
            caxis["syst"] = "noSF"
            baxis["syst"] = "noSF"

        hep.histplot(
            collated[args.ref][discr][laxis] + collated[args.ref][discr][puaxis],
            label=args.shortref + "-l",
            color="b",
            histtype=hist_type,
            yerr=True,
            ax=ax,
        )
        hep.histplot(
            collated[args.ref][discr][caxis],
            label=args.shortref + "-c",
            color="g",
            histtype=hist_type,
            yerr=True,
            ax=ax,
        )
        hep.histplot(
            collated[args.ref][discr][baxis],
            label=args.shortref + "-b",
            yerr=True,
            color="r",
            histtype=hist_type,
            ax=ax,
        )

        index = 0
        for c, s in zip(args.compared.split(","), args.shortcomp.split(",")):
            hep.histplot(
                collated[c][discr][laxis] + collated[c][discr][puaxis],
                label=s + "-l",
                color="b",
                marker=markers[index + 1],
                histtype="errorbar",
                yerr=True,
                ax=ax,
            )
            hep.histplot(
                collated[c][discr][caxis],
                label=s + "-c",
                color="g",
                marker=markers[index + 1],
                histtype="errorbar",
                yerr=True,
                ax=ax,
            )
            hep.histplot(
                collated[c][discr][baxis],
                label=s + "-b",
                yerr=True,
                color="r",
                marker=markers[index + 1],
                histtype="errorbar",
                ax=ax,
            )
        index += 1
        ax.legend(
            ncol=3,
            loc="upper right",
        )
        index = 0
        for c in args.compared.split(","):

            rax.errorbar(
                x=collated[c][discr][laxis].axes[0].centers,
                y=(
                    collated[c][discr][laxis].values()
                    + collated[c][discr][puaxis].values()
                )
                / (
                    collated[args.ref][discr][laxis].values()
                    + collated[args.ref][discr][puaxis].values()
                ),
                yerr=ratio_uncertainty(
                    (
                        collated[c][discr][laxis].values()
                        + collated[c][discr][puaxis].values()
                    ),
                    collated[args.ref][discr][laxis].values()
                    + collated[args.ref][discr][puaxis].values(),
                ),
                color="b",
                linestyle="none",
                marker=markers[index + 1],
            )
            rax2.errorbar(
                x=collated[c][discr][caxis].axes[0].centers,
                y=collated[c][discr][caxis].values()
                / collated[args.ref][discr][caxis].values(),
                yerr=ratio_uncertainty(
                    collated[c][discr][caxis].values(),
                    collated[args.ref][discr][caxis].values(),
                ),
                color="g",
                linestyle="none",
                marker=markers[index + 1],
            )
            rax3.errorbar(
                x=collated[c][discr][baxis].axes[0].centers,
                y=collated[c][discr][baxis].values()
                / collated[args.ref][discr][baxis].values(),
                yerr=ratio_uncertainty(
                    collated[c][discr][baxis].values(),
                    collated[args.ref][discr][baxis].values(),
                ),
                color="r",
                linestyle="none",
                marker=markers[index + 1],
            )

        discrs = discr
        ax.set_xlabel("A.U.")
        rax3.set_xlabel(discrs)
        rax.set_ylabel("udsg-jets")
        rax2.set_ylabel("c-jets")
        rax3.set_ylabel("b-jets")
        rax.set_ylim(0.5, 1.5)
        rax2.set_ylim(0.5, 1.5)
        rax3.set_ylim(0.5, 1.5)
        rax3.set_xlabel(discr)
        ax.legend()
        at = AnchoredText(
            "",
            # + "inclusive pT, $\eta$"
            loc=2,
            prop=dict(size=15),
            frameon=False,
        )
        ax.add_artist(at)
        hep.mpl_magic(ax=ax)
        if args.log:
            ax.set_yscale("log")
        fig.savefig(
            f"plot/BTV/{args.phase}_{args.ext}_{time}/compare_{args.phase}_inclusive{discrs}.png"
        )
        fig.savefig(
            f"plot/BTV/{args.phase}_{args.ext}_{time}/compare_{args.phase}_inclusive{discrs}.pdf"
        )

    else:
        fig, ((ax), (rax)) = plt.subplots(
            2, 1, figsize=(8, 8), gridspec_kw={"height_ratios": (3, 1)}, sharex=True
        )
        fig.subplots_adjust(hspace=0.07)
        hep.cms.label(
            label,
            com=args.com,
            data=True,
            loc=0,
            ax=ax,
        )
        ax.set_xlabel(None)
        ax.set_xticklabels(ax.get_xticklabels(), fontsize=0)
        allaxis = {}
        if "flav" in collated[args.ref][discr].axes.name:
            allaxis["flav"] = sum
        if "syst" in collated[args.ref][discr].axes.name:
            allaxis["syst"] = sum
        hep.histplot(
            collated[args.ref][discr][allaxis],
            label=args.shortref,
            histtype=hist_type,
            yerr=True,
            ax=ax,
        )
        for c, s in zip(args.compared.split(","), args.shortcomp.split(",")):
            hep.histplot(
                collated[c][discr][allaxis],
                label=s,
                histtype=hist_type,
                yerr=True,
                ax=ax,
            )

        for c in args.compared.split(","):
            rax.errorbar(
                x=collated[c][discr][allaxis].axes[0].centers,
                y=collated[c][discr][allaxis].values()
                / collated[args.ref][discr][allaxis].values(),
                yerr=ratio_uncertainty(
                    collated[c][discr][allaxis].values(),
                    collated[args.ref][discr][allaxis].values(),
                ),
                color="k",
                linestyle="none",
                marker="o",
                elinewidth=1,
            )
        rax.set_xlabel(discr)
        ax.set_xlabel(None)
        ax.set_ylabel("Events")
        rax.set_ylabel("Other/Ref")
        ax.legend()
        rax.set_ylim(0.0, 2.0)

        at = AnchoredText(
            "",
            loc=2,
            frameon=False,
        )
        ax.add_artist(at)
        hep.mpl_magic(ax=ax)
        if args.log:
            ax.set_yscale("log")
        fig.savefig(
            f"plot/BTV/{args.phase}_{args.ext}_{time}/compare_{args.phase}_lin_inclusive{discr}.pdf"
        )
        fig.savefig(
            f"plot/BTV/{args.phase}_{args.ext}_{time}/compare_{args.phase}_lin_inclusive{discr}.png"
        )
