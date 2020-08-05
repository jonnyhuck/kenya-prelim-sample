"""
* Uses mann-whitney u to determine whether the demographic distribution of samples is
*   sufficiently similar to the defined quotas. Used this rather than chisquare as
*   some of the individual frequencies are <5.
*
* @author: jonnyhuck
"""

from numpy import zeros, array
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
from pandas import read_csv, DataFrame, IntervalIndex, cut, value_counts

''' EXPECTED VALUES '''

expected = {
    'Kibera, Nairobi': {
        'Male': [51, 30, 21, 8, 4, 1, 0],
        'Female': [55, 29, 16, 21, 2, 1, 0]
    },
    'Rodah, Nakuru': {
        'Male': [58, 32, 18, 7, 3, 1, 0],
        'Female': [60, 28, 13, 17, 2, 1, 0]
    },
    'Daraja/Nubian, Kisii': {
        'Male': [47, 25, 15, 11, 6, 3, 1],
        'Female': [55, 26, 15, 22, 7, 4, 1]
    },
}

''' OBSERVED VALUES '''

# read in dataset
mask_survey = read_csv("./data/mask-survey.csv")[["Respondent's Gender/Sex", "2.Age of  Respondent", "Name of Informal Settlement"]].dropna()

''' ANALYSIS '''

# initialise bins
bins = IntervalIndex.from_tuples([(18, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 80), (80, 90)])

# for each settlement
for s in ['Daraja/Nubian, Kisii', 'Rodah, Nakuru', 'Kibera, Nairobi']:

    # for each gender
    for g in ['Male', 'Female']:

        # get the current settlement & gender
        sample = mask_survey[(mask_survey["Name of Informal Settlement"] == s) & (mask_survey["Respondent's Gender/Sex"] == g)]

        # sort age data into bins
        observed = list(value_counts(cut(sample["2.Age of  Respondent"], bins), sort=False, ascending=True))

        # get two-sided mann-whitney U and p value
        stat, p = mannwhitneyu(observed, expected[s][g], alternative='two-sided')

        # output to console
        print()
        print(s, g)
        # print(observed)
        # print(expected[s][g])
        print(f"u={stat}, p={p}")
        print("----------")
        if (p < 0.05):
            print(f"Reject H0: The distributions do not match (p={p:.6f})")
        else:
            print(f"Cannot Reject H0: The difference between the distributions is not significant (p={p:.6f})")
        print()


        # init plot
        fig, axes = plt.subplots(figsize=(15, 8), nrows=1, ncols=3)

        # create bin labels
        labels = array([20, 30, 40, 50, 60, 70, 80])

        # observed plot
        plt.subplot(131)
        plt.bar(labels, observed, width=9, align='edge', color="#5bc0de")
        plt.xlabel('Age')
        plt.ylabel('Frequency')
        plt.xlim([10, 90])
        plt.ylim([0, 70])
        plt.title('Observed Values')

        # expected plot
        plt.subplot(132)
        plt.bar(labels, expected[s][g], width=9, align='edge', color="#f0ad4e")
        plt.xlabel('Age')
        plt.ylabel('Frequency')
        plt.xlim([10, 90])
        plt.ylim([0, 70])
        plt.title('Expected Values')

        # calculate difference (balance) for third plot
        difference = array(observed) - array(expected[s][g])

        # difference plot
        plt.subplot(133)
        mask1 = difference < 0
        mask2 = difference >= 1
        plt.bar(labels[mask1], difference[mask1], width=9, align='edge', color="#d9534f")
        plt.bar(labels[mask2], difference[mask2], width=9, align='edge', color="#0275d8")
        plt.xlabel('Age')
        plt.ylabel('Frequency')
        plt.xlim([10, 90])
        plt.ylim([-70, 70])
        plt.axhline(y=0, linewidth=0.5, color='k')
        plt.title('Difference')

        # output image
        plt.savefig(f'./out/{s.replace(",", "").replace("/", "").replace(" ", "_")}_{g}.png', dpi=300)
