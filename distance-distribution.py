from re import split
from pyproj import Geod
import matplotlib.pyplot as plt
from numpy import median, percentile
from pandas import read_csv, value_counts
from scipy.stats import median_absolute_deviation as mad

def distance(x1, y1, x2, y2):
    """
    * Ellipsoidal distance between two points
    """
    # measure the forward azimuth, back azimuth and distance between two points
    azF, azB, distance = g.inv(x1, y1, x2, y2)

    # return the distance only
    return distance


# set which ellipsoid you would like to use
g = Geod(ellps='WGS84')

# read in survey dataset
mask_survey = read_csv("./data/mask-survey.csv")[["_Geo-Location_longitude", "_Geo-Location_latitude", "4.Sample ID", "Name of Informal Settlement"]].dropna()

# extract the sample ids using regex
mask_survey['survey-id'] = mask_survey.apply(lambda x: int(split("/", x["4.Sample ID"].replace("\\", "/"))[0]), axis = 1)

# just for testing / degugging dataset
# for k, v in mask_survey['survey-id'].value_counts().iteritems():
#     print(k,v)

# read in geopandas dataset
datasets = {
    'kibera': {
        'data': read_csv("./data/kibera.csv"),
        'name': 'Kibera, Nairobi'
        },
    'rodah': {
        'data': read_csv("./data/rhoda.csv"),
        'name': 'Rodah, Nakuru'
        },
    'kisii': {
        'data': read_csv("./data/kisii.csv"),
        'name': 'Daraja/Nubian, Kisii'
        }
}

# init a figure
fig, axes = plt.subplots(figsize=(15, 8), nrows=3, ncols=1)

# init counter for which plot to draw to
plot_n = 131


# for each settlement
print()
for s in ['kibera', 'rodah', 'kisii']:

    # get samples for this settlement
    samples = mask_survey[mask_survey["Name of Informal Settlement"] == datasets[s]['name']]

    # join to original sample locations
    samples = samples.merge(datasets[s]['data'], how='left', left_on='survey-id', right_on='id')

    # get distances from sample points to actual sample locations
    distances = samples[["longitude", "latitude", "_Geo-Location_longitude", "_Geo-Location_latitude"]].apply(lambda x: distance(x['longitude'], x['latitude'], x["_Geo-Location_longitude"], x["_Geo-Location_latitude"]), axis = 1).to_numpy()
    print(f"{s}: n:{len(distances)}, \tmedian:{median(distances):.2f}, \tmad:{mad(distances):.2f}, \tmin:{min(distances):.2f}, \tmax:{max(distances):.2f}")

    # plot histogram
    plt.subplot(plot_n)
    plt.hist(distances, bins=range(0, 2700, 100), align='left', color="#5bc0de")
    plt.axvline(median(distances), color='red', linestyle='dashed', linewidth=1.5)
    plt.axvline(median(distances) + mad(distances), color='red', linewidth=0.5)
    plt.axvline(median(distances) - mad(distances), color='red', linewidth=0.5)
    # plt.axvline(percentile(distances, 25), color='blue', linewidth=0.5)
    # plt.axvline(percentile(distances, 75), color='blue', linewidth=0.5)
    plt.xlabel('Distance')
    plt.ylabel('Frequency')
    plt.ylim([0, 180])
    plt.title(f'{s} (Median: {median(distances):.2f}, MAD: {mad(distances):.2f})')

    # increment counter for which plot to draw to
    plot_n += 1

    # output a csv file for mapping
    samples['distance'] = distances
    samples.to_csv(f"./out/{s}.csv", index=False, columns=['survey-id', "_Geo-Location_longitude", "_Geo-Location_latitude", 'distance'])

plt.savefig(f"./out/distances.png")
print()
