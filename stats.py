import pickle
import matplotlib.pyplot as plt
plt.switch_backend('Agg')


def crate_historgram_data(file_path: str, png_str: str) -> dict[float, int]:
    with open(file_path, "rb") as p:
        data = pickle.load(p)

    den_off = []
    den_max = float('-inf')
    den_min = float('inf')
    for game in data:
        strs = game['STRS']
        den_off.append(game['STRS'])
        if strs < den_min:
            den_min = strs
        elif strs > den_max:
            den_max = strs
    sqrt_bins = int(100 ** 0.5)
    difference = den_max - den_min
    bin_size = difference / sqrt_bins
    den_bins = {}
    value = den_min
    for _ in range(sqrt_bins):
        value = value + bin_size
        den_bins[value] = []
    for strs in den_off:
        for key in den_bins:
            if strs <= key:
                den_bins[key].append(strs)
                break
    histogram = {key: len(den_bins[key]) for key in den_bins}
    plt.bar(histogram.keys(), histogram.values(), width=bin_size)
    plt.xlabel('STRS Bins')
    plt.ylabel('Frequency')
    plt.title('Histogram of STRS')

    # Save the plot as an image file
    plt.savefig(png_str)
    return histogram


# den_home_off = "den_off_stats_home.pickle"
# den_away_off = "den_off_stats_away.pickle"
# den_home_png = "den_home_hist.png"
# den_away_png = "den_away_hist.png"
# crate_historgram_data(den_home_off, den_home_png)
# crate_historgram_data(den_away_off, den_away_png)

nop_away_off = "nop_off_stats_away.pickle"
nop_home_off = "nop_off_stats_away.pickle"
nop_away_png = "nop_away_hist.png"
nop_home_png = "nop_home_hist.png"
crate_historgram_data(nop_away_off, nop_away_png)
crate_historgram_data(nop_home_off, nop_home_png)


